"""A Windows-compatible evaluator for the local pilot.

EvalPlus' official evaluator depends on the Unix-only ``resource`` module. This module
keeps the important isolation property (candidate code runs in a killable child process),
adds a conservative AST/import gate, and mirrors the HumanEval+ output comparison rules.
Confirmatory results must still be rerun with the official evaluator on Linux.
"""

from __future__ import annotations

import ast
import builtins
import copy
import multiprocessing
from dataclasses import dataclass
from typing import Any, Sequence


ALLOWED_IMPORTS = frozenset(
    {
        "bisect",
        "collections",
        "decimal",
        "fractions",
        "functools",
        "heapq",
        "itertools",
        "math",
        "operator",
        "re",
        "statistics",
        "string",
        "typing",
    }
)
BLOCKED_CALLS = frozenset(
    {
        "breakpoint",
        "compile",
        "eval",
        "exec",
        "globals",
        "help",
        "input",
        "locals",
        "open",
        "vars",
        "__import__",
    }
)


@dataclass(frozen=True)
class EvaluationResult:
    status: str
    details: tuple[bool, ...]
    outcomes: tuple[Any, ...]
    reason: str | None = None


def audit_code(code: str) -> str | None:
    """Return a rejection reason, or ``None`` for code admitted to the worker."""

    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return f"syntax:{exc.msg}"
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            modules = (
                [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""]
            )
            if any(module.split(".", 1)[0] not in ALLOWED_IMPORTS for module in modules):
                return "unsafe_import"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in BLOCKED_CALLS:
                return f"unsafe_call:{node.func.id}"
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            return "dunder_attribute"
        if isinstance(node, ast.Name) and node.id in {"os", "sys", "subprocess", "socket"}:
            return f"unsafe_name:{node.id}"
    return None


def _safe_import(
    name: str,
    globals: dict[str, Any] | None = None,
    locals: dict[str, Any] | None = None,
    fromlist: Sequence[str] = (),
    level: int = 0,
) -> Any:
    if level != 0 or name.split(".", 1)[0] not in ALLOWED_IMPORTS:
        raise ImportError(f"import blocked: {name}")
    return builtins.__import__(name, globals, locals, fromlist, level)


def _safe_builtins() -> dict[str, Any]:
    names = {
        "ArithmeticError",
        "AssertionError",
        "Exception",
        "IndexError",
        "KeyError",
        "RuntimeError",
        "StopIteration",
        "TypeError",
        "ValueError",
        "ZeroDivisionError",
        "abs",
        "all",
        "any",
        "bin",
        "bool",
        "bytearray",
        "bytes",
        "callable",
        "chr",
        "classmethod",
        "complex",
        "dict",
        "divmod",
        "enumerate",
        "filter",
        "float",
        "frozenset",
        "hash",
        "hex",
        "int",
        "isinstance",
        "issubclass",
        "iter",
        "len",
        "list",
        "map",
        "max",
        "memoryview",
        "min",
        "next",
        "object",
        "oct",
        "ord",
        "pow",
        "property",
        "range",
        "repr",
        "reversed",
        "round",
        "set",
        "slice",
        "sorted",
        "staticmethod",
        "str",
        "sum",
        "super",
        "tuple",
        "type",
        "zip",
    }
    values = {name: getattr(builtins, name) for name in names}
    values["__build_class__"] = builtins.__build_class__
    values["__import__"] = _safe_import
    return values


def _equivalent(output: Any, expected: Any, atol: float) -> bool:
    import numpy as np

    try:
        if output == expected:
            return True
    except (TypeError, ValueError):
        pass
    effective_atol = atol
    if effective_atol == 0 and _contains_float(expected):
        effective_atol = 1e-6
    if effective_atol:
        try:
            if type(output) is not type(expected):
                return False
            if isinstance(expected, (list, tuple)) and len(output) != len(expected):
                return False
            return bool(np.allclose(output, expected, rtol=1e-7, atol=effective_atol))
        except (TypeError, ValueError):
            return False
    return False


def _contains_float(value: Any) -> bool:
    if isinstance(value, float):
        return True
    if isinstance(value, (list, tuple)):
        return any(_contains_float(item) for item in value)
    return False


def _worker(
    queue: Any,
    solution: str,
    entry_point: str,
    inputs: Sequence[Any],
    expected: Sequence[Any] | None,
    atol: float,
) -> None:
    namespace: dict[str, Any] = {
        "__builtins__": _safe_builtins(),
        "__name__": "__candidate__",
    }
    details: list[bool] = []
    outcomes: list[Any] = []
    try:
        exec(compile(solution, "<candidate>", "exec"), namespace)
        function = namespace[entry_point]
        for index, arguments in enumerate(inputs):
            try:
                output = function(*copy.deepcopy(arguments))
                outcomes.append(("return", repr(output)))
                details.append(
                    True if expected is None else _equivalent(output, expected[index], atol)
                )
            except BaseException as exc:
                outcomes.append(("exception", type(exc).__name__))
                details.append(False)
        status = "pass" if all(details) else "fail"
        queue.put((status, tuple(details), tuple(outcomes), None))
    except BaseException as exc:
        queue.put(("fail", tuple(details), tuple(outcomes), type(exc).__name__))


def check_solution(
    *,
    solution: str,
    entry_point: str,
    inputs: Sequence[Any],
    expected: Sequence[Any] | None,
    atol: float = 0.0,
    timeout_seconds: float = 10.0,
) -> EvaluationResult:
    """Execute a candidate in a spawned process and kill it on task-level timeout."""

    rejection = audit_code(solution)
    if rejection:
        return EvaluationResult("unsafe", (), (), rejection)
    context = multiprocessing.get_context("spawn")
    queue = context.Queue(maxsize=1)
    process = context.Process(
        target=_worker,
        args=(queue, solution, entry_point, inputs, expected, atol),
    )
    process.start()
    process.join(timeout_seconds)
    if process.is_alive():
        process.terminate()
        process.join(1.0)
        if process.is_alive():
            process.kill()
        return EvaluationResult("timeout", (), (), "task_timeout")
    if queue.empty():
        return EvaluationResult("fail", (), (), f"worker_exit:{process.exitcode}")
    status, details, outcomes, reason = queue.get()
    return EvaluationResult(status, details, outcomes, reason)

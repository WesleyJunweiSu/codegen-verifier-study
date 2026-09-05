"""Local generation backend with auditable per-sample metadata."""

from __future__ import annotations

import ast
import hashlib
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SYSTEM_PROMPT = """You are completing a Python programming benchmark.
Return one correct implementation. Output only executable Python code: no Markdown,
no explanation, and no tests. Preserve the requested function name and signature."""


@dataclass(frozen=True)
class GenerationRecord:
    task_id: str
    sample_index: int
    generation_kind: str
    seed: int
    model_id: str
    prompt_sha256: str
    raw_output: str
    code: str
    code_parses: bool
    input_tokens: int
    output_tokens: int
    mean_token_entropy: float
    wall_seconds: float
    peak_vram_bytes: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_prompt(function_prompt: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Complete this function:\n\n{function_prompt}",
        },
    ]


def prompt_hash(messages: list[dict[str, str]]) -> str:
    canonical = "\n".join(f"{m['role']}\0{m['content']}" for m in messages)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


_FENCE = re.compile(r"```(?:python)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)


def extract_code(raw_output: str) -> str:
    """Extract code while retaining enough context to compile a full function."""

    fenced = _FENCE.search(raw_output)
    code = fenced.group(1) if fenced else raw_output
    code = code.strip()
    for marker in ("<|im_end|>", "<|endoftext|>"):
        code = code.split(marker, 1)[0].rstrip()
    return code


def parses_as_python(code: str) -> bool:
    try:
        ast.parse(code)
    except (SyntaxError, ValueError):
        return False
    return True


def compose_solution(function_prompt: str, code: str) -> str:
    """Restore imports from the benchmark prompt around a full model-written function."""

    if re.search(r"^\s*(?:async\s+)?def\s+", code, flags=re.MULTILINE):
        definition = re.search(
            r"^(?:async\s+)?def\s+", function_prompt, flags=re.MULTILINE
        )
        prelude = function_prompt[: definition.start()] if definition else ""
        return prelude + code
    # Completion-style fall-back for backends that return only an indented body.
    return function_prompt + code


class LocalCausalLM:
    """Thin Transformers wrapper used by the reproducible experiment scripts."""

    def __init__(self, model_path: str | Path, model_id: str) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.model_id = model_id
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            str(model_path),
            dtype=torch.bfloat16,
            device_map="cuda",
            local_files_only=True,
            low_cpu_mem_usage=True,
        )
        self.model.eval()

    def _render(self, messages: list[dict[str, str]]) -> str:
        try:
            return self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
        except TypeError:
            return self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

    def generate(
        self,
        *,
        task_id: str,
        function_prompt: str,
        sample_index: int,
        seed: int,
        max_new_tokens: int = 768,
        temperature: float = 0.7,
        top_p: float = 0.8,
    ) -> GenerationRecord:
        torch = self.torch
        messages = build_prompt(function_prompt)
        return self._generate_messages(
            task_id=task_id,
            messages=messages,
            sample_index=sample_index,
            seed=seed,
            generation_kind="initial",
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        )

    def generate_contrastive_branch(
        self,
        *,
        task_id: str,
        function_prompt: str,
        candidate_a: str,
        candidate_b: str,
        sample_index: int,
        seed: int,
        max_new_tokens: int = 768,
        temperature: float = 0.95,
        top_p: float = 0.95,
    ) -> GenerationRecord:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Review two proposed implementations against the specification below. "
                    "Reason privately about boundary cases, hidden assumptions, and off-by-one "
                    "errors. Return a corrected implementation only. When uncertainty remains, "
                    "prefer an algorithmically distinct solution rather than copying either "
                    "proposal.\n\nSPECIFICATION:\n"
                    f"{function_prompt}\n\nPROPOSAL A:\n{candidate_a}\n\n"
                    f"PROPOSAL B:\n{candidate_b}"
                ),
            },
        ]
        return self._generate_messages(
            task_id=task_id,
            messages=messages,
            sample_index=sample_index,
            seed=seed,
            generation_kind="contrastive_branch",
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        )

    def _generate_messages(
        self,
        *,
        task_id: str,
        messages: list[dict[str, str]],
        sample_index: int,
        seed: int,
        generation_kind: str,
        max_new_tokens: int,
        temperature: float,
        top_p: float,
    ) -> GenerationRecord:
        torch = self.torch
        rendered = self._render(messages)
        inputs = self.tokenizer(rendered, return_tensors="pt").to("cuda")
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.cuda.reset_peak_memory_stats()
        started = time.perf_counter()
        with torch.inference_mode():
            result = self.model.generate(
                **inputs,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                max_new_tokens=max_new_tokens,
                return_dict_in_generate=True,
                output_scores=True,
                output_logits=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - started
        generated = result.sequences[0, inputs.input_ids.shape[1] :]
        raw_output = self.tokenizer.decode(generated, skip_special_tokens=True)

        # ``scores`` are post-processor values and contain -inf after top-p filtering.
        # Raw logits preserve the model distribution needed by the entropy baseline.
        entropy_logits = getattr(result, "logits", None) or result.scores
        entropies: list[float] = []
        for logits in entropy_logits:
            logits = logits[0].float()
            log_probabilities = torch.log_softmax(logits, dim=-1)
            entropy = -torch.sum(torch.exp(log_probabilities) * log_probabilities)
            entropies.append(float(entropy.cpu()))
        mean_entropy = sum(entropies) / len(entropies) if entropies else 0.0
        code = extract_code(raw_output)
        return GenerationRecord(
            task_id=task_id,
            sample_index=sample_index,
            generation_kind=generation_kind,
            seed=seed,
            model_id=self.model_id,
            prompt_sha256=prompt_hash(messages),
            raw_output=raw_output,
            code=code,
            code_parses=parses_as_python(code),
            input_tokens=int(inputs.input_ids.shape[1]),
            output_tokens=int(generated.shape[0]),
            mean_token_entropy=mean_entropy,
            wall_seconds=elapsed,
            peak_vram_bytes=int(torch.cuda.max_memory_allocated()),
        )

"""Candidate/test execution helpers; called only by the isolated Linux evaluator."""
from __future__ import annotations

import hashlib
import json
import textwrap
from pathlib import Path

from evalplus.eval import untrusted_check
from verifier_study.selection import select_candidates
from verifier_study.test_quality import public_assertions


def check_assertion(solution: str, assertion: str) -> str:
    # EvalPlus supplies process isolation, a timeout and reliability guards; Docker is the security boundary.
    name="__verifier_assert_6dc382"
    code=solution+"\ndef "+name+"():\n"+textwrap.indent(assertion,"    ")+"\n    return True\n"
    status,_=untrusted_check("humaneval",code,[[]],name,[True],0,[0.001],fast_check=True,min_time_limit=0.25)
    return status


def write_rows(path: Path, rows: list[dict]):
    path.write_text("".join(json.dumps(row)+"\n" for row in rows))


def build_matrix(generations: list[dict], tests_path: Path, output: Path):
    visible={row["task_id"]:row for row in map(json.loads,Path("/app/mbpp-prompts.jsonl").read_text().splitlines())}
    generated={row["task_id"]:row for row in map(json.loads,tests_path.read_text().splitlines())}
    assert set(generated)=={row["task_id"] for row in generations},"Incomplete test generation"
    matrix=[];candidates=[]
    for candidate in generations:
        task_id=candidate["task_id"]
        candidates.append({"task_id":task_id,"sample_index":candidate["sample_index"],
                           "code_sha256":hashlib.sha256(candidate["code"].encode()).hexdigest()})
        tests=[{"source":"generated",**test} for test in generated[task_id]["tests"]]
        tests.extend({"source":"public","test_index":i,"assertion":assertion,"keep":True,"reasons":[]}
                     for i,assertion in enumerate(public_assertions(visible[task_id]["prompt"])))
        for test in tests:
            matrix.append({"task_id":task_id,"sample_index":candidate["sample_index"],"source":test["source"],
                           "test_index":test["test_index"],"keep":test["keep"],
                           "status":check_assertion(candidate["code"],test["assertion"])})
        print(f"Matrix {task_id} sample {candidate['sample_index']} complete",flush=True)
    write_rows(output/"candidate-test-matrix.jsonl",matrix)
    decisions=select_candidates(candidates,matrix)
    plan_path=tests_path.parent/"repair-plan.json"
    if plan_path.exists():
        from verifier_study.repair import select_repair
        decisions=select_repair(json.loads(plan_path.read_text()),matrix)
    write_rows(output/"decisions.jsonl",decisions)
    return generated


def reference_diagnostics(problems: dict, generated: dict, output: Path):
    rows=[]
    for task_id,record in generated.items():
        task=problems[task_id]
        solution=task["prompt"]+task["canonical_solution"]
        for test in record["tests"]:
            rows.append({"task_id":task_id,"test_index":test["test_index"],"keep":test["keep"],
                         "reference_status":check_assertion(solution,test["assertion"])})
    write_rows(output/"reference-test-diagnostics.jsonl",rows)

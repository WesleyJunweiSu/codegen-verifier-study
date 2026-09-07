"""Analyze saved decisions and scorer labels; never execute generated code."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import random
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verifier_study.io import read_jsonl,write_json


def wilson(k,n):
    if n==0: return None
    z=1.95996398454;p=k/n;d=1+z*z/n
    center=(p+z*z/(2*n))/d
    radius=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [center-radius,center+radius]


def paired_interval(deltas):
    rng=random.Random(20260905)
    values=sorted(sum(rng.choices(deltas,k=len(deltas)))/len(deltas) for _ in range(10000))
    return [values[249],values[9749]]


def historical():
    run=ROOT/"runs/historical-holdout"
    labels=read_jsonl(run/"windows-labels.jsonl")
    linux=read_jsonl(run/"linux/evaluation.jsonl")
    indexed={row["task_id"]:row for row in linux}
    assert len(indexed)==len(linux)==len(labels)==134
    assert set(indexed)=={row["task_id"] for row in labels}
    mismatch=[{"task_id":row["task_id"],"split":row["split"],"windows_pass":row["pass"],
               "linux_pass":indexed[row["task_id"]]["pass"],"base_status":indexed[row["task_id"]]["base_status"],
               "plus_status":indexed[row["task_id"]]["plus_status"]} for row in labels if row["pass"]!=indexed[row["task_id"]]["pass"]]
    summary={"comparison":"same saved code, historical Windows labels versus official EvalPlus primitives in isolated Linux",
             "samples":len(labels),"mismatches":mismatch,"splits":{}}
    for split in sorted({row["split"] for row in labels}):
        subset=[row for row in labels if row["split"]==split]
        accepted=[row for row in subset if row["accepted"]]
        summary["splits"][split]={"n":len(subset),"windows_passed":sum(row["pass"] for row in subset),
             "linux_passed":sum(indexed[row["task_id"]]["pass"] for row in subset),
             "historically_accepted":len(accepted),"linux_passed_among_historically_accepted":sum(indexed[row["task_id"]]["pass"] for row in accepted)}
    write_json(run/"comparison.json",summary)
    print(json.dumps(summary,indent=2))


def pilot(name):
    run=ROOT/"runs"/name
    candidates=read_jsonl(run/"generations.jsonl")
    tests=read_jsonl(run/"generated-tests.jsonl")
    labels=read_jsonl(run/"linux/evaluation.jsonl")
    decisions=read_jsonl(run/"linux/decisions.jsonl")
    matrix=read_jsonl(run/"linux/candidate-test-matrix.jsonl")
    reference=read_jsonl(run/"linux/reference-test-diagnostics.jsonl")
    indexed={(row["task_id"],row["sample_index"]):row for row in labels}
    assert len(indexed)==len(labels)==len(candidates)
    for row in candidates:
        assert indexed[row["task_id"],row["sample_index"]]["code_sha256"]==hashlib.sha256(row["code"].encode()).hexdigest()
    task_ids=sorted({row["task_id"] for row in candidates});n=len(task_ids)
    task_rows=[]
    for task_id in task_ids:
        pool=sorted([row for row in candidates if row["task_id"]==task_id],key=lambda row:row["sample_index"])
        truth=[indexed[task_id,row["sample_index"]]["pass"] for row in pool]
        test_record=next(row for row in tests if row["task_id"]==task_id)
        row={"task_id":task_id,"candidate_count":len(pool),"unique_code":len({x["code"] for x in pool}),
             "correct_candidates":sum(truth),"first_correct":truth[0],"oracle_correct":any(truth),
             "uniform_random_expected_correct":sum(truth)/len(truth),"parsed_tests":len(test_record["tests"])}
        for decision in [d for d in decisions if d["task_id"]==task_id]:
            method=decision["method"]
            row[method+"_selected"]=decision["sample_index"]
            row[method+"_correct"]=bool(decision["accepted"] and indexed[task_id,decision["sample_index"]]["pass"])
        task_rows.append(row)
    summary={"phase":"development pilot; not confirmatory","tasks":n,"candidates":len(candidates),"methods":{},
        "oracle_tasks":sum(row["oracle_correct"] for row in task_rows),
        "all_identical_candidate_tasks":sum(row["unique_code"]==1 for row in task_rows),
        "tasks_with_mixed_correctness":sum(0<row["correct_candidates"]<row["candidate_count"] for row in task_rows),
        "uniform_random_expected_correct":sum(row["uniform_random_expected_correct"] for row in task_rows),
        "generated_assertions":sum(len(row["tests"]) for row in tests),
        "tasks_without_parsed_tests":sum(not row["tests"] for row in tests),
        "kept_assertions":sum(test["keep"] for row in tests for test in row["tests"]),
        "reference_rejected_assertions":sum(row["reference_status"]!="pass" for row in reference),
        "kept_reference_rejected_assertions":sum(row["keep"] and row["reference_status"]!="pass" for row in reference),
        "executed_candidate_test_pairs":len(matrix),
        "candidate_output_tokens":sum(row["output_tokens"] for row in candidates),
        "test_output_tokens":sum(row["output_tokens"] for row in tests),
        "candidate_generation_seconds":sum(row["wall_seconds"] for row in candidates),
        "test_generation_seconds":sum(row["wall_seconds"] for row in tests),
        "peak_vram_bytes":max(row["peak_vram_bytes"] for row in candidates+tests),
        "filter_reasons":dict(collections.Counter(reason for row in tests for test in row["tests"] for reason in test["reasons"]))}
    test_manifest=json.loads((run/"test-manifest.json").read_text())
    candidate_reused=test_manifest.get("candidate_generation_reused","parent_run" in test_manifest)
    test_reused=test_manifest.get("test_generation_reused","parent_run" in test_manifest)
    summary["reuses_generation_from"]=test_manifest.get("parent_run") if candidate_reused else None
    summary["reuses_tests_from"]=test_manifest.get("parent_run") if test_reused else None
    summary["incremental_model_output_tokens"]=(0 if candidate_reused else summary["candidate_output_tokens"])+(0 if test_reused else summary["test_output_tokens"])
    for method in sorted({row["method"] for row in decisions}):
        correct=sum(row[method+"_correct"] for row in task_rows)
        accepted=sum(row[method+"_selected"] is not None for row in task_rows)
        deltas=[int(row[method+"_correct"])-int(row["first_correct"]) for row in task_rows]
        summary["methods"][method]={"correct_returned":correct,"returned":accepted,"tasks":n,"coverage":accepted/n,
            "correct_return_rate":correct/n,"selective_accuracy":correct/accepted if accepted else None,
            "correct_return_wilson95":wilson(correct,n),"paired_difference_vs_first":sum(deltas)/n,
            "paired_task_bootstrap95":paired_interval(deltas),
            "rescues_vs_first":sum(d>0 for d in deltas),"regressions_vs_first":sum(d<0 for d in deltas)}
    write_json(run/"summary.json",summary)
    write_json(run/"task-results.json",task_rows)
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("run",choices=["historical-holdout","mbpp-pilot-20260905","mbpp-parser-ablation-20260905","mbpp-temperature-20260906"])
    args=parser.parse_args()
    historical() if args.run=="historical-holdout" else pilot(args.run)

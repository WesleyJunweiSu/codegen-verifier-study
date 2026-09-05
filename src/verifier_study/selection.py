"""Label-blind, deterministic selectors. This module has no reference-data input."""
from __future__ import annotations


def select_candidates(candidates: list[dict], matrix: list[dict]) -> list[dict]:
    tasks=sorted({row["task_id"] for row in candidates})
    decisions=[]
    for task_id in tasks:
        pool=sorted([row for row in candidates if row["task_id"]==task_id],key=lambda row:row["sample_index"])
        evidence=[row for row in matrix if row["task_id"]==task_id]
        for method in ("first","public_tests","raw_tests","filtered_tests","filtered_abstain"):
            source="public" if method=="public_tests" else "generated"
            selected_tests=[row for row in evidence if row["source"]==source and
                            (method not in ("filtered_tests","filtered_abstain") or row["keep"])]
            scores={row["sample_index"]:sum(test["status"]=="pass" for test in selected_tests
                      if test["sample_index"]==row["sample_index"]) for row in pool}
            chosen=pool[0] if method=="first" else max(pool,key=lambda row:scores[row["sample_index"]])
            index=chosen["sample_index"]
            ntests=sum(row["sample_index"]==index for row in selected_tests)
            # Identical code is one alternative; duplicate samples are not independent evidence.
            others=[scores[row["sample_index"]] for row in pool if row["code_sha256"]!=chosen["code_sha256"]]
            margin=scores[index]-max(others) if others else None
            accepted=method!="filtered_abstain" or (ntests>0 and scores[index]==ntests and margin is not None and margin>=1)
            decisions.append({"task_id":task_id,"method":method,"sample_index":index if accepted else None,
                              "best_sample_index":index,"accepted":accepted,"score":scores[index],"test_count":ntests,
                              "margin_against_distinct_code":margin,"tie_break":"smallest sample_index",
                              "rule_status":"fixed development heuristic; not calibrated" if method=="filtered_abstain" else "baseline"})
    return decisions

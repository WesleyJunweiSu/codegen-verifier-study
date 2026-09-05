"""Summarize controlled diagnostic evidence without executing any saved code."""
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verifier_study.io import read_jsonl,write_json

run=ROOT/"runs/legacy-diagnostics-20260905"
rows=read_jsonl(run/"linux/diagnostics.jsonl")
metadata=json.loads((run/"linux/diagnostic-metadata.json").read_text(encoding="utf-8"))
assert len(rows)==metadata["rows"]==29
assert hashlib.sha256((ROOT/"src/verifier_study/legacy_windows_eval.py").read_bytes()).hexdigest()==metadata["legacy_source_sha256"]
assert hashlib.sha256((ROOT/"runs/historical-holdout/generations.jsonl").read_bytes()).hexdigest()==metadata["generations_sha256"]
indexed={}
for row in rows:
    key=(row["task_id"],row["condition"])
    assert key not in indexed
    indexed[key]=row
assert len({row['solution_sha256'] for row in rows if row['task_id']=='HumanEval/139'})==1
historical={row["task_id"]:row for row in read_jsonl(ROOT/"runs/historical-holdout/windows-labels.jsonl")}
summaries=[]
for task_id in metadata["task_ids"]:
    subset={condition:row for (task,condition),row in indexed.items() if task==task_id}
    assert len({row["solution_sha256"] for row in subset.values()})==1
    original=subset["original"];drained=subset["drain_first"];omitted=subset["drain_first_omit_repr"]
    if original["status"]=="timeout" and drained["status"]=="pass":
        mechanism="queue_join_order_reproduced_on_linux"
    elif original["status"]==drained["status"]=="fail" and omitted["status"]=="pass" and subset.get("drain_first_unlimited_repr",{}).get("status")=="pass":
        mechanism="integer_repr_limit_reproduced_on_linux"
    elif original["status"]=="unsafe":
        mechanism="legacy_gate_reproduced"
    elif historical[task_id]["status"]=="timeout" and original["status"]=="pass":
        mechanism="historical_timeout_not_reproduced_on_linux"
    else: mechanism="unresolved"
    summaries.append({"task_id":task_id,"historical_windows_status":historical[task_id]["status"],
        "original_legacy_linux_status":original["status"],"drain_first_status":drained["status"],
        "omit_repr_status":omitted["status"],"mechanism":mechanism,
        "queue_payload_bytes_with_repr":drained.get("queue_payload_bytes"),
        "queue_payload_bytes_without_repr":omitted.get("queue_payload_bytes"),
        "drain_first_seconds":drained["wall_seconds"],"reason":original.get("reason")})
summary={"historical_cases":7,"fixture_cases":2,"condition_rows":len(rows),"model_calls":0,
         "wall_seconds":metadata["wall_seconds"],"cases":summaries,
         "scope":"Mechanisms tested on Linux with the original Windows evaluator source and unchanged candidates. Two historical timeouts remain unreproduced.",
         "reproduced_queue_cases":sum(row["mechanism"]=="queue_join_order_reproduced_on_linux" for row in summaries),
         "reproduced_repr_cases":sum(row["mechanism"]=="integer_repr_limit_reproduced_on_linux" for row in summaries),
         "reproduced_gate_cases":sum(row["mechanism"]=="legacy_gate_reproduced" for row in summaries),
         "unreproduced_historical_timeout_cases":sum(row["mechanism"]=="historical_timeout_not_reproduced_on_linux" for row in summaries)}
write_json(run/"summary.json",summary)
print(json.dumps(summary,indent=2))

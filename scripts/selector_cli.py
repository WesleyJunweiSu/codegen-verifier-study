"""Inspect a saved decision and its execution evidence. Does not run candidate code."""
import argparse
import json
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--run",default="mbpp-pilot-20260905")
parser.add_argument("--task",required=True)
parser.add_argument("--method",default="public_tests")
args=parser.parse_args()
all_runs=Path(__file__).resolve().parents[1]/"runs"
root=all_runs/args.run
def rows(name): return [json.loads(line) for line in (root/name).read_text(encoding="utf-8").splitlines() if line]
decision_path="decisions.jsonl" if (root/"decisions.jsonl").exists() else "linux/decisions.jsonl"
decisions=[row for row in rows(decision_path) if row["task_id"]==args.task and row["method"]==args.method]
if len(decisions)!=1: raise SystemExit("No unique saved decision for that task and method")
decision=decisions[0]
print(json.dumps({"decision":decision,"scope":"Saved execution evidence; not a correctness guarantee"},indent=2))
if decision["accepted"]:
    generation_root=root
    if not (root/"generations.jsonl").exists():
        metadata_path=root/"manifest.json" if (root/"manifest.json").exists() else root/"linux/metadata.json"
        metadata=json.loads(metadata_path.read_text(encoding="utf-8"))
        generation_root=all_runs/metadata["parent_run"]
    candidates=[json.loads(line) for line in (generation_root/"generations.jsonl").read_text(encoding="utf-8").splitlines()]
    record=next(row for row in candidates if row["task_id"]==args.task and row["sample_index"]==decision["sample_index"])
    print("\nSelected code:\n"+record["code"])
else:
    print("\nNo candidate returned: the fixed pilot rule found insufficient discriminating evidence.")

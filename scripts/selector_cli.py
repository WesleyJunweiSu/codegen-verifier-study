"""Inspect a saved decision and its execution evidence. Does not run candidate code."""
import argparse
import json
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--run",default="mbpp-pilot-20260905")
parser.add_argument("--task",required=True)
parser.add_argument("--method",default="public_tests")
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]/"runs"/args.run
def rows(name): return [json.loads(line) for line in (root/name).read_text(encoding="utf-8").splitlines() if line]
decisions=[row for row in rows("linux/decisions.jsonl") if row["task_id"]==args.task and row["method"]==args.method]
if len(decisions)!=1: raise SystemExit("No unique saved decision for that task and method")
decision=decisions[0]
print(json.dumps({"decision":decision,"scope":"Saved execution evidence; not a correctness guarantee"},indent=2))
if decision["accepted"]:
    record=next(row for row in rows("generations.jsonl") if row["task_id"]==args.task and row["sample_index"]==decision["sample_index"])
    print("\nSelected code:\n"+record["code"])
else:
    print("\nNo candidate returned: the fixed pilot rule found insufficient discriminating evidence.")

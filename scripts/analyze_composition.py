"""Score previously persisted development-composition decisions with existing hidden labels."""
import json
import argparse
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verifier_study.io import read_jsonl,write_json,sha256
from analyze_results import wilson,paired_interval

parser=argparse.ArgumentParser()
parser.add_argument("--run",default="mbpp-public-consensus-20260906")
args=parser.parse_args()
run=ROOT/"runs"/args.run
manifest=json.loads((run/"manifest.json").read_text(encoding="utf-8"))
assert sha256(run/"decisions.jsonl")==manifest["decisions_sha256"]
parent=ROOT/"runs"/manifest["parent_run"]
labels={(row["task_id"],row["sample_index"]):row["pass"] for row in read_jsonl(parent/"linux/evaluation.jsonl")}
decisions=read_jsonl(run/"decisions.jsonl")
rows=[{"task_id":row["task_id"],"sample_index":row["sample_index"],"correct":labels[row["task_id"],row["sample_index"]],
       "first_correct":labels[row["task_id"],0]} for row in decisions]
n=len(json.loads((parent/'manifest.json').read_text(encoding='utf-8'))['task_ids'])
assert len(rows)==len({row['task_id'] for row in rows})==n
delta=[int(row["correct"])-int(row["first_correct"]) for row in rows]
correct=sum(row["correct"] for row in rows)
fixed_temperature=manifest["parent_run"]=="mbpp-temperature-20260906"
write_json(run/"summary.json",{"phase":"Previously chosen policy held fixed on new temperature condition; same exposed tasks" if fixed_temperature else "Development composition, not confirmation","correct":correct,"tasks":n,
    "coverage":1.0,"accuracy":correct/n,"wilson95":wilson(correct,n),"rescues":sum(d>0 for d in delta),
    "regressions":sum(d<0 for d in delta),"paired_difference_vs_first":sum(delta)/n,"paired_task_bootstrap95":paired_interval(delta),
    "new_model_calls":0,"new_execution_calls":0,"limitations":"Policy chosen on original development pool; temperature condition reuses task IDs. No independent-task confirmation or selection-adjusted inference." if fixed_temperature else "Policy selected after inspecting development baseline rescues; do not interpret resampling interval as selection-adjusted confirmation."})
write_json(run/"task-results.json",rows)
print((run/"summary.json").read_text(encoding="utf-8"))

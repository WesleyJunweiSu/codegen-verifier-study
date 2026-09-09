"""Join persisted label-blind consensus decisions to already scored candidate labels."""
import json
import argparse
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verifier_study.io import read_jsonl,write_json,sha256
from analyze_results import wilson,paired_interval

parser=argparse.ArgumentParser()
parser.add_argument("--run",default="mbpp-consensus-20260906")
args=parser.parse_args()
run=ROOT/"runs"/args.run
metadata=json.loads((run/"linux/metadata.json").read_text(encoding="utf-8"))
parent=ROOT/"runs"/metadata["parent_run"]
assert sha256(parent/"generations.jsonl")==metadata["generations_sha256"]
assert sha256(parent/"generated-tests.jsonl")==metadata["tests_sha256"]
assert sha256(run/"linux/decisions.jsonl")==metadata["decisions_sha256"]
labels={(row["task_id"],row["sample_index"]):row["pass"] for row in read_jsonl(parent/"linux/evaluation.jsonl")}
decisions=read_jsonl(run/"linux/decisions.jsonl")
task_ids=sorted({row["task_id"] for row in decisions})
n=metadata['tasks']
assert len(task_ids)==n and len(decisions)==2*n
assert set(task_ids)==set(json.loads((parent/'manifest.json').read_text(encoding='utf-8'))['task_ids'])
task_rows=[]
for task_id in task_ids:
    row={"task_id":task_id,"first_correct":labels[task_id,0]}
    for decision in [item for item in decisions if item["task_id"]==task_id]:
        row[decision["method"]+"_sample_index"]=decision["sample_index"]
        row[decision["method"]+"_correct"]=labels[task_id,decision["sample_index"]]
    task_rows.append(row)
summary={"phase":"Development tasks; consensus adds no model calls","parent_run":parent.name,"tasks":n,"methods":{},
         "execution":metadata,"hidden_labels_loaded_after_decisions":True}
for method in sorted({row["method"] for row in decisions}):
    correct=sum(row[method+"_correct"] for row in task_rows)
    delta=[int(row[method+"_correct"])-int(row["first_correct"]) for row in task_rows]
    summary["methods"][method]={"correct":correct,"tasks":n,"coverage":1.0,"accuracy":correct/n,
        "wilson95":wilson(correct,n),"rescues":sum(d>0 for d in delta),"regressions":sum(d<0 for d in delta),
        "paired_difference_vs_first":sum(delta)/n,"paired_task_bootstrap95":paired_interval(delta)}
write_json(run/"summary.json",summary)
write_json(run/"task-results.json",task_rows)
print(json.dumps(summary,indent=2))

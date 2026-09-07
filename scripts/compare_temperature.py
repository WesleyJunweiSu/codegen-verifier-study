"""Paired development comparison of the frozen 0.7 and 1.0 generation conditions."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verifier_study.io import read_jsonl,write_json
from analyze_results import paired_interval

old=ROOT/"runs/mbpp-parser-ablation-20260905"
new=ROOT/"runs/mbpp-temperature-20260906"
old_rows=read_jsonl(old/"generations.jsonl");new_rows=read_jsonl(new/"generations.jsonl")
old_index={(row["task_id"],row["sample_index"]):row for row in old_rows}
new_index={(row["task_id"],row["sample_index"]):row for row in new_rows}
assert set(old_index)==set(new_index) and len(old_index)==len(old_rows)==len(new_rows)==80
for key in old_index:
    for field in ("seed","prompt_sha256","model_id"):
        assert old_index[key][field]==new_index[key][field],(key,field,"changed")
assert (old/"generated-tests.jsonl").read_bytes()==(new/"generated-tests.jsonl").read_bytes()
old_summary=json.loads((old/"summary.json").read_text(encoding="utf-8"))
new_summary=json.loads((new/"summary.json").read_text(encoding="utf-8"))
old_tasks={row["task_id"]:row for row in json.loads((old/"task-results.json").read_text(encoding="utf-8"))}
new_tasks={row["task_id"]:row for row in json.loads((new/"task-results.json").read_text(encoding="utf-8"))}
old_comp={row["task_id"]:row for row in json.loads((ROOT/"runs/mbpp-public-consensus-20260906/task-results.json").read_text(encoding="utf-8"))}
new_comp={row["task_id"]:row for row in json.loads((ROOT/"runs/mbpp-temperature-public-consensus-20260907/task-results.json").read_text(encoding="utf-8"))}
old_cons={row["task_id"]:row for row in json.loads((ROOT/"runs/mbpp-consensus-20260906/task-results.json").read_text(encoding="utf-8"))}
new_cons={row["task_id"]:row for row in json.loads((ROOT/"runs/mbpp-temperature-consensus-20260907/task-results.json").read_text(encoding="utf-8"))}
tasks=[]
for task_id in sorted(old_tasks):
    task={"task_id":task_id,"old_unique_code":old_tasks[task_id]["unique_code"],"new_unique_code":new_tasks[task_id]["unique_code"]}
    for method in ("first","public_tests","raw_tests","filtered_tests","public_then_filtered","filtered_abstain","oracle"):
        field="oracle_correct" if method=="oracle" else method+"_correct"
        task["old_"+method]=old_tasks[task_id][field]
        task["new_"+method]=new_tasks[task_id][field]
    for method in ("execution_consensus","unique_code_consensus"):
        task["old_"+method]=old_cons[task_id][method+"_correct"]
        task["new_"+method]=new_cons[task_id][method+"_correct"]
    task["old_public_then_consensus"]=old_comp[task_id]["correct"]
    task["new_public_then_consensus"]=new_comp[task_id]["correct"]
    tasks.append(task)
comparisons={}
for method in ("first","public_tests","raw_tests","filtered_tests","public_then_filtered","filtered_abstain","execution_consensus","unique_code_consensus","public_then_consensus","oracle"):
    deltas=[int(row["new_"+method])-int(row["old_"+method]) for row in tasks]
    comparisons[method]={"temperature_0_7_correct":sum(row["old_"+method] for row in tasks),
        "temperature_1_0_correct":sum(row["new_"+method] for row in tasks),
        "gained_tasks":[row["task_id"] for row,d in zip(tasks,deltas) if d>0],
        "lost_tasks":[row["task_id"] for row,d in zip(tasks,deltas) if d<0],
        "paired_accuracy_difference":sum(deltas)/20,"paired_task_bootstrap95":paired_interval(deltas)}
summary={"phase":"Same exposed development tasks; prior selectors fixed; not confirmation","tasks":20,"paired_seeds_and_prompts_verified":True,
    "tests_identical_bytes":True,"inherited_top_k":20,"top_p":0.8,"max_new_tokens":768,
    "comparisons":comparisons,"diversity":{"old_unique_code_total":sum(row["old_unique_code"] for row in tasks),
        "new_unique_code_total":sum(row["new_unique_code"] for row in tasks),"old_all_identical_tasks":old_summary["all_identical_candidate_tasks"],
        "new_all_identical_tasks":new_summary["all_identical_candidate_tasks"]},
    "cost":{"old_candidate_output_tokens":old_summary["candidate_output_tokens"],"new_candidate_output_tokens":new_summary["candidate_output_tokens"],
        "old_candidate_generation_seconds":old_summary["candidate_generation_seconds"],"new_candidate_generation_seconds":new_summary["candidate_generation_seconds"],
        "new_peak_vram_bytes":max(row["peak_vram_bytes"] for row in new_rows),"new_test_generation_tokens":0,
        "limitation":"Different wall-clock sessions and system load; timings exclude loading and other overhead. Equal caps/counts, not equal realized cost."}}
write_json(new/"comparison.json",summary);write_json(new/"paired-task-results.json",tasks)
print(json.dumps(summary,indent=2))

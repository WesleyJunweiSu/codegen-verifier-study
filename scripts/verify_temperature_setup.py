"""Audit paired generation controls before reading any new hidden scores."""
import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verifier_study.io import read_jsonl,write_json,sha256

old=ROOT/"runs/mbpp-pilot-20260905";new=ROOT/"runs/mbpp-temperature-20260906"
a=json.loads((old/"manifest.json").read_text(encoding="utf-8"));b=json.loads((new/"manifest.json").read_text(encoding="utf-8"))
unchanged=[key for key in a if key!="temperature"]
for key in unchanged: assert a[key]==b[key],"Unexpected metadata change: "+key
assert a["temperature"]==.7 and b["temperature"]==1.0
before={(row["task_id"],row["sample_index"]):row for row in read_jsonl(old/"generations.jsonl")}
after={(row["task_id"],row["sample_index"]):row for row in read_jsonl(new/"generations.jsonl")}
assert set(before)==set(after) and len(after)==80
for key in before:
    for field in ("seed","prompt_sha256","model_id","input_tokens"):
        assert before[key][field]==after[key][field],(key,field)
def normalized_function(source,name):
    tree=ast.parse(source)
    return ast.dump(next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name==name),include_attributes=False)
prior=subprocess.check_output(["git","show","11a24ef:scripts/combine_public_consensus.py"],cwd=ROOT).decode("utf-8")
current=(ROOT/"scripts/combine_public_consensus.py").read_text(encoding="utf-8")
assert normalized_function(prior,"select")==normalized_function(current,"select")
diversity={}
for name,rows in (("temperature_0_7",before),("temperature_1_0",after)):
    unique=[len({row["code"] for row in rows.values() if row["task_id"]==task_id}) for task_id in a["task_ids"]]
    diversity[name]={"unique_code_total":sum(unique),"all_identical_tasks":sum(count==1 for count in unique),
                     "parseable_candidates":sum(row["code_parses"] for row in rows.values())}
write_json(new/"pre-score-check.json",{"metadata_unchanged_except_temperature":unchanged,"paired_seeds_prompts_input_counts":True,
    "public_first_consensus_function_AST_unchanged":True,"reference_policy_commit":"11a24ef",
    "source_sha256":sha256(Path(__file__)),"diversity":diversity,"new_hidden_scores_read":False})
print((new/"pre-score-check.json").read_text(encoding="utf-8"))

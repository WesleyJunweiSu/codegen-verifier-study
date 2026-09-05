"""Development-only AST normalization of saved test text. No new model calls or execution."""
import ast
import json
import shutil
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verifier_study.io import read_jsonl,write_json,write_jsonl,sha256
from verifier_study.test_quality import assess_tests

source=ROOT/"runs/mbpp-pilot-20260905"
target=ROOT/"runs/mbpp-parser-ablation-20260905"
if target.exists(): raise SystemExit("Derived run already exists; reuse it rather than overwrite.")
target.mkdir()
tasks={row["task_id"]:row for row in read_jsonl(ROOT/"data/prompts/mbpp-v0.2.0.jsonl")}
records=read_jsonl(source/"generated-tests.jsonl")
converted=0
for row in records:
    row["strict_parse_errors"]=row["parse_errors"]
    row["normalization"]="Top-level comparison expressions converted to assert; no expected-value edits"
    tree=ast.parse(row["raw_output"])
    assertions=[];errors=[];count=0
    for node in tree.body:
        if isinstance(node,ast.Assert): assertions.append(ast.unparse(node))
        elif isinstance(node,ast.Expr) and isinstance(node.value,ast.Compare):
            assertions.append("assert "+ast.unparse(node.value));count+=1
        else: errors.append("non_assert_statement:"+type(node).__name__)
    converted+=count
    row["converted_comparisons"]=count
    row["parse_errors"]=errors
    row["tests"]=assess_tests(assertions,tasks[row["task_id"]]["prompt"],tasks[row["task_id"]]["entry_point"])
for name in ("generations.jsonl","manifest.json","progress.json"):
    shutil.copyfile(source/name,target/name)
write_jsonl(target/"generated-tests.jsonl",records)
write_json(target/"test-manifest.json",{
    "parent_run":source.name,"parent_tests_sha256":sha256(source/"generated-tests.jsonl"),
    "normalization":"AST Expr(Compare) to Assert; original text and strict errors retained",
    "converted_comparisons":converted,"new_model_calls":0,"new_generation_tokens":0,
    "selector_extension":"public_then_filtered: lexicographic public passes, then filtered generated-test passes",
    "development_adaptation":"Chosen after inspecting initial pilot; not independent confirmation",
    "source_script_sha256":sha256(Path(__file__)),"selection_code_sha256":sha256(ROOT/"src/verifier_study/selection.py")})
print(json.dumps({"run":target.name,"converted":converted,"assertions":sum(len(row['tests']) for row in records)}))

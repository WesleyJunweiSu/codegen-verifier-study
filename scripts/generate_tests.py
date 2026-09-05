"""Generate natural tests from public task specifications without seeing candidate code."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verifier_study.generation import LocalCausalLM
from verifier_study.io import append_jsonl,read_jsonl,sha256,write_json
from verifier_study.test_quality import assess_tests,parse_assertions

SYSTEM="""Write Python assert statements to test a function from its specification.
Return only 8 independent assert statements. No Markdown, imports, helper functions,
loops, or explanations. Include valid edge cases. Each assertion must call the requested
function and check its result against an independently reasoned expected value.
Do not compare a function call to another call to the same function as an oracle.
Do not invent input-domain restrictions or require unspecified behavior."""


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--model-path",required=True)
    parser.add_argument("--run",default="mbpp-pilot-20260905")
    args=parser.parse_args()
    os.environ["HF_HUB_OFFLINE"]="1";os.environ["TRANSFORMERS_OFFLINE"]="1"
    run=ROOT/"runs"/args.run
    manifest=json.loads((run/"manifest.json").read_text(encoding="utf-8"))
    tasks={row["task_id"]:row for row in read_jsonl(ROOT/"data/prompts/mbpp-v0.2.0.jsonl")}
    config={"system_prompt":SYSTEM,"generator":"Qwen/Qwen3-4B","generation_manifest_sha256":sha256(run/"manifest.json"),
            "temperature":0.7,"top_p":0.8,"max_new_tokens":768,"candidates_visible":False,"hidden_tests_visible":False,
            "quality_code_sha256":sha256(ROOT/"src/verifier_study/test_quality.py")}
    config_path=run/"test-manifest.json"
    if config_path.exists(): assert json.loads(config_path.read_text(encoding="utf-8"))==config,"Test-generation config mismatch"
    else: write_json(config_path,config)
    path=run/"generated-tests.jsonl"
    existing=read_jsonl(path) if path.exists() else []
    done={row["task_id"] for row in existing}
    assert len(done)==len(existing)
    model=LocalCausalLM(args.model_path,"Qwen/Qwen3-4B")
    for task_id in manifest["task_ids"]:
        if task_id in done: continue
        task=tasks[task_id]
        messages=[{"role":"system","content":SYSTEM},{"role":"user","content":task["prompt"]+"\nFunction name: "+task["entry_point"]}]
        seed=int(hashlib.sha256(f"test:20260905:{task_id}".encode()).hexdigest()[:8],16)
        record=model._generate_messages(task_id=task_id,messages=messages,sample_index=0,seed=seed,generation_kind="spec_tests",
                                        max_new_tokens=768,temperature=0.7,top_p=0.8).to_dict()
        assertions,errors=parse_assertions(record["raw_output"])
        record["parse_errors"]=errors
        record["tests"]=assess_tests(assertions,task["prompt"],task["entry_point"])
        append_jsonl(path,record)
        done.add(task_id)
        print(f"Tests {len(done)}/{len(manifest['task_ids'])} {task_id}: parsed={len(assertions)} kept={sum(t['keep'] for t in record['tests'])} tokens={record['output_tokens']} seconds={record['wall_seconds']:.2f}",flush=True)


if __name__=="__main__": main()

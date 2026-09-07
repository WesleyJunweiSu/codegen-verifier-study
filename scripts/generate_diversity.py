"""One frozen temperature intervention, resumable and guarded by observed GPU headroom."""
import argparse
import datetime
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verifier_study.io import read_jsonl,write_json,append_jsonl,sha256


def finalize_tests(out,test_parent):
    target=out/"generated-tests.jsonl"
    raw=(test_parent/"generated-tests.jsonl").read_bytes()
    if target.exists(): assert target.read_bytes()==raw,"Refusing to overwrite changed reused tests"
    else: target.write_bytes(raw)
    write_json(out/"test-manifest.json",{"parent_run":test_parent.name,"test_generation_reused":True,"candidate_generation_reused":False,
        "new_test_model_calls":0,"tests_sha256":sha256(test_parent/"generated-tests.jsonl")})


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--model-path",required=True)
    parser.add_argument("--check-only",action="store_true")
    args=parser.parse_args()
    config_path=ROOT/"configs/temperature-intervention.json"
    config=json.loads(config_path.read_text(encoding="utf-8"))
    out=ROOT/"runs"/config["run_id"];out.mkdir(parents=True,exist_ok=True)
    parent=ROOT/"runs"/config["parent_candidate_run"]
    test_parent=ROOT/"runs"/config["parent_test_run"]
    parent_manifest=json.loads((parent/"manifest.json").read_text(encoding="utf-8"))
    tasks={row["task_id"]:row for row in read_jsonl(ROOT/"data/prompts/mbpp-v0.2.0.jsonl")}
    seeds={(row["task_id"],row["sample_index"]):row["seed"] for row in read_jsonl(parent/"generations.jsonl")}
    path=out/"generations.jsonl"
    records=read_jsonl(path) if path.exists() else []
    done={(row["task_id"],row["sample_index"]) for row in records}
    assert len(done)==len(records)
    if (out/"manifest.json").exists():
        frozen=json.loads((out/"manifest.json").read_text(encoding="utf-8"))
        assert frozen["intervention_config_sha256"]==sha256(config_path),"Intervention config changed"
    planned=len(parent_manifest["task_ids"])*config["candidates_per_task"]
    assert done<=set(seeds),"Unexpected candidate keys in resumable run"
    if len(done)==planned:
        finalize_tests(out,test_parent)
        print("All frozen generations already complete; test reuse finalized, no model loaded.");return
    query=subprocess.check_output(["nvidia-smi","--query-gpu=memory.free,utilization.gpu","--format=csv,noheader,nounits"],text=True)
    free,utilization=[int(value.strip()) for value in query.splitlines()[0].split(",")]
    sufficient=free>=config["gpu_minimum_free_mib"]
    attempt={"utc":datetime.datetime.now(datetime.UTC).isoformat(),"free_mib":free,"gpu_utilization_percent":utilization,
        "required_free_mib":config["gpu_minimum_free_mib"],"status":"ready" if sufficient else "deferred_insufficient_vram",
        "config_sha256":sha256(config_path),"completed":len(done),"planned":planned,"model_loaded":False}
    append_jsonl(out/"attempts.jsonl",attempt);print(json.dumps(attempt),flush=True)
    if args.check_only or not sufficient: return
    model_path=Path(args.model_path)
    fingerprint=json.loads((ROOT/"configs/model-fingerprint.json").read_text(encoding="utf-8"))
    for item in fingerprint["files"]: assert sha256(model_path/item["file"])==item["sha256"],"Checkpoint mismatch: "+item["file"]
    manifest={**parent_manifest,"temperature":config["temperature"],"top_p":config["top_p"],
        "intervention_config_sha256":sha256(config_path),"generator_script_sha256":sha256(Path(__file__)),
        "parent_candidate_run":parent.name,"parent_tests_sha256":sha256(test_parent/"generated-tests.jsonl"),
        "packages":{name:importlib.metadata.version(name) for name in ["torch","transformers","accelerate","tokenizers"]}}
    manifest_path=out/"manifest.json"
    if manifest_path.exists(): assert json.loads(manifest_path.read_text(encoding="utf-8"))==manifest,"Resume configuration mismatch"
    else: write_json(manifest_path,manifest)
    os.environ["HF_HUB_OFFLINE"]="1";os.environ["TRANSFORMERS_OFFLINE"]="1"
    from verifier_study.generation import LocalCausalLM
    started=time.perf_counter();model=LocalCausalLM(args.model_path,"Qwen/Qwen3-4B")
    print(f"Loaded model in {time.perf_counter()-started:.2f}s",flush=True)
    for task_id in parent_manifest["task_ids"]:
        for index in range(config["candidates_per_task"]):
            if (task_id,index) in done: continue
            record=model.generate(task_id=task_id,function_prompt=tasks[task_id]["prompt"],sample_index=index,seed=seeds[task_id,index],
                max_new_tokens=config["max_new_tokens"],temperature=config["temperature"],top_p=config["top_p"]).to_dict()
            append_jsonl(path,record);records.append(record);done.add((task_id,index))
            write_json(out/"progress.json",{"completed":len(records),"planned":planned,"output_tokens":sum(row["output_tokens"] for row in records),
                "generation_seconds":sum(row["wall_seconds"] for row in records),"peak_vram_bytes":max(row["peak_vram_bytes"] for row in records),
                "status":"complete" if len(records)==planned else "running"})
            print(f"{len(records)}/{planned} {task_id} sample={index} tokens={record['output_tokens']}",flush=True)
    finalize_tests(out,test_parent)


if __name__=="__main__": main()

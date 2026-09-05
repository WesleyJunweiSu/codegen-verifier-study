"""Resumable local GPU generation. Reads only generator-visible task fields."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from verifier_study.io import append_jsonl, candidate_key, read_jsonl, sha256, write_json
from verifier_study.generation import LocalCausalLM


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--run", default="mbpp-pilot-20260905")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--candidates", type=int, default=4)
    parser.add_argument("--max-new-tokens", type=int, default=768)
    args = parser.parse_args()
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    split = json.loads((ROOT / "configs/split-manifest.json").read_text(encoding="utf-8"))
    tasks = {row["task_id"]: row for row in read_jsonl(ROOT / "data/prompts/mbpp-v0.2.0.jsonl")}
    ids = split["pilot"][:args.limit]
    out = ROOT / "runs" / args.run
    out.mkdir(parents=True, exist_ok=True)
    metadata = {
        "model_id": "Qwen/Qwen3-4B", "model_config_sha256": sha256(Path(args.model_path) / "config.json"),
        "split_sha256": sha256(ROOT / "configs/split-manifest.json"),
        "visible_prompts_sha256": sha256(ROOT / "data/prompts/mbpp-v0.2.0.jsonl"),
        "task_ids": ids, "candidates_per_task": args.candidates, "precision": "bfloat16",
        "thinking": False, "temperature": 0.7, "top_p": 0.8, "max_new_tokens": args.max_new_tokens,
        "python": platform.python_version(),
        "packages": {name: importlib.metadata.version(name) for name in ["torch", "transformers", "accelerate", "tokenizers"]},
        "generation_backend_sha256": sha256(ROOT / "src/verifier_study/generation.py"),
        "hidden_tests_visible_to_generator": False,
    }
    manifest_path = out / "manifest.json"
    if manifest_path.exists():
        assert json.loads(manifest_path.read_text(encoding="utf-8")) == metadata, "Resume configuration mismatch"
    else:
        write_json(manifest_path, metadata)
    records_path = out / "generations.jsonl"
    records = read_jsonl(records_path) if records_path.exists() else []
    completed = {candidate_key(row) for row in records}
    assert len(completed) == len(records), "Duplicate generation records"
    print(f"Loading model; {len(completed)}/{len(ids)*args.candidates} generations already recorded", flush=True)
    load_start = time.perf_counter()
    model = LocalCausalLM(args.model_path, "Qwen/Qwen3-4B")
    print(f"Model ready in {time.perf_counter()-load_start:.1f}s", flush=True)
    for task_id in ids:
        for index in range(args.candidates):
            if (task_id, index) in completed:
                continue
            seed = int(hashlib.sha256(f"20260905:{task_id}:{index}".encode()).hexdigest()[:8], 16)
            record = model.generate(task_id=task_id, function_prompt=tasks[task_id]["prompt"], sample_index=index,
                                    seed=seed, max_new_tokens=args.max_new_tokens).to_dict()
            append_jsonl(records_path, record)
            records.append(record)
            print(f"{len(records)}/{len(ids)*args.candidates} {task_id} sample={index} tokens={record['output_tokens']} seconds={record['wall_seconds']:.2f} parses={record['code_parses']}", flush=True)
            write_json(out / "progress.json", {"completed":len(records),"planned":len(ids)*args.candidates,
                       "output_tokens":sum(x["output_tokens"] for x in records),
                       "generation_seconds":sum(x["wall_seconds"] for x in records),
                       "peak_vram_bytes":max(x["peak_vram_bytes"] for x in records),
                       "status":"complete" if len(records)==len(ids)*args.candidates else "running"})


if __name__ == "__main__":
    main()

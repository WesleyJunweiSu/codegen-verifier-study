"""Freeze remaining development task IDs without loading prompts, references or outcomes."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verifier_study.io import write_json,sha256

split=json.loads((ROOT/"configs/split-manifest.json").read_text(encoding="utf-8"))
ids=split["development"][20:60]
assert len(ids)==len(set(ids))==40 and not set(ids)&set(split["pilot"])
assert not set(ids)&set(split["calibration"]+split["confirmation"]+split["reserve"])
config={"recorded_date":"2026-09-07","run_id":"mbpp-development40-20260907",
    "task_ids":ids,"split_manifest_sha256":sha256(ROOT/"configs/split-manifest.json"),
    "phase":"Remaining development tasks, excluding inspected 20-task pilot; not the reserved confirmation set",
    "purpose":"Test the already chosen selection rules on additional tasks before tuning or using calibration/confirmation labels",
    "model":"Same fingerprinted Qwen3-4B BF16 non-thinking","temperature":0.7,"top_p":0.8,"top_k":20,"max_new_tokens":768,
    "candidates_per_task":4,"candidate_seed_rule":"sha256('20260905:{task_id}:{sample_index}')[:8] interpreted as hex integer",
    "tests":"Same public-spec-only eight-assertion prompt and test seed rule as the pilot; apply already documented AST comparison normalization",
    "selectors":"First, public, raw/filtered tests, execution/unique-code consensus, fixed public-first consensus; no threshold or tie-break tuning",
    "policy_source_commit":"11a24ef7db6f7dda7aa6a6c9c578bd270e08a419","gpu_minimum_free_mib":9216,
    "failure_policy":"Persist all failed/malformed/empty outputs; retain all 40 task denominators",
    "rationale_for_temperature":"Original baseline setting, not a winner established by the small temperature comparison",
    "status":"Protocol only; generation and scoring not started"}
target=ROOT/"configs/development-expansion.json"
if target.exists(): assert json.loads(target.read_text(encoding="utf-8"))==config,"Refusing to alter frozen expansion"
else: write_json(target,config)
print("Frozen",len(ids),"remaining development IDs without reading their task contents or labels")

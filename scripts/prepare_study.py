"""Prepare frozen, disjoint splits and generator-visible prompts. Executes no code."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from verifier_study.io import read_jsonl, sha256, write_json, write_jsonl


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=str(ROOT / "data/private/MbppPlus.jsonl"))
    args = parser.parse_args()
    rows = read_jsonl(args.dataset)
    ids = [row["task_id"] for row in rows]
    assert len(ids) == len(set(ids)) == 378
    seed = 20260905
    ordered = sorted(ids, key=lambda task: hashlib.sha256(f"{seed}:{task}".encode()).hexdigest())
    manifest = {
        "dataset": "MBPP+", "version": "v0.2.0", "sha256": sha256(args.dataset),
        "split_seed": seed, "ordering": "sha256(seed:task_id)",
        "development": ordered[:60], "calibration": ordered[60:120],
        "confirmation": ordered[120:300], "reserve": ordered[300:],
        "pilot": ordered[:20],
        "prior_usage_audit": "Previous repository PROGRESS.md explicitly records MBPP+ as not performed.",
        "stage": "Frozen before new generation or scoring; not public preregistration.",
    }
    target = ROOT / "configs/split-manifest.json"
    if target.exists():
        assert json.loads(target.read_text(encoding="utf-8")) == manifest, "Refusing to alter frozen split"
    else:
        write_json(target, manifest)
    # Deliberately exclude canonical_solution, assertion, contract, base_input and plus_input.
    visible = [{key: row[key] for key in ("task_id", "prompt", "entry_point")} for row in rows]
    write_jsonl(ROOT / "data/prompts/mbpp-v0.2.0.jsonl", visible)
    print(json.dumps({"tasks": len(rows), "dev": 60, "calibration": 60, "confirmation": 180, "reserve": 78, "pilot": 20}))


if __name__ == "__main__":
    main()

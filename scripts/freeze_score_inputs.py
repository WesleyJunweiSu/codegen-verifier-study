"""Freeze score inputs from visible evidence, without reading correctness labels."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifier_study.io import read_jsonl, write_json, sha256
from verifier_study.frozen_decisions import validate_decisions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', default='mbpp-development40-repair-20260908')
    args = parser.parse_args()
    run = ROOT/'runs'/args.run
    metadata = json.loads((run/'visible/metadata.json').read_text())
    manifest = json.loads((run/'manifest.json').read_text())
    repair = json.loads((run/'repair-plan.json').read_text())
    assert metadata['hidden_benchmark_mounted'] is False and metadata['hidden_reference_loading'] is False
    for field, name in [('generations_sha256', 'generations.jsonl'), ('tests_sha256', 'generated-tests.jsonl'),
                        ('manifest_sha256', 'manifest.json'), ('repair_plan_sha256', 'repair-plan.json'),
                        ('decisions_sha256', 'visible/decisions.jsonl'), ('matrix_sha256', 'visible/candidate-test-matrix.jsonl')]:
        assert sha256(run/name) == metadata[field], field
    split_path = ROOT/'configs/split-manifest.json'
    split = json.loads(split_path.read_text())
    plan = {'schema_version': 1, 'task_ids': manifest['task_ids'],
            'methods': ['selected_baseline'] + [a['method'] for a in repair['arms']] + (['first'] if repair.get('include_first_baseline') else []),
            'generations_sha256': sha256(run/'generations.jsonl'), 'decisions_sha256': sha256(run/'visible/decisions.jsonl'),
            'dataset_sha256': split['sha256'], 'split_manifest_sha256': sha256(split_path),
            'visible_metadata_sha256': sha256(run/'visible/metadata.json'),
            'freeze_script_sha256': sha256(Path(__file__))}
    validate_decisions(plan, read_jsonl(run/'generations.jsonl'), read_jsonl(run/'visible/decisions.jsonl'))
    data = (run/'visible/decisions.jsonl').read_bytes()
    target = run/'frozen-decisions.jsonl'
    if target.exists(): assert target.read_bytes() == data
    else: target.write_bytes(data)
    if (run/'score-plan.json').exists(): assert json.loads((run/'score-plan.json').read_text()) == plan
    else: write_json(run/'score-plan.json', plan)
    print('Frozen', len(plan['task_ids']), 'tasks and', len(plan['methods']), 'methods without reading hidden labels')


if __name__ == '__main__': main()

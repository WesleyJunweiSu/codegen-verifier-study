"""Freeze all development routing decisions in a restricted, reference-free container."""
import json
import os
import platform
from pathlib import Path
from verifier_study.io import read_jsonl, write_json, write_jsonl, sha256
from verifier_study.routing_v2 import METHODS, select_routing
from verifier_study.frozen_decisions import validate_decisions


def make_score_plan(task_ids, dataset_sha256, generations_sha256, decisions_sha256):
    return dict(schema_version=1, task_ids=task_ids, methods=METHODS,
                dataset_sha256=dataset_sha256, generations_sha256=generations_sha256,
                decisions_sha256=decisions_sha256)


def main():
    assert platform.system() == 'Linux' and os.environ.get('VERIFIER_ISOLATED_RUN') == '1'
    source, out = Path('/inputs'), Path('/output')
    plan = json.loads((source/'routing-plan.json').read_text())
    records = read_jsonl(source/'generations.jsonl')
    expected = {(t['task_id'], t['selected_index']) for t in plan['tasks']}
    expected |= {(t['task_id'], i) for t in plan['tasks'] if t['triggered'] for i in [5, 7]}
    assert len(records) == len(expected) and {(r['task_id'], r['sample_index']) for r in records} == expected
    assert not (source/'repair-plan.json').exists()
    from test_matrix_linux import build_matrix
    build_matrix(records, source/'generated-tests.jsonl', out)
    decisions = select_routing(plan, read_jsonl(out/'candidate-test-matrix.jsonl'))
    write_jsonl(out/'frozen-decisions.jsonl', decisions)
    score_plan = make_score_plan(plan['task_ids'], plan['dataset_sha256'],
        sha256(source/'generations.jsonl'), sha256(out/'frozen-decisions.jsonl'))
    validate_decisions(score_plan, records, decisions)
    write_json(out/'score-plan.json', score_plan)
    write_json(out/'metadata.json', dict(hidden_benchmark_mounted=False, hidden_reference_loading=False,
        routing_plan_sha256=sha256(source/'routing-plan.json'), score_plan_sha256=sha256(out/'score-plan.json'),
        generations_sha256=sha256(source/'generations.jsonl'), matrix_sha256=sha256(out/'candidate-test-matrix.jsonl')))


if __name__ == '__main__': main()

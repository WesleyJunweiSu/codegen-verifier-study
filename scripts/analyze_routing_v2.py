"""Report every development routing arm, including regressions and reused compute."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifier_study.io import read_jsonl, write_json, sha256
from verifier_study.routing_v2 import METHODS
from verifier_study.frozen_decisions import validate_decisions


def main():
    run = ROOT/'runs/mbpp-routing-v2-development-20260911'
    plan = json.loads((run/'routing-plan.json').read_text())
    for path, digest in plan['source_hashes'].items():
        assert sha256(ROOT/path) == digest, path
    score_plan = json.loads((run/'visible/score-plan.json').read_text())
    metadata = json.loads((run/'linux/metadata.json').read_text())
    assert metadata['generations_sha256'] == sha256(run/'generations.jsonl') == score_plan['generations_sha256']
    assert metadata['score_plan_sha256'] == sha256(run/'visible/score-plan.json')
    assert metadata['dataset_sha256'] == plan['dataset_sha256']
    assert (run/'linux/decisions.jsonl').read_bytes() == (run/'visible/frozen-decisions.jsonl').read_bytes()
    assert sha256(run/'linux/decisions.jsonl') == score_plan['decisions_sha256']
    decisions = read_jsonl(run/'linux/decisions.jsonl')
    records = read_jsonl(run/'generations.jsonl')
    validate_decisions(score_plan, records, decisions)
    labels = read_jsonl(run/'linux/evaluation.jsonl')
    key = lambda row: (row['task_id'], row['sample_index'])
    assert len(labels) == len({key(r) for r in labels}) == len(records)
    assert {key(r) for r in labels} == {key(r) for r in records}
    labels = {key(r): r['pass'] for r in labels}
    outcomes = {method: {r['task_id']: labels[key(r)] for r in decisions if r['method'] == method} for method in METHODS}
    base = outcomes['selected_baseline']
    assert len(base) == 40
    summary = {}
    for method, values in outcomes.items():
        assert set(values) == set(base)
        rescued = [t for t in base if not base[t] and values[t]]
        regressed = [t for t in base if base[t] and not values[t]]
        summary[method] = dict(correct=sum(values.values()), tasks=40, accuracy=sum(values.values())/40,
            gain_percentage_points=100*(sum(values.values())-sum(base.values()))/40,
            rescued=rescued, regressed=regressed,
            transition_matrix={'wrong_to_correct': len(rescued), 'correct_to_wrong': len(regressed),
                'correct_to_correct': sum(base[t] and values[t] for t in base),
                'wrong_to_wrong': sum(not base[t] and not values[t] for t in base)})
    # Existing public-only arms must reproduce completed transfer decisions and labels.
    old = read_jsonl(ROOT/'runs/mbpp-development40-repair-20260908/linux/decisions.jsonl')
    for mode in ['nonthinking', 'reasoning']:
        expected = {r['task_id']: r['sample_index'] for r in old if r['method'] == mode+'_resample'}
        actual = {r['task_id']: r['sample_index'] for r in decisions if r['method'] == 'public_'+mode+'_strict'}
        assert actual == expected
        assert summary['public_'+mode+'_strict']['correct'] == (32 if mode == 'nonthinking' else 33)
    costs = {}
    new_keys = {key(r) for r in read_jsonl(run/'new-generations.jsonl')}
    for mode, index in [('nonthinking', 5), ('reasoning', 7)]:
        calls = [r for r in records if r['sample_index'] == index]
        costs[mode] = dict(calls=len(calls), newly_generated=sum(key(r) in new_keys for r in calls),
            output_tokens=sum(r['output_tokens'] for r in calls), wall_seconds=sum(r['wall_seconds'] for r in calls))
    write_json(run/'summary.json', dict(scope='Adaptive development, not independent confirmation; all seven arms reported',
        methods=summary, extension_costs=costs, timing_limitation='Uncontrolled desktop wall time; includes reused calls',
        evaluation_sha256=sha256(run/'linux/evaluation.jsonl'), decisions_sha256=sha256(run/'linux/decisions.jsonl')))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__': main()

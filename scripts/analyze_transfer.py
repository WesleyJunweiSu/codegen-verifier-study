"""Analyze complete four-arm decisions after isolated scoring; never execute code."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifier_study.io import read_jsonl, write_json, sha256
from analyze_results import wilson, paired_interval


def main():
    run = ROOT/'runs/mbpp-development40-repair-20260908'
    plan = json.loads((run/'repair-plan.json').read_text(encoding='utf-8'))
    parent = ROOT/'runs'/plan['parent_run']
    metadata = json.loads((run/'linux/metadata.json').read_text(encoding='utf-8'))
    for field, name in [('generations_sha256', 'generations.jsonl'), ('tests_sha256', 'generated-tests.jsonl'), ('decisions_sha256', 'linux/decisions.jsonl')]:
        assert sha256(run/name) == metadata[field]
    assert metadata['decision_order'] == 'Candidate/test matrix and decisions saved before loading hidden benchmark data'
    config = ROOT/'configs/development-repair-transfer.json'
    assert sha256(config) == plan['source_hashes'][str(config.relative_to(ROOT))]
    assert (run/'generated-tests.jsonl').read_bytes() == (parent/'generated-tests.jsonl').read_bytes()
    labels_raw = read_jsonl(run/'linux/evaluation.jsonl')
    labels = {(r['task_id'], r['sample_index']): r['pass'] for r in labels_raw}
    candidates = read_jsonl(run/'generations.jsonl')
    assert len(labels) == len(labels_raw) == len(candidates)
    assert set(labels) == {(r['task_id'], r['sample_index']) for r in candidates}
    old = {(r['task_id'], r['sample_index']): r['pass'] for r in read_jsonl(parent/'linux/evaluation.jsonl')}
    for t in plan['tasks']:
        key = t['task_id'], t['selected_index']
        assert labels[key] == old[key], 'Reused label changed'
    decisions = read_jsonl(run/'linux/decisions.jsonl')
    methods = ['selected_baseline'] + [a['method'] for a in plan['arms']]
    task_ids = {t['task_id'] for t in plan['tasks']}
    assert len(task_ids) == len(plan['tasks']) == 40
    assert len(decisions) == len(task_ids)*len(methods)
    assert {(r['task_id'], r['method']) for r in decisions} == {(t, m) for t in task_ids for m in methods}
    by_method = {m: {r['task_id']: labels[r['task_id'], r['sample_index']] for r in decisions if r['method'] == m} for m in methods}
    new = read_jsonl(run/'new-generations.jsonl')
    expected_new = {(t['task_id'], a['sample_index']) for t in plan['tasks'] if t['triggered'] for a in plan['arms']}
    assert len(new) == len(expected_new) and {(r['task_id'], r['sample_index']) for r in new} == expected_new
    summary = {'phase': plan['phase'], 'tasks': 40, 'triggered_tasks': sum(t['triggered'] for t in plan['tasks']),
               'methods': {}, 'comparisons': {}, 'extra_cost': {}, 'executor_seconds': metadata['wall_seconds'],
               'limitations': 'Additional development, not confirmation. Calls and output caps match within mode; realized input/output tokens and wall time differ. Desktop runtime is uncontrolled. No hidden-outcome tuning of triggers or replacements.'}
    for method in methods:
        correct = sum(by_method[method].values())
        delta = [int(by_method[method][t]) - int(by_method['selected_baseline'][t]) for t in sorted(task_ids)]
        summary['methods'][method] = {'correct': correct, 'tasks': 40, 'accuracy': correct/40, 'coverage': 1.0,
            'wilson95': wilson(correct, 40), 'rescues': sum(x > 0 for x in delta), 'regressions': sum(x < 0 for x in delta)}
    comparisons = [('primary_reasoning_vs_nonthinking_resample', 'reasoning_resample', 'nonthinking_resample'),
                   ('reasoning_feedback_vs_resample', 'reasoning_feedback_repair', 'reasoning_resample'),
                   ('nonthinking_feedback_vs_resample', 'nonthinking_feedback_repair', 'nonthinking_resample')]
    for name, left, right in comparisons:
        delta = [int(by_method[left][t]) - int(by_method[right][t]) for t in sorted(task_ids)]
        summary['comparisons'][name] = {'difference': sum(delta)/40, 'paired_task_bootstrap95': paired_interval(delta)}
    for arm in plan['arms']:
        rows = [r for r in new if r['sample_index'] == arm['sample_index']]
        summary['extra_cost'][arm['method']] = {'model_calls': len(rows), 'input_tokens': sum(r['input_tokens'] for r in rows),
           'output_tokens': sum(r['output_tokens'] for r in rows), 'generation_seconds': sum(r['wall_seconds'] for r in rows),
           'peak_vram_bytes': max((r['peak_vram_bytes'] for r in rows), default=0),
           'capped': sum(r['output_tokens'] == arm['max_new_tokens'] for r in rows),
           'incomplete_reasoning': sum(r.get('thinking_complete') is False for r in rows)}
    write_json(run/'summary.json', summary)
    write_json(run/'task-results.json', [{**r, 'correct': labels[r['task_id'], r['sample_index']]} for r in decisions])
    print(json.dumps(summary, indent=2))


if __name__ == '__main__': main()

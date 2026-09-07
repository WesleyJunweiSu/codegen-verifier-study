"""Score decisions already persisted before hidden-label loading in Linux."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifier_study.io import read_jsonl, write_json, sha256
from analyze_results import paired_interval, wilson

run = ROOT/'runs/mbpp-repair-20260907'
plan = json.loads((run/'repair-plan.json').read_text(encoding='utf-8'))
metadata = json.loads((run/'linux/metadata.json').read_text(encoding='utf-8'))
assert sha256(run/'generations.jsonl') == metadata['generations_sha256']
assert sha256(run/'linux/decisions.jsonl') == metadata['decisions_sha256']
assert metadata['decision_order'] == 'Candidate/test matrix and decisions saved before loading hidden benchmark data'
decisions = read_jsonl(run/'linux/decisions.jsonl')
labels = {(r['task_id'], r['sample_index']): r['pass'] for r in read_jsonl(run/'linux/evaluation.jsonl')}
generations = read_jsonl(run/'new-generations.jsonl')
old_labels = {(r['task_id'], r['sample_index']): r['pass'] for r in
              read_jsonl(ROOT/'runs/mbpp-parser-ablation-20260905/linux/evaluation.jsonl')}
for task in plan['tasks']:
    key = task['task_id'], task['selected_index']
    assert labels[key] == old_labels[key], 'Reused-candidate scoring changed'
by_method = {}
task_rows = []
for method in ['selected_baseline', 'public_feedback_repair', 'extra_sample_control']:
    rows = [r for r in decisions if r['method'] == method]
    assert len(rows) == len({r['task_id'] for r in rows}) == len(plan['tasks'])
    by_method[method] = {r['task_id']: labels[r['task_id'], r['sample_index']] for r in rows}
    task_rows.extend({**r, 'correct': labels[r['task_id'], r['sample_index']]} for r in rows)
n = len(plan['tasks'])
summary = {'phase': plan['phase'], 'tasks': n, 'triggered_tasks': sum(t['triggered'] for t in plan['tasks']),
           'methods': {}, 'comparison': {}, 'cost': {}, 'executor_seconds': metadata['wall_seconds'],
           'limitations': 'Only 20 exposed development tasks; method chosen using their public failures. Equal extra calls and output caps, not equal realized tokens or runtime. Neither significance nor independent-task generalization is established.'}
for method, correct in by_method.items():
    values = [int(correct[t['task_id']]) - int(by_method['selected_baseline'][t['task_id']]) for t in plan['tasks']]
    count = sum(correct.values())
    summary['methods'][method] = {'correct': count, 'accuracy': count/n, 'coverage': 1.0,
          'wilson95': wilson(count, n), 'rescues_vs_selected': sum(x > 0 for x in values),
          'regressions_vs_selected': sum(x < 0 for x in values)}
for name, left, right in [('repair_vs_baseline', 'public_feedback_repair', 'selected_baseline'),
                           ('repair_vs_extra_sample', 'public_feedback_repair', 'extra_sample_control')]:
    delta = [int(by_method[left][t['task_id']]) - int(by_method[right][t['task_id']]) for t in plan['tasks']]
    summary['comparison'][name] = {'difference': sum(delta)/n, 'paired_task_bootstrap95': paired_interval(delta)}
for method, index in [('public_feedback_repair', 4), ('extra_sample_control', 5)]:
    rows = [r for r in generations if r['sample_index'] == index]
    summary['cost'][method] = {'extra_model_calls': len(rows), 'input_tokens': sum(r['input_tokens'] for r in rows),
          'output_tokens': sum(r['output_tokens'] for r in rows), 'generation_seconds': sum(r['wall_seconds'] for r in rows),
          'peak_vram_bytes': max(r['peak_vram_bytes'] for r in rows),
          'truncated_at_cap': sum(r['output_tokens'] == plan['max_new_tokens'] for r in rows)}
write_json(run/'task-results.json', task_rows)
write_json(run/'summary.json', summary)
print(json.dumps(summary, indent=2))

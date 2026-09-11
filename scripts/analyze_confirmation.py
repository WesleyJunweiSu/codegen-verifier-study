"""Final prespecified task-paired analysis after all confirmation decisions are frozen."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifier_study.io import read_jsonl, sha256, write_json
from verifier_study.frozen_decisions import validate_decisions
from verifier_study.paired_inference import exact_mcnemar
from analyze_results import paired_interval, wilson
from confirmation import load_config


def main():
    config, digest = load_config()
    run = ROOT/'runs'/config['extension_run']; base = ROOT/'runs'/config['base_run']
    metadata = json.loads((run/'linux/metadata.json').read_text())
    assert metadata['decision_order'] == 'Externally frozen decisions validated before reference loading; scorer never selects'
    for field, path in [('decisions_sha256', run/'frozen-decisions.jsonl'), ('generations_sha256', run/'generations.jsonl'),
                        ('score_plan_sha256', run/'score-plan.json')]: assert sha256(path) == metadata[field]
    assert (run/'linux/decisions.jsonl').read_bytes() == (run/'frozen-decisions.jsonl').read_bytes()
    assert metadata['dataset_sha256'] == config['dataset_sha256']
    assert json.loads((run/'manifest.json').read_text())['confirmation_protocol_sha256'] == digest
    plan = json.loads((run/'score-plan.json').read_text())
    assert plan['task_ids'] == config['task_ids'] and set(plan['methods']) == set(config['reported_methods'])
    candidates = read_jsonl(run/'generations.jsonl'); decisions = read_jsonl(run/'frozen-decisions.jsonl')
    validate_decisions(plan, candidates, decisions)
    # No correctness labels are read until the frozen input/decision checks pass.
    raw_labels = read_jsonl(run/'linux/evaluation.jsonl')
    labels = {(r['task_id'], r['sample_index']): r for r in raw_labels}
    assert len(labels) == len(raw_labels) == len(candidates)
    for row in candidates:
        assert labels[row['task_id'], row['sample_index']]['code_sha256'] == hashlib.sha256(row['code'].encode()).hexdigest()
    keyed = {(r['task_id'], r['method']): r for r in decisions}
    outcomes = {m: [bool(keyed[t, m]['accepted'] and labels[t, keyed[t, m]['sample_index']]['pass'])
                   for t in config['task_ids']] for m in config['reported_methods']}
    primary = exact_mcnemar(outcomes['reasoning_resample'], outcomes['nonthinking_resample'])
    delta = [int(a) - int(b) for a, b in zip(outcomes['reasoning_resample'], outcomes['nonthinking_resample'])]
    primary.update({'paired_task_bootstrap95': paired_interval(delta), 'comparison': config['primary_comparison']})
    summary = {'phase': 'Prespecified 180-task confirmation', 'protocol_sha256': digest, 'tasks': 180,
               'primary': primary, 'methods': {}, 'cost': {}, 'scoring_seconds': metadata['wall_seconds']}
    for method, values in outcomes.items():
        paired = exact_mcnemar(values, outcomes['selected_baseline'])
        summary['methods'][method] = {'correct': sum(values), 'tasks': 180, 'accuracy': sum(values)/180,
            'coverage': sum(keyed[t, method]['accepted'] for t in config['task_ids'])/180,
            'wilson95': wilson(sum(values), 180), 'rescues_vs_selected': paired['wins'], 'regressions_vs_selected': paired['losses']}
    groups = {'common_candidates': read_jsonl(base/'generations.jsonl'), 'common_tests': read_jsonl(base/'generated-tests.jsonl')}
    new_path = run/'new-generations.jsonl'; new = read_jsonl(new_path) if new_path.exists() else []
    for arm in config['arms']: groups[arm['method']] = [r for r in new if r['sample_index'] == arm['sample_index']]
    for name, rows in groups.items():
        cap = next((a['max_new_tokens'] for a in config['arms'] if a['method'] == name), 768)
        summary['cost'][name] = {'model_calls': len(rows), 'input_tokens': sum(r['input_tokens'] for r in rows),
            'output_tokens': sum(r['output_tokens'] for r in rows), 'wall_seconds': sum(r['wall_seconds'] for r in rows),
            'peak_allocated_bytes': max((r['peak_vram_bytes'] for r in rows), default=0),
            'capped': sum(r['output_tokens'] == cap for r in rows), 'incomplete_reasoning': sum(r.get('thinking_complete') is False for r in rows)}
    summary['limitations'] = 'One model, public benchmark, single frozen seed schedule; realized compute differs and desktop timing is uncontrolled. Primary contrast changes reasoning mode, sampling and cap jointly. No causal claim for any one factor, fixed-compute superiority, or novel algorithm.'
    write_json(run/'summary.json', summary)
    write_json(run/'task-results.json', [{'task_id': t, **{m: outcomes[m][i] for m in outcomes}} for i, t in enumerate(config['task_ids'])])
    print(json.dumps(summary, indent=2))


if __name__ == '__main__': main()

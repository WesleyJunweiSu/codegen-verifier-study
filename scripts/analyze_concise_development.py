"""Validate and report every arm of the development concise-instruction ablation."""
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifier_study.io import read_jsonl, write_json, sha256
from verifier_study.frozen_decisions import validate_decisions

RUN = 'mbpp-concise-development-20260913'


def main():
    run = ROOT/'runs'/RUN
    plan = json.loads((run/'repair-plan.json').read_text())
    for name, digest in plan['source_hashes'].items():
        assert sha256(ROOT/name) == digest, name
    score_plan = json.loads((run/'score-plan.json').read_text())
    metadata = json.loads((run/'linux/metadata.json').read_text())
    assert metadata['decision_order'] == 'Externally frozen decisions validated before reference loading; scorer never selects'
    for field, name in [('generations_sha256', 'generations.jsonl'), ('decisions_sha256', 'frozen-decisions.jsonl'), ('score_plan_sha256', 'score-plan.json')]:
        assert metadata[field] == sha256(run/name)
    assert metadata['dataset_sha256'] == score_plan['dataset_sha256']
    assert (run/'frozen-decisions.jsonl').read_bytes() == (run/'linux/decisions.jsonl').read_bytes()
    candidates = read_jsonl(run/'generations.jsonl')
    decisions = read_jsonl(run/'frozen-decisions.jsonl')
    validate_decisions(score_plan, candidates, decisions)
    key = lambda r: (r['task_id'], r['sample_index'])
    raw = read_jsonl(run/'linux/evaluation.jsonl')
    labels = {key(r): r for r in raw}
    assert len(labels) == len(raw) == len(candidates) == 46
    for r in candidates:
        assert labels[key(r)]['code_sha256'] == hashlib.sha256(r['code'].encode()).hexdigest()
    outcome = {m: {r['task_id']: labels[key(r)]['pass'] for r in decisions if r['method'] == m} for m in score_plan['methods']}
    base = outcome['selected_baseline']; control = outcome['reasoning_2048']
    assert len(base) == 40 and sum(base.values()) == 32 and sum(control.values()) == 33
    old_labels = {key(r): r['pass'] for r in read_jsonl(ROOT/'runs/mbpp-development40-repair-20260908/linux/evaluation.jsonl')}
    reused = read_jsonl(run/'reused-generations.jsonl')
    assert len(reused) == 3 and all(labels[key(r)]['pass'] == old_labels[key(r)] for r in reused)
    methods = {}
    for method, values in outcome.items():
        assert set(values) == set(base)
        rescued = [t for t in base if not base[t] and values[t]]
        regressed = [t for t in base if base[t] and not values[t]]
        methods[method] = dict(correct=sum(values.values()), tasks=40, accuracy=sum(values.values())/40,
            rescues_vs_baseline=rescued, regressions_vs_baseline=regressed,
            transition_matrix=dict(wrong_to_correct=len(rescued), correct_to_wrong=len(regressed),
                correct_to_correct=sum(base[t] and values[t] for t in base),
                wrong_to_wrong=sum(not base[t] and not values[t] for t in base)))
    cost = {}
    for arm in plan['arms']:
        rows = [r for r in candidates if r['sample_index'] == arm['sample_index']]
        assert len(rows) == 3
        cost[arm['method']] = dict(calls=3, cached=arm['sample_index'] == 7,
            output_tokens=sum(r['output_tokens'] for r in rows), wall_seconds=sum(r['wall_seconds'] for r in rows),
            incomplete=sum(not r['thinking_complete'] for r in rows), capped=sum(r['output_tokens'] == arm['max_new_tokens'] for r in rows))
    treated = outcome['reasoning_concise']
    contrast = dict(wins=[t for t in base if treated[t] and not control[t]], losses=[t for t in base if control[t] and not treated[t]],
                    difference_percentage_points=100*(sum(treated.values())-sum(control.values()))/40)
    summary = dict(scope='Adaptive development on 40 tasks with three triggers; not independent confirmation', methods=methods,
        contrast_concise_vs_original=contrast, cost=cost,
        limitations='Three triggered tasks, one seed schedule, unequal compute and uncontrolled desktop timing. Retain all failures. No general superiority or confirmatory p-value claim.',
        source_hashes={name: sha256(run/name) for name in ['repair-plan.json', 'score-plan.json', 'frozen-decisions.jsonl', 'linux/evaluation.jsonl']})
    write_json(run/'summary.json', summary)
    write_json(run/'task-results.json', [dict(task_id=t, **{m: outcome[m][t] for m in outcome}) for t in base])
    print(json.dumps(summary, indent=2))


if __name__ == '__main__': main()

"""Post-hoc development-only screening diagnostics; never alter confirmation decisions."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifier_study.io import read_jsonl, write_json, sha256


def confusion(rows, predicate):
    counts = dict(tp=0, fp=0, fn=0, tn=0)
    for row in rows:
        predicted_error = predicate(row)
        key = ('t' if row['incorrect'] else 'f') + 'p' if predicted_error else ('f' if row['incorrect'] else 't') + 'n'
        counts[key] += 1
    tp, fp, fn, tn = (counts[k] for k in ['tp', 'fp', 'fn', 'tn'])
    counts.update({'tasks': len(rows), 'flagged': tp + fp,
                   'error_recall': tp/(tp+fn) if tp+fn else None,
                   'error_precision': tp/(tp+fp) if tp+fp else None,
                   'false_positive_rate': fp/(fp+tn) if fp+tn else None,
                   'f1': 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None})
    return counts


def main():
    cohorts = [
        ('original20', 'mbpp-parser-ablation-20260905', 'mbpp-public-consensus-20260906'),
        ('additional40', 'mbpp-development40-20260907', 'mbpp-development40-public-consensus-20260908')]
    rows = []; sources = {}
    for cohort, parent_name, selected_name in cohorts:
        parent = ROOT/'runs'/parent_name; selected = ROOT/'runs'/selected_name
        decisions = read_jsonl(selected/'decisions.jsonl')
        matrix = read_jsonl(parent/'linux/candidate-test-matrix.jsonl')
        labels = {(r['task_id'], r['sample_index']): r['pass'] for r in read_jsonl(parent/'linux/evaluation.jsonl')}
        for name in [parent/'linux/candidate-test-matrix.jsonl', parent/'linux/evaluation.jsonl', selected/'decisions.jsonl']:
            sources[str(name.relative_to(ROOT))] = sha256(name)
        for decision in decisions:
            tid, index = decision['task_id'], decision['sample_index']
            subset = [r for r in matrix if (r['task_id'], r['sample_index']) == (tid, index)]
            public = [r for r in subset if r['source'] == 'public']
            generated = [r for r in subset if r['source'] == 'generated' and r['keep']]
            assert public
            rows.append({'cohort': cohort, 'task_id': tid, 'sample_index': index, 'incorrect': not labels[tid, index],
                'public_failed': any(r['status'] != 'pass' for r in public),
                'generated_failures': sum(r['status'] != 'pass' for r in generated), 'generated_tests': len(generated),
                'consensus_fraction': decision['consensus_scores'][str(index)]['fraction']})
    assert len(rows) == len({r['task_id'] for r in rows}) == 60
    rules = {'public_failure': lambda r: r['public_failed'],
             'public_or_any_generated_failure': lambda r: r['public_failed'] or r['generated_failures'] > 0,
             'public_or_consensus_disagreement': lambda r: r['public_failed'] or r['consensus_fraction'] < 1}
    summary = {'scope': 'Post-hoc development diagnostics; screening errors, not new answer accuracy or calibrated risk',
               'positive_class': 'Baseline-selected candidate is incorrect on base+plus tests', 'cohorts': {}, 'source_hashes': sources,
               'limitation': 'Expanded flags alone cannot improve public-passing cases under strict public-improvement replacement. Any tie-acceptance policy is a separate development intervention and may regress correct answers. No change to frozen confirmation.'}
    for cohort in ['original20', 'additional40', 'all60']:
        subset = rows if cohort == 'all60' else [r for r in rows if r['cohort'] == cohort]
        summary['cohorts'][cohort] = {name: confusion(subset, rule) for name, rule in rules.items()}
    out = ROOT/'runs/development-routing-diagnostic-20260911'; out.mkdir(parents=True, exist_ok=True)
    write_json(out/'summary.json', summary); write_json(out/'task-features.json', rows)
    print(json.dumps(summary['cohorts'], indent=2))


if __name__ == '__main__': main()

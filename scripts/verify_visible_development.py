"""Validate the visible-only stage against already frozen development evidence."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifier_study.io import read_jsonl, write_json, sha256


def main():
    run = ROOT/'runs/mbpp-development40-visible-20260910'
    visible = run/'visible'
    parent = ROOT/'runs/mbpp-development40-20260907'
    consensus = ROOT/'runs/mbpp-development40-consensus-20260908/linux'
    composition = ROOT/'runs/mbpp-development40-public-consensus-20260908'
    metadata = json.loads((visible/'metadata.json').read_text())
    assert metadata['kind'] == 'visible_evidence'
    assert metadata['hidden_benchmark_mounted'] is False and metadata['hidden_reference_loading'] is False
    for field, path in [('generations_sha256', parent/'generations.jsonl'), ('tests_sha256', parent/'generated-tests.jsonl'),
                        ('manifest_sha256', parent/'manifest.json'), ('matrix_sha256', visible/'candidate-test-matrix.jsonl'),
                        ('decisions_sha256', visible/'decisions.jsonl'), ('composition_decisions_sha256', visible/'composition-decisions.jsonl')]:
        assert sha256(path) == metadata[field], field
    checks = {}
    for name in ['candidate-test-matrix.jsonl', 'decisions.jsonl']:
        checks[name] = read_jsonl(visible/name) == read_jsonl(parent/'linux'/name)
    for name in ['decisions.jsonl', 'pair-outcomes.jsonl', 'execution-success.jsonl', 'inputs.jsonl']:
        checks['consensus/' + name] = read_jsonl(visible/'consensus'/name) == read_jsonl(consensus/name)
    old = read_jsonl(composition/'decisions.jsonl')
    new = read_jsonl(visible/'composition-decisions.jsonl')
    # Only the explanatory phase field changes; scores and selected IDs must agree.
    strip_phase = lambda rows: [{k: v for k, v in r.items() if k != 'phase'} for r in rows]
    checks['composition_decisions_excluding_phase'] = strip_phase(old) == strip_phase(new)
    summary = {'scope': 'Engineering boundary validation on 40 previously scored development tasks, not new accuracy evidence',
               'tasks': metadata['tasks'], 'candidates': metadata['candidates'], 'exact_record_checks': checks,
               'all_equal': all(checks.values()), 'hidden_labels_read_by_this_comparison': False}
    write_json(run/'verification.json', summary)
    assert summary['all_equal'], 'Visible-stage execution changed; inspect before confirming the boundary validation'
    print(json.dumps(summary, indent=2))


if __name__ == '__main__': main()

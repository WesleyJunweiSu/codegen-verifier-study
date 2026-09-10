"""Persist all selection evidence inside Linux without loading benchmark references."""
import argparse
import hashlib
import json
import os
import platform
import sys
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--parent-run', required=True)
    args = parser.parse_args()
    if platform.system() != 'Linux' or os.environ.get('VERIFIER_ISOLATED_RUN') != '1':
        raise SystemExit('Restricted Linux container required; host execution disabled.')
    source = Path(args.input); out = Path(args.output); out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((source/'manifest.json').read_text())
    task_ids = manifest['task_ids']
    assert len(task_ids) == len(set(task_ids)), 'Duplicate expected tasks'
    records = [json.loads(line) for line in (source/'generations.jsonl').read_text().splitlines() if line]
    keys = {(r['task_id'], r['sample_index']) for r in records}
    assert len(keys) == len(records)
    plan_path = source/'repair-plan.json'
    if plan_path.exists():
        plan = json.loads(plan_path.read_text())
        assert len(plan['tasks']) == len(task_ids) and {t['task_id'] for t in plan['tasks']} == set(task_ids)
        expected = {(t['task_id'], t['selected_index']) for t in plan['tasks']}
        expected |= {(t['task_id'], a['sample_index']) for t in plan['tasks'] if t['triggered'] for a in plan['arms']}
    else:
        expected = {(t, i) for t in task_ids for i in range(4)}
    assert keys == expected, 'Incomplete/unexpected candidate keys'
    from test_matrix_linux import build_matrix
    build_matrix(records, source/'generated-tests.jsonl', out)
    if not plan_path.exists():
        # Reuse the existing consensus algorithm and source seed unchanged.
        from consensus_linux import main as consensus_main
        sys.argv = ['consensus_linux.py', '--input', str(source), '--output', str(out/'consensus'), '--parent-run', args.parent_run]
        consensus_main()
        from combine_public_consensus import select
        public = [json.loads(line) for line in (out/'candidate-test-matrix.jsonl').read_text().splitlines()]
        public = [r for r in public if r['source'] == 'public']
        consensus = [json.loads(line) for line in (out/'consensus/decisions.jsonl').read_text().splitlines()]
        combined = select(public, consensus)
        assert len(combined) == len(task_ids) and {r['task_id'] for r in combined} == set(task_ids)
        for row in combined:
            row['phase'] = 'Frozen composition in visible-only stage; no hidden dataset mounted'
        (out/'composition-decisions.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in combined))
    decisions_path = out/'decisions.jsonl'
    metadata = {'kind': 'visible_evidence', 'parent_run': args.parent_run, 'tasks': len(task_ids), 'candidates': len(records),
        'hidden_benchmark_mounted': False, 'hidden_reference_loading': False,
        'generations_sha256': digest(source/'generations.jsonl'), 'tests_sha256': digest(source/'generated-tests.jsonl'),
        'manifest_sha256': digest(source/'manifest.json'), 'decisions_sha256': digest(decisions_path),
        'matrix_sha256': digest(out/'candidate-test-matrix.jsonl'), 'source_sha256': digest(Path(__file__))}
    if (out/'composition-decisions.jsonl').exists():
        metadata['composition_decisions_sha256'] = digest(out/'composition-decisions.jsonl')
    if plan_path.exists(): metadata['repair_plan_sha256'] = digest(plan_path)
    (out/'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(metadata), flush=True)


if __name__ == '__main__': main()

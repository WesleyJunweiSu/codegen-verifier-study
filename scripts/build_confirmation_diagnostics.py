"""Post-confirmation diagnostics; never selects a new confirmation policy."""
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifier_study.io import read_jsonl, write_json, sha256
from confirmation import load_config


def main():
    config, digest = load_config()
    run = ROOT/'runs'/config['extension_run']
    metadata = json.loads((run/'linux/metadata.json').read_text())
    for field, name in [('generations_sha256', 'generations.jsonl'), ('decisions_sha256', 'frozen-decisions.jsonl'), ('score_plan_sha256', 'score-plan.json')]:
        assert metadata[field] == sha256(run/name)
    assert (run/'frozen-decisions.jsonl').read_bytes() == (run/'linux/decisions.jsonl').read_bytes()
    summary = json.loads((run/'summary.json').read_text())
    assert summary['protocol_sha256'] == digest
    records = read_jsonl(run/'generations.jsonl')
    labels = read_jsonl(run/'linux/evaluation.jsonl')
    key = lambda r: (r['task_id'], r['sample_index'])
    labels = {key(r): r for r in labels}
    assert len(labels) == len(records)
    for row in records:
        assert labels[key(row)]['code_sha256'] == hashlib.sha256(row['code'].encode()).hexdigest()
    decisions = {(r['task_id'], r['method']): r['sample_index'] for r in read_jsonl(run/'frozen-decisions.jsonl')}
    tasks = json.loads((run/'repair-plan.json').read_text())['tasks']
    detection = dict(tp=0, fp=0, fn=0, tn=0)
    transitions = {m: dict(wrong_to_correct=0, correct_to_wrong=0, correct_to_correct=0, wrong_to_wrong=0)
                   for m in config['reported_methods']}
    for task in tasks:
        tid = task['task_id']; base = labels[tid, decisions[tid, 'selected_baseline']]['pass']
        detection[('fp' if base else 'tp') if task['triggered'] else ('tn' if base else 'fn')] += 1
        for method, matrix in transitions.items():
            passed = labels[tid, decisions[tid, method]]['pass']
            matrix[('correct' if base else 'wrong')+'_to_'+('correct' if passed else 'wrong')] += 1
    detection['error_recall'] = detection['tp']/(detection['tp']+detection['fn'])
    detection['error_precision'] = detection['tp']/(detection['tp']+detection['fp'])
    sources = ['linux/evaluation.jsonl', 'frozen-decisions.jsonl', 'repair-plan.json', 'summary.json']
    write_json(run/'postconfirmation-diagnostics.json', dict(scope='Post-confirmation descriptive diagnostics; no policy selection or refitting',
        source_hashes={name: sha256(run/name) for name in sources}, detection=detection, transitions=transitions))
    print(json.dumps(dict(detection=detection, transitions=transitions), indent=2))


if __name__ == '__main__': main()

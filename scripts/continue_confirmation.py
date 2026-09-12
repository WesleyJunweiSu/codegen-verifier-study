"""Continue the frozen confirmation after the existing GPU queue; no protocol changes.

Run with --execute. The default validates configuration and reports state only.
Each Actions dispatch is journaled before sending; uncertain dispatches are never
automatically repeated. This script never opens intermediate correctness labels.
"""
import argparse
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifier_study.io import read_jsonl, write_json
from confirmation import load_config

JOURNAL = ROOT/'runs/confirmation-continuation-20260912/state.json'
MODEL = 'C:/Users/Asuka/Documents/techblog/models/Qwen3-4B'
ROUTING = ROOT/'runs/mbpp-routing-v2-development-20260911'


def command(args, capture=False):
    result = subprocess.run(args, cwd=ROOT, check=True, text=True, encoding='utf-8',
                            stdout=subprocess.PIPE if capture else None)
    return result.stdout.strip() if capture else None


def python(script, *args, capture=False):
    return command([sys.executable, '-X', 'utf8', 'scripts/'+script, *args], capture)


def git(*args):
    return command(['git', '-c', 'safe.directory='+ROOT.as_posix(), *args], capture=True)


def api(operation, *args):
    return json.loads(python('github_ops.py', operation, *args, capture=True))


def checkpoint(state, stage):
    state.update(stage=stage, updated_utc=datetime.datetime.now(datetime.UTC).isoformat())
    write_json(JOURNAL, state)
    print(stage, flush=True)


def commit(paths, message):
    assert not git('diff', '--cached', '--name-only'), 'Unrelated staged changes; stop before committing'
    git('add', '--', *paths)
    if git('diff', '--cached', '--name-only'):
        git('commit', '-m', message)
    git('push', 'origin', 'HEAD:main')
    return git('rev-parse', 'HEAD')


def workflow(state, key, workflow_name, run_name, artifact_name, target, source_commit):
    jobs = state.setdefault('jobs', {})
    if key not in jobs:
        jobs[key] = dict(source_commit=source_commit, dispatch_pending=True)
        checkpoint(state, key+'_dispatch_pending')
        # github_ops prints a Python dict on dispatch, unlike its JSON read commands.
        python('github_ops.py', 'dispatch', '--workflow', workflow_name, '--input-run', run_name)
    job = jobs[key]
    if 'run_id' not in job:
        for _ in range(12):
            matches = [r for r in api('runs') if r['head_sha'] == job['source_commit']]
            if len(matches) == 1:
                job['run_id'] = str(matches[0]['id'])
                checkpoint(state, key+'_running')
                break
            assert len(matches) < 2, 'Ambiguous workflow identity; inspect before proceeding'
            time.sleep(10)
        assert 'run_id' in job, 'Dispatch uncertain; inspect GitHub before retrying'
    # Inspect only job status, not logs or intermediate scoring artifacts.
    for _ in range(240):
        jobs_status = api('jobs', '--run-id', job['run_id'])
        if jobs_status and all(j['conclusion'] is not None for j in jobs_status):
            assert all(j['conclusion'] == 'success' for j in jobs_status), 'Workflow did not succeed'
            break
        time.sleep(15)
    else:
        raise TimeoutError('Workflow still running; resume with its recorded run id')
    artifacts = api('artifacts', '--run-id', job['run_id'])
    matching = [a for a in artifacts if a['name'] == artifact_name and not a['expired']]
    assert len(matching) == 1
    archive = ROOT.parent/'tmp'/('confirmation-'+key+'.zip')
    python('github_ops.py', 'download', '--artifact-id', str(matching[0]['id']), '--output', str(archive))
    if target.exists():
        provenance = json.loads((target/'workflow.json').read_text())
        assert str(provenance['workflow_id']) == job['run_id'] and provenance['source_commit'] == job['source_commit']
    else:
        python('import_artifact.py', str(archive), str(target), '--workflow-id', job['run_id'], '--commit', job['source_commit'])
    checkpoint(state, key+'_imported')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    config, digest = load_config()
    state = json.loads(JOURNAL.read_text()) if JOURNAL.exists() else dict(protocol_sha256=digest, jobs={})
    assert state['protocol_sha256'] == digest
    if not args.execute:
        print(json.dumps(state, indent=2)); return
    if state.get('stage') == 'complete':
        print('Already complete; no repeated experiments.'); return
    try:
        checkpoint(state, 'waiting_for_existing_routing_queue')
        for _ in range(2880):
            queue = json.loads((ROUTING/'queue-state.json').read_text(encoding='utf-8-sig'))
            if queue['status'] == 'scoring_dispatched_import_artifacts_next': break
            assert queue['status'] not in ['stopped_check_log_before_retry', 'deferred_gpu_headroom'], 'Existing GPU queue stopped; inspect it first'
            time.sleep(15)
        else:
            raise TimeoutError('Existing GPU queue has not finished')
        base = ROOT/'runs'/config['base_run']; extension = ROOT/'runs'/config['extension_run']
        rows, tests = read_jsonl(base/'generations.jsonl'), read_jsonl(base/'generated-tests.jsonl')
        assert len(rows) == 720 and {(r['task_id'], r['sample_index']) for r in rows} == {(t, i) for t in config['task_ids'] for i in range(4)}
        assert len(tests) == 180 and {r['task_id'] for r in tests} == set(config['task_ids'])
        source = commit([str(base.relative_to(ROOT))], 'Record complete 180-task confirmation baseline inputs')
        workflow(state, 'base_visible', 'visible-evidence.yml', config['base_run'], 'visible-evidence', base/'visible', source)
        checkpoint(state, 'preparing_frozen_confirmation_extensions')
        python('confirmation.py', 'prepare-extension')
        checkpoint(state, 'generating_frozen_confirmation_extensions')
        python('confirmation.py', 'extension', '--model-path', MODEL)
        assert (extension/'generations.jsonl').exists(), 'Extension generation deferred; resume when GPU is available'
        source = commit([str(base.relative_to(ROOT)), str(extension.relative_to(ROOT))], 'Record frozen confirmation extension inputs')
        workflow(state, 'extension_visible', 'visible-evidence.yml', config['extension_run'], 'visible-evidence', extension/'visible', source)
        python('freeze_score_inputs.py', '--run', config['extension_run'])
        source = commit([str(extension.relative_to(ROOT))], 'Freeze all confirmation decisions before hidden scoring')
        workflow(state, 'final_score', 'score-frozen.yml', config['extension_run'], 'frozen-scoring', extension/'linux', source)
        checkpoint(state, 'analyzing_complete_confirmation')
        python('analyze_confirmation.py')
        commit([str(extension.relative_to(ROOT))], 'Record prespecified confirmation results and paired analysis')
        checkpoint(state, 'complete')
    except Exception as error:
        state['failure_type'] = type(error).__name__
        state['failure_message'] = str(error)
        checkpoint(state, 'stopped_inspect_before_resume')
        raise


if __name__ == '__main__': main()

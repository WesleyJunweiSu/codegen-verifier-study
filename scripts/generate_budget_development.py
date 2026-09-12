"""Generate a development-only token-cap ablation, reusing the fixed 2048 control."""
import argparse
import datetime
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifier_study.io import read_jsonl, write_json, write_jsonl, append_jsonl, sha256
from verifier_study.generation import SYSTEM_PROMPT, build_prompt
from verifier_study.test_quality import public_assertions


def frozen_json(path, value):
    if path.exists():
        assert json.loads(path.read_text(encoding='utf-8')) == value, f'Frozen input changed: {path.name}'
    else:
        write_json(path, value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-path')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    config_path = ROOT/'configs/development-budget.json'
    config = json.loads(config_path.read_text(encoding='utf-8'))
    parent = ROOT/'runs'/config['parent_run']
    composition = ROOT/'runs/mbpp-development40-public-consensus-20260908'
    out = ROOT/'runs'/config['run_id']; out.mkdir(parents=True, exist_ok=True)
    cohort = json.loads((parent/'manifest.json').read_text(encoding='utf-8'))
    selected = read_jsonl(composition/'decisions.jsonl')
    assert len(selected) == 40 and {r['task_id'] for r in selected} == set(cohort['task_ids'])
    composition_manifest = json.loads((composition/'manifest.json').read_text(encoding='utf-8'))
    assert sha256(composition/'decisions.jsonl') == composition_manifest['decisions_sha256']
    assert composition_manifest['parent_run'] == parent.name
    matrix_path = parent/'linux/candidate-test-matrix.jsonl'
    assert sha256(matrix_path) == composition_manifest['public_matrix_sha256']
    public = [r for r in read_jsonl(matrix_path) if r['source'] == 'public']
    visible_path = ROOT/'data/prompts/mbpp-v0.2.0.jsonl'
    visible = {r['task_id']: r for r in read_jsonl(visible_path)}
    pool = {(r['task_id'], r['sample_index']): r for r in read_jsonl(parent/'generations.jsonl')}
    tasks = []; base = []
    for row in selected:
        tid, index = row['task_id'], row['sample_index']
        statuses = [r for r in public if (r['task_id'], r['sample_index']) == (tid, index)]
        assertions = public_assertions(visible[tid]['prompt'])
        assert len(statuses) == len(assertions) and {r['test_index'] for r in statuses} == set(range(len(assertions)))
        assert assertions, 'Task has no public example'
        failures = [assertions[r['test_index']] for r in statuses if r['status'] != 'pass']
        tasks.append({'task_id': tid, 'selected_index': index, 'triggered': bool(failures), 'failed_public_assertions': failures})
        base.append(pool[tid, index])
    old_plan_path = ROOT/'runs/mbpp-repair-20260907/repair-plan.json'
    instruction = json.loads(old_plan_path.read_text(encoding='utf-8'))['repair_instruction']
    sources = [config_path, composition/'decisions.jsonl', matrix_path, visible_path, parent/'generations.jsonl', old_plan_path,
               Path(__file__), ROOT/'runs/mbpp-development40-repair-20260908/new-generations.jsonl', ROOT/'src/verifier_study/transfer.py', ROOT/'src/verifier_study/generation.py', ROOT/'src/verifier_study/reasoning_generation.py']
    plan = {**config, 'tasks': tasks, 'repair_instruction': instruction,
            'source_hashes': {str(p.relative_to(ROOT)): sha256(p) for p in sources}}
    frozen_json(out/'repair-plan.json', plan)
    test_raw = (parent/'generated-tests.jsonl').read_bytes()
    if (out/'generated-tests.jsonl').exists(): assert (out/'generated-tests.jsonl').read_bytes() == test_raw
    else: (out/'generated-tests.jsonl').write_bytes(test_raw)
    frozen_json(out/'test-manifest.json', {'parent_run': parent.name, 'test_generation_reused': True,
                'new_test_model_calls': 0, 'tests_sha256': sha256(parent/'generated-tests.jsonl')})
    records_path = out/'new-generations.jsonl'
    reused = [r for r in read_jsonl(ROOT/'runs/mbpp-development40-repair-20260908/new-generations.jsonl') if r['sample_index'] == 7]
    assert len(reused) == 3 and {r['task_id'] for r in reused} == {t['task_id'] for t in tasks if t['triggered']}
    for row in reused:
        assert row['seed'] == int(hashlib.sha256(f'transfer:20260908:{row["task_id"]}'.encode()).hexdigest()[:8], 16)
        assert row['output_tokens'] <= 2048
    reused_path = out/'reused-generations.jsonl'
    if reused_path.exists(): assert read_jsonl(reused_path) == reused
    else: write_jsonl(reused_path, reused)
    records = reused + (read_jsonl(records_path) if records_path.exists() else [])
    done = {(r['task_id'], r['sample_index']) for r in records}
    expected = {(t['task_id'], a['sample_index']) for t in tasks if t['triggered'] for a in config['arms']}
    assert len(done) == len(records) and done <= expected
    print(json.dumps({'tasks': len(tasks), 'triggered': sum(t['triggered'] for t in tasks), 'new_calls': len(expected)-len(reused), 'reused_calls': len(reused), 'completed': len(done)}), flush=True)
    if args.prepare_only: return
    if done != expected:
        assert args.model_path
        packages = json.loads((ROOT/'runs/mbpp-development40-repair-20260908/manifest.json').read_text())['packages']
        assert {n: importlib.metadata.version(n) for n in packages} == packages
        free = int(subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'], text=True).splitlines()[0])
        append_jsonl(out/'attempts.jsonl', {'utc': datetime.datetime.now(datetime.UTC).isoformat(), 'free_mib': free,
                     'status': 'ready' if free >= 9216 else 'deferred_insufficient_vram', 'completed': len(done), 'planned': len(expected)})
        if free < 9216: return
        fingerprint_path = ROOT/'configs/model-fingerprint.json'
        for item in json.loads(fingerprint_path.read_text(encoding='utf-8'))['files']:
            assert sha256(Path(args.model_path)/item['file']) == item['sha256']
        manifest = {'task_ids': cohort['task_ids'], 'plan_sha256': sha256(out/'repair-plan.json'),
                    'model_fingerprint_sha256': sha256(fingerprint_path), 'generator_script_sha256': sha256(Path(__file__)),
                    'packages': {n: importlib.metadata.version(n) for n in ['torch', 'transformers', 'accelerate', 'tokenizers']}}
        frozen_json(out/'manifest.json', manifest)
        os.environ['HF_HUB_OFFLINE'] = '1'; os.environ['TRANSFORMERS_OFFLINE'] = '1'
        from verifier_study.reasoning_generation import ReasoningLM
        model = ReasoningLM(args.model_path, 'Qwen/Qwen3-4B')
        for task in tasks:
            if not task['triggered']: continue
            tid = task['task_id']; prompt = visible[tid]['prompt']
            seed = int(hashlib.sha256(f'transfer:20260908:{tid}'.encode()).hexdigest()[:8], 16)
            for arm in config['arms']:
                index = arm['sample_index']
                if (tid, index) in done: continue
                messages = build_prompt(prompt)
                if arm['feedback']:
                    content = (instruction + '\nSPECIFICATION:\n' + prompt + '\nIMPLEMENTATION:\n' + pool[tid, task['selected_index']]['code']
                               + '\nFAILED PUBLIC ASSERTIONS:\n' + '\n'.join(task['failed_public_assertions']))
                    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}, {'role': 'user', 'content': content}]
                common = dict(task_id=tid, messages=messages, sample_index=index, seed=seed, generation_kind=arm['method'], max_new_tokens=arm['max_new_tokens'])
                if arm['thinking']:
                    assert (arm['temperature'], arm['top_p'], arm['top_k']) == (0.6, 0.95, 20)
                    record = model.generate_reasoning(**common)
                else:
                    assert arm['top_k'] == 20
                    record = model._generate_messages(**common, temperature=arm['temperature'], top_p=arm['top_p']).to_dict()
                control = next(r for r in reused if r['task_id'] == tid)
                assert record['prompt_sha256'] == control['prompt_sha256'] and record['rendered_prompt_sha256'] == control['rendered_prompt_sha256']
                append_jsonl(records_path, record); records.append(record); done.add((tid, index))
                write_json(out/'progress.json', {'completed': len(done), 'planned': len(expected), 'triggered_tasks': sum(t['triggered'] for t in tasks),
                    'status': 'generation_complete' if done == expected else 'running',
                    'output_tokens': sum(r['output_tokens'] for r in records), 'generation_seconds': sum(r['wall_seconds'] for r in records)})
                print(f'{len(done)}/{len(expected)} {tid} {arm["method"]} tokens={record["output_tokens"]}', flush=True)
    assert done == expected
    write_jsonl(out/'generations.jsonl', base + records)


if __name__ == '__main__': main()

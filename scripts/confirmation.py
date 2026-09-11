"""Frozen confirmation generation and public-only extension preparation. Never reads labels."""
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
from verifier_study.generation import build_prompt
from verifier_study.test_quality import public_assertions, assess_tests
from generate_tests import SYSTEM
from generate_development import normalize


def frozen(path, value):
    if path.exists(): assert json.loads(path.read_text(encoding='utf-8')) == value, str(path)
    else: write_json(path, value)


def load_config():
    path = ROOT/'configs/confirmation-protocol.json'
    config = json.loads(path.read_text(encoding='utf-8'))
    for name, expected in config['source_hashes'].items(): assert sha256(ROOT/name) == expected, name
    split = json.loads((ROOT/'configs/split-manifest.json').read_text())
    assert config['task_ids'] == split['confirmation'] and len(config['task_ids']) == 180
    assert not set(config['task_ids']) & set(split['development'] + split['calibration'] + split['reserve'])
    return config, sha256(path)


def model_for(args, out):
    expected_packages = json.loads((ROOT/'configs/confirmation-protocol.json').read_text())['runtime_packages']
    assert {n: importlib.metadata.version(n) for n in expected_packages} == expected_packages, 'Runtime packages changed'
    free = int(subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'], text=True).splitlines()[0])
    append_jsonl(out/'attempts.jsonl', {'utc': datetime.datetime.now(datetime.UTC).isoformat(), 'free_mib': free,
                'status': 'check_only' if args.check_only else ('ready' if free >= 9216 else 'deferred_insufficient_vram')})
    if args.check_only or free < 9216:
        print('Model not loaded; free MiB:', free, flush=True); return None
    assert args.model_path
    fingerprint = json.loads((ROOT/'configs/model-fingerprint.json').read_text())
    for row in fingerprint['files']: assert sha256(Path(args.model_path)/row['file']) == row['sha256']
    os.environ['HF_HUB_OFFLINE'] = '1'; os.environ['TRANSFORMERS_OFFLINE'] = '1'
    from verifier_study.reasoning_generation import ReasoningLM
    return ReasoningLM(args.model_path, 'Qwen/Qwen3-4B')


def generate_base(config, digest, args):
    out = ROOT/'runs'/config['base_run']; out.mkdir(parents=True, exist_ok=True)
    frozen(out/'manifest.json', {'task_ids': config['task_ids'], 'confirmation_protocol_sha256': digest,
        'phase': 'Confirmation baseline inputs; no correctness labels permitted before final decisions',
        'packages': {n: importlib.metadata.version(n) for n in ['torch', 'transformers', 'accelerate', 'tokenizers']}})
    frozen(out/'test-manifest.json', {'candidate_generation_reused': False, 'test_generation_reused': False,
        'system_prompt': SYSTEM, 'generation_manifest_sha256': sha256(out/'manifest.json'),
        'temperature': 0.7, 'top_p': 0.8, 'top_k': 20, 'max_new_tokens': 768, 'hidden_tests_visible': False})
    gp, tp = out/'generations.jsonl', out/'generated-tests.jsonl'
    records = read_jsonl(gp) if gp.exists() else []; tests = read_jsonl(tp) if tp.exists() else []
    done = {(r['task_id'], r['sample_index']) for r in records}; tested = {r['task_id'] for r in tests}
    expected = {(t, i) for t in config['task_ids'] for i in range(4)}
    assert len(done) == len(records) and done <= expected
    assert len(tested) == len(tests) and tested <= set(config['task_ids'])
    print(f'Confirmation candidates {len(done)}/720; test responses {len(tested)}/180', flush=True)
    if done == expected and tested == set(config['task_ids']): return
    model = model_for(args, out)
    if model is None: return
    visible = {r['task_id']: r for r in read_jsonl(ROOT/'data/prompts/mbpp-v0.2.0.jsonl')}
    for tid in config['task_ids']:
        task = visible[tid]
        for index in range(4):
            if (tid, index) in done: continue
            seed = int(hashlib.sha256(f'20260905:{tid}:{index}'.encode()).hexdigest()[:8], 16)
            row = model.generate(task_id=tid, function_prompt=task['prompt'], sample_index=index, seed=seed,
                                 max_new_tokens=768, temperature=0.7, top_p=0.8).to_dict()
            append_jsonl(gp, row); records.append(row); done.add((tid, index))
        if tid not in tested:
            seed = int(hashlib.sha256(f'test:20260905:{tid}'.encode()).hexdigest()[:8], 16)
            messages = [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': task['prompt'] + '\nFunction name: ' + task['entry_point']}]
            row = model._generate_messages(task_id=tid, messages=messages, sample_index=0, seed=seed,
                       generation_kind='spec_tests', max_new_tokens=768, temperature=0.7, top_p=0.8).to_dict()
            assertions, errors, strict, count = normalize(row['raw_output'])
            row.update({'parse_errors': errors, 'strict_parse_errors': strict, 'converted_comparisons': count,
                        'tests': assess_tests(assertions, task['prompt'], task['entry_point'])})
            append_jsonl(tp, row); tests.append(row); tested.add(tid)
        write_json(out/'progress.json', {'status': 'generation_complete' if len(done) == 720 and len(tested) == 180 else 'running',
            'candidate_count': len(done), 'test_responses': len(tested), 'output_tokens': sum(r['output_tokens'] for r in records + tests),
            'generation_seconds': sum(r['wall_seconds'] for r in records + tests)})
        print(f'{tid}: candidates {len(done)}/720, test responses {len(tested)}/180', flush=True)


def prepare_extension(config, digest):
    parent = ROOT/'runs'/config['base_run']; out = ROOT/'runs'/config['extension_run']; out.mkdir(parents=True, exist_ok=True)
    metadata = json.loads((parent/'visible/metadata.json').read_text())
    assert metadata['hidden_benchmark_mounted'] is False and metadata['hidden_reference_loading'] is False
    for field, name in [('generations_sha256', 'generations.jsonl'), ('tests_sha256', 'generated-tests.jsonl'),
                        ('composition_decisions_sha256', 'visible/composition-decisions.jsonl'), ('matrix_sha256', 'visible/candidate-test-matrix.jsonl')]:
        assert sha256(parent/name) == metadata[field], field
    selected = read_jsonl(parent/'visible/composition-decisions.jsonl')
    assert len(selected) == 180 and {r['task_id'] for r in selected} == set(config['task_ids'])
    public = [r for r in read_jsonl(parent/'visible/candidate-test-matrix.jsonl') if r['source'] == 'public']
    prompts = {r['task_id']: r for r in read_jsonl(ROOT/'data/prompts/mbpp-v0.2.0.jsonl')}
    tasks = []
    for decision in selected:
        tid, index = decision['task_id'], decision['sample_index']
        statuses = [r for r in public if (r['task_id'], r['sample_index']) == (tid, index)]
        assertions = public_assertions(prompts[tid]['prompt'])
        assert assertions and len(statuses) == len(assertions) and {r['test_index'] for r in statuses} == set(range(len(assertions)))
        failed = [assertions[r['test_index']] for r in statuses if r['status'] != 'pass']
        tasks.append({'task_id': tid, 'selected_index': index, 'triggered': bool(failed), 'failed_public_assertions': failed})
    plan = {'phase': 'Confirmation; no label inspection before all final decisions frozen', 'parent_run': parent.name,
        'confirmation_protocol_sha256': digest, 'tasks': tasks, 'arms': config['arms'],
        'base_candidate_mode': 'all_four', 'include_first_baseline': True,
        'visible_metadata_sha256': sha256(parent/'visible/metadata.json'), 'generations_sha256': sha256(parent/'generations.jsonl')}
    frozen(out/'repair-plan.json', plan)
    frozen(out/'manifest.json', {'task_ids': config['task_ids'], 'confirmation_protocol_sha256': digest, 'plan_sha256': sha256(out/'repair-plan.json')})
    raw = (parent/'generated-tests.jsonl').read_bytes()
    if (out/'generated-tests.jsonl').exists(): assert (out/'generated-tests.jsonl').read_bytes() == raw
    else: (out/'generated-tests.jsonl').write_bytes(raw)
    frozen(out/'test-manifest.json', {'parent_run': parent.name, 'test_generation_reused': True, 'new_test_model_calls': 0})
    print('Frozen public-only triggers:', sum(t['triggered'] for t in tasks), flush=True)
    return out, plan, prompts


def generate_extension(config, digest, args):
    out, plan, prompts = prepare_extension(config, digest)
    path = out/'new-generations.jsonl'
    records = read_jsonl(path) if path.exists() else []
    done = {(r['task_id'], r['sample_index']) for r in records}
    expected = {(t['task_id'], a['sample_index']) for t in plan['tasks'] if t['triggered'] for a in plan['arms']}
    assert len(done) == len(records) and done <= expected
    if done != expected:
        model = model_for(args, out)
        if model is None: return
        for task in plan['tasks']:
            if not task['triggered']: continue
            tid = task['task_id']; messages = build_prompt(prompts[tid]['prompt'])
            seed = int(hashlib.sha256(f'confirmation:20260911:extension:{tid}'.encode()).hexdigest()[:8], 16)
            for arm in plan['arms']:
                index = arm['sample_index']
                if (tid, index) in done: continue
                common = dict(task_id=tid, messages=messages, sample_index=index, seed=seed, generation_kind=arm['method'], max_new_tokens=arm['max_new_tokens'])
                if arm['thinking']: row = model.generate_reasoning(**common)
                else: row = model._generate_messages(**common, temperature=0.7, top_p=0.8).to_dict()
                append_jsonl(path, row); records.append(row); done.add((tid, index))
                write_json(out/'progress.json', {'completed': len(done), 'planned': len(expected),
                    'status': 'generation_complete' if done == expected else 'running',
                    'output_tokens': sum(r['output_tokens'] for r in records), 'generation_seconds': sum(r['wall_seconds'] for r in records)})
                print(f'{len(done)}/{len(expected)} {tid} {arm["method"]}', flush=True)
    assert done == expected
    original = read_jsonl(ROOT/'runs'/config['base_run']/'generations.jsonl')
    assert len(original) == 720
    write_jsonl(out/'generations.jsonl', original + records)
    if not expected: write_json(out/'progress.json', {'completed': 0, 'planned': 0, 'status': 'generation_complete'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['base', 'prepare-extension', 'extension'])
    parser.add_argument('--model-path')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    config, digest = load_config()
    if args.stage == 'base': generate_base(config, digest, args)
    elif args.stage == 'prepare-extension': prepare_extension(config, digest)
    else: generate_extension(config, digest, args)


if __name__ == '__main__': main()

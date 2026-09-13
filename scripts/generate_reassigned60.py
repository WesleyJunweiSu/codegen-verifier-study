"""Resume the previously frozen 60-task development cohort with one model load."""
import argparse
import ast
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifier_study.io import read_jsonl, write_json, append_jsonl, sha256
from verifier_study.test_quality import assess_tests, parse_assertions
from generate_tests import SYSTEM


def normalize(raw):
    assertions, strict_errors = parse_assertions(raw)
    try:
        tree = ast.parse(raw)
    except (SyntaxError, ValueError):
        return assertions, strict_errors, strict_errors, 0
    assertions = []; errors = []; count = 0
    for node in tree.body:
        if isinstance(node, ast.Assert): assertions.append(ast.unparse(node))
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Compare):
            assertions.append('assert ' + ast.unparse(node.value)); count += 1
        else: errors.append('non_assert_statement:' + type(node).__name__)
    return assertions, errors, strict_errors, count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-path', required=True)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    config_path = ROOT/'configs/development-reassigned60.json'
    config = json.loads(config_path.read_text(encoding='utf-8'))
    split_path = ROOT/'configs/split-manifest-v2.json'
    assert sha256(split_path) == config['split_manifest_sha256']
    out = ROOT/'runs'/config['run_id']; out.mkdir(parents=True, exist_ok=True)
    manifest = {**config, 'config_sha256': sha256(config_path),
          'generation_source_sha256': sha256(ROOT/'src/verifier_study/generation.py'),
          'generator_script_sha256': sha256(Path(__file__)),
          'model_fingerprint_sha256': sha256(ROOT/'configs/model-fingerprint.json'),
          'packages': {n: importlib.metadata.version(n) for n in ['torch', 'transformers', 'accelerate', 'tokenizers']}}
    if (out/'manifest.json').exists(): assert json.loads((out/'manifest.json').read_text(encoding='utf-8')) == manifest
    else: write_json(out/'manifest.json', manifest)
    test_manifest = {'system_prompt': SYSTEM, 'candidate_generation_reused': False, 'test_generation_reused': False,
          'normalization': 'Existing AST comparison-to-assert conversion; strict errors and raw responses retained; malformed text retained as failure',
          'candidates_visible': False, 'hidden_tests_visible': False, 'temperature': 0.7, 'top_p': 0.8, 'max_new_tokens': 768,
          'quality_code_sha256': sha256(ROOT/'src/verifier_study/test_quality.py'), 'generation_manifest_sha256': sha256(out/'manifest.json')}
    if (out/'test-manifest.json').exists(): assert json.loads((out/'test-manifest.json').read_text(encoding='utf-8')) == test_manifest
    else: write_json(out/'test-manifest.json', test_manifest)
    gp = out/'generations.jsonl'; tp = out/'generated-tests.jsonl'
    records = read_jsonl(gp) if gp.exists() else []; tests = read_jsonl(tp) if tp.exists() else []
    done = {(r['task_id'], r['sample_index']) for r in records}; test_done = {r['task_id'] for r in tests}
    expected = {(t, i) for t in config['task_ids'] for i in range(4)}
    assert len(done) == len(records) and done <= expected
    assert len(test_done) == len(tests) and test_done <= set(config['task_ids'])
    print(f'Candidates {len(done)}/240; test responses {len(test_done)}/60', flush=True)
    if done == expected and test_done == set(config['task_ids']): return
    free = int(subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'], text=True).splitlines()[0])
    if args.check_only or free < config['gpu_minimum_free_mib']:
        print('Headroom MiB:', free, '; model not loaded', flush=True); return
    for item in json.loads((ROOT/'configs/model-fingerprint.json').read_text(encoding='utf-8'))['files']:
        assert sha256(Path(args.model_path)/item['file']) == item['sha256']
    visible = {r['task_id']: r for r in read_jsonl(ROOT/'data/prompts/mbpp-v0.2.0.jsonl')}
    os.environ['HF_HUB_OFFLINE'] = '1'; os.environ['TRANSFORMERS_OFFLINE'] = '1'
    from verifier_study.generation import LocalCausalLM
    model = LocalCausalLM(args.model_path, 'Qwen/Qwen3-4B')
    for tid in config['task_ids']:
        task = visible[tid]
        for index in range(4):
            if (tid, index) in done: continue
            seed = int(hashlib.sha256(f'20260905:{tid}:{index}'.encode()).hexdigest()[:8], 16)
            record = model.generate(task_id=tid, function_prompt=task['prompt'], sample_index=index, seed=seed,
                         max_new_tokens=768, temperature=0.7, top_p=0.8).to_dict()
            append_jsonl(gp, record); records.append(record); done.add((tid, index))
        if tid not in test_done:
            seed = int(hashlib.sha256(f'test:20260905:{tid}'.encode()).hexdigest()[:8], 16)
            messages = [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': task['prompt'] + '\nFunction name: ' + task['entry_point']}]
            record = model._generate_messages(task_id=tid, messages=messages, sample_index=0, seed=seed,
                generation_kind='spec_tests', max_new_tokens=768, temperature=0.7, top_p=0.8).to_dict()
            assertions, errors, strict, count = normalize(record['raw_output'])
            record.update({'parse_errors': errors, 'strict_parse_errors': strict, 'converted_comparisons': count,
                           'tests': assess_tests(assertions, task['prompt'], task['entry_point'])})
            append_jsonl(tp, record); tests.append(record); test_done.add(tid)
        write_json(out/'progress.json', {'status': 'generation_complete' if len(done) == 240 and len(test_done) == 60 else 'running',
            'candidate_count': len(done), 'test_responses': len(test_done),
            'output_tokens': sum(r['output_tokens'] for r in records + tests),
            'generation_seconds': sum(r['wall_seconds'] for r in records + tests)})
        print(f'{tid}: candidates {len(done)}/240; tests {len(test_done)}/60', flush=True)


if __name__ == '__main__': main()

"""Freeze public-only triggers, then generate one repair and one extra-sample control."""
import argparse
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
from verifier_study.test_quality import public_assertions

REPAIR_INSTRUCTION = '''The implementation below failed one or more PUBLIC example assertions.
Correct the implementation using the specification and the failed public assertions.
Reconcile the examples with the prose, fix the general algorithm rather than hardcoding
the examples, and preserve the function name and signature. Return only executable
Python code. Do not add tests or explanations.
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-path')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = ROOT/'runs/mbpp-repair-20260907'
    out.mkdir(parents=True, exist_ok=True)
    parent = ROOT/'runs/mbpp-parser-ablation-20260905'
    decision_path = ROOT/'runs/mbpp-public-consensus-20260906/decisions.jsonl'
    visible_path = ROOT/'data/prompts/mbpp-v0.2.0.jsonl'
    visible = {r['task_id']: r for r in read_jsonl(visible_path)}
    candidates = {(r['task_id'], r['sample_index']): r for r in read_jsonl(parent/'generations.jsonl')}
    public = [r for r in read_jsonl(parent/'linux/candidate-test-matrix.jsonl') if r['source'] == 'public']
    selected = read_jsonl(decision_path)
    tasks = []
    base = []
    for decision in selected:
        tid, index = decision['task_id'], decision['sample_index']
        statuses = [r for r in public if (r['task_id'], r['sample_index']) == (tid, index)]
        assert statuses
        assertions = public_assertions(visible[tid]['prompt'])
        failures = [assertions[r['test_index']] for r in statuses if r['status'] != 'pass']
        tasks.append({'task_id': tid, 'selected_index': index, 'triggered': bool(failures),
                      'failed_public_assertions': failures})
        base.append(candidates[tid, index])
    assert len(tasks) == len({t['task_id'] for t in tasks}) == 20
    plan = {'phase': 'Adaptive exposed-development pilot; never confirmation',
            'tasks': tasks, 'temperature': 0.7, 'top_p': 0.8, 'top_k': 20, 'max_new_tokens': 768,
            'repair_instruction': REPAIR_INSTRUCTION,
            'trigger': 'At least one selected-candidate public assertion failed',
            'replacement': 'Replace only if new candidate passes strictly more public assertions; otherwise retain original',
            'budget': 'One extra model call per triggered task per arm; same seed and output cap, actual tokens/time reported separately',
            'repair_index': 4, 'control_index': 5,
            'source_hashes': {str(p.relative_to(ROOT)): sha256(p) for p in
                [decision_path, visible_path, parent/'generations.jsonl', parent/'linux/candidate-test-matrix.jsonl']},
            'generation_source_sha256': sha256(ROOT/'src/verifier_study/generation.py'),
            'selector_sha256': sha256(ROOT/'src/verifier_study/repair.py')}
    plan_path = out/'repair-plan.json'
    if plan_path.exists():
        assert json.loads(plan_path.read_text(encoding='utf-8')) == plan, 'Frozen repair plan changed'
    else:
        write_json(plan_path, plan)
    tests = (parent/'generated-tests.jsonl').read_bytes()
    if (out/'generated-tests.jsonl').exists():
        assert (out/'generated-tests.jsonl').read_bytes() == tests
    else:
        (out/'generated-tests.jsonl').write_bytes(tests)
    write_json(out/'test-manifest.json', {'parent_run': parent.name, 'test_generation_reused': True,
              'new_test_model_calls': 0, 'tests_sha256': sha256(out/'generated-tests.jsonl')})
    path = out/'new-generations.jsonl'
    records = read_jsonl(path) if path.exists() else []
    expected = {(t['task_id'], i) for t in tasks if t['triggered'] for i in (4, 5)}
    done = {(r['task_id'], r['sample_index']) for r in records}
    assert len(done) == len(records) and done <= expected
    print(json.dumps({'triggered': sum(t['triggered'] for t in tasks), 'planned_new_calls': len(expected),
                      'completed_new_calls': len(done)}), flush=True)
    if args.prepare_only:
        return
    if done != expected:
        assert args.model_path
        free = int(subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'], text=True).splitlines()[0])
        if free < 9216:
            print('Deferred: insufficient free VRAM', free, flush=True)
            return
        fingerprint_path = ROOT/'configs/model-fingerprint.json'
        fingerprint = json.loads(fingerprint_path.read_text(encoding='utf-8'))
        for item in fingerprint['files']:
            assert sha256(Path(args.model_path)/item['file']) == item['sha256']
        manifest = {'task_ids': [t['task_id'] for t in tasks], 'plan_sha256': sha256(plan_path),
                    'model_fingerprint_sha256': sha256(fingerprint_path),
                    'generator_script_sha256': sha256(Path(__file__)),
                    'packages': {n: importlib.metadata.version(n) for n in ['torch', 'transformers', 'accelerate', 'tokenizers']}}
        if (out/'manifest.json').exists():
            assert json.loads((out/'manifest.json').read_text(encoding='utf-8')) == manifest
        else:
            write_json(out/'manifest.json', manifest)
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '1'
        from verifier_study.generation import LocalCausalLM, SYSTEM_PROMPT
        model = LocalCausalLM(args.model_path, 'Qwen/Qwen3-4B')
        for task in tasks:
            if not task['triggered']:
                continue
            tid = task['task_id']
            prompt = visible[tid]['prompt']
            seed = int(hashlib.sha256(f'repair:20260907:{tid}'.encode()).hexdigest()[:8], 16)
            for index in (4, 5):
                if (tid, index) in done:
                    continue
                common = dict(task_id=tid, sample_index=index, seed=seed, temperature=0.7, top_p=0.8, max_new_tokens=768)
                if index == 4:
                    content = (REPAIR_INSTRUCTION + '\nSPECIFICATION:\n' + prompt + '\nIMPLEMENTATION:\n' +
                               candidates[tid, task['selected_index']]['code'] + '\nFAILED PUBLIC ASSERTIONS:\n' +
                               '\n'.join(task['failed_public_assertions']))
                    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}, {'role': 'user', 'content': content}]
                    record = model._generate_messages(messages=messages, generation_kind='public_feedback_repair', **common).to_dict()
                else:
                    record = model.generate(function_prompt=prompt, **common).to_dict()
                    record['generation_kind'] = 'extra_sample_control'
                append_jsonl(path, record)
                records.append(record)
                done.add((tid, index))
                print(f'{len(done)}/{len(expected)} {tid} sample={index} tokens={record["output_tokens"]}', flush=True)
    assert done == expected
    write_jsonl(out/'generations.jsonl', base + records)
    write_json(out/'progress.json', {'status': 'generation_complete', 'reused_selected_candidates': len(base),
                'new_calls': len(records), 'new_output_tokens': sum(r['output_tokens'] for r in records),
                'new_generation_seconds': sum(r['wall_seconds'] for r in records)})


if __name__ == '__main__':
    main()

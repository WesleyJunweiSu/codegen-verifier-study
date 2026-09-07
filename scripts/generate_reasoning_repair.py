"""Paired reasoning repair vs reasoning resampling on frozen public-failure triggers."""
import argparse
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--model-path')
    args = parser.parse_args()
    parent = ROOT/'runs/mbpp-repair-20260907'
    out = ROOT/'runs/mbpp-reasoning-repair-20260907'
    out.mkdir(parents=True, exist_ok=True)
    plan = json.loads((parent/'repair-plan.json').read_text(encoding='utf-8'))
    plan.update({'thinking': True, 'temperature': 0.6, 'top_p': 0.95, 'max_new_tokens': 2048,
        'parent_plan_sha256': sha256(parent/'repair-plan.json'),
        'generation_source_sha256': sha256(ROOT/'src/verifier_study/reasoning_generation.py'),
        'reasoning_policy': 'Single call, 2048 total generated tokens including reasoning. If no closing think token, empty failed candidate. No retry or budget extension.',
        'rationale': 'Observed public-example errors persist in non-thinking repair outputs; official Qwen thinking preset, not a one-factor attribution.',
        'entropy_logging': False,
        'source': 'https://huggingface.co/Qwen/Qwen3-4B (accessed 2026-09-07)'})
    plan_path = out/'repair-plan.json'
    if plan_path.exists():
        assert json.loads(plan_path.read_text(encoding='utf-8')) == plan
    else:
        write_json(plan_path, plan)
    for name in ['generated-tests.jsonl', 'test-manifest.json']:
        raw = (parent/name).read_bytes()
        if (out/name).exists(): assert (out/name).read_bytes() == raw
        else: (out/name).write_bytes(raw)
    records_path = out/'new-generations.jsonl'
    records = read_jsonl(records_path) if records_path.exists() else []
    done = {(r['task_id'], r['sample_index']) for r in records}
    expected = {(t['task_id'], i) for t in plan['tasks'] if t['triggered'] for i in (4, 5)}
    assert len(done) == len(records) and done <= expected
    print(json.dumps({'planned': len(expected), 'completed': len(done)}), flush=True)
    if args.prepare_only: return
    base = [r for r in read_jsonl(parent/'generations.jsonl') if r['sample_index'] < 4]
    if done != expected:
        assert args.model_path
        free = int(subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'], text=True).splitlines()[0])
        if free < 9216:
            print('Deferred: insufficient free VRAM', free, flush=True); return
        fingerprint_path = ROOT/'configs/model-fingerprint.json'
        for item in json.loads(fingerprint_path.read_text(encoding='utf-8'))['files']:
            assert sha256(Path(args.model_path)/item['file']) == item['sha256']
        manifest = {'task_ids': [t['task_id'] for t in plan['tasks']], 'plan_sha256': sha256(plan_path),
                    'model_fingerprint_sha256': sha256(fingerprint_path), 'generator_script_sha256': sha256(Path(__file__)),
                    'packages': {n: importlib.metadata.version(n) for n in ['torch', 'transformers', 'accelerate', 'tokenizers']}}
        if (out/'manifest.json').exists(): assert json.loads((out/'manifest.json').read_text(encoding='utf-8')) == manifest
        else: write_json(out/'manifest.json', manifest)
        visible = {r['task_id']: r for r in read_jsonl(ROOT/'data/prompts/mbpp-v0.2.0.jsonl')}
        selected = {r['task_id']: r for r in base}
        seeds = {(r['task_id'], r['sample_index']): r['seed'] for r in read_jsonl(parent/'new-generations.jsonl')}
        os.environ['HF_HUB_OFFLINE'] = '1'; os.environ['TRANSFORMERS_OFFLINE'] = '1'
        from verifier_study.reasoning_generation import ReasoningLM
        model = ReasoningLM(args.model_path, 'Qwen/Qwen3-4B')
        for task in plan['tasks']:
            if not task['triggered']: continue
            tid = task['task_id']; prompt = visible[tid]['prompt']
            for index in (4, 5):
                if (tid, index) in done: continue
                messages = build_prompt(prompt)
                if index == 4:
                    content = (plan['repair_instruction'] + '\nSPECIFICATION:\n' + prompt + '\nIMPLEMENTATION:\n' +
                               selected[tid]['code'] + '\nFAILED PUBLIC ASSERTIONS:\n' + '\n'.join(task['failed_public_assertions']))
                    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}, {'role': 'user', 'content': content}]
                record = model.generate_reasoning(task_id=tid, messages=messages, sample_index=index,
                    seed=seeds[tid, index], generation_kind='public_feedback_repair' if index == 4 else 'extra_sample_control',
                    max_new_tokens=plan['max_new_tokens'])
                append_jsonl(records_path, record); records.append(record); done.add((tid, index))
                write_json(out/'progress.json', {'completed': len(done), 'planned': len(expected),
                    'output_tokens': sum(r['output_tokens'] for r in records), 'generation_seconds': sum(r['wall_seconds'] for r in records),
                    'status': 'generation_complete' if done == expected else 'running'})
                print(f'{len(done)}/{len(expected)} {tid} sample={index} tokens={record["output_tokens"]} complete={record["thinking_complete"]}', flush=True)
    write_jsonl(out/'generations.jsonl', base + records)


if __name__ == '__main__':
    main()

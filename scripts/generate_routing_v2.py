"""Prepare/resume a development-only two-arm routing ablation, without label reads."""
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

RUN = 'mbpp-routing-v2-development-20260911'


def freeze(path, value):
    if path.exists():
        assert json.loads(path.read_text(encoding='utf-8')) == value, str(path)
    else:
        write_json(path, value)


def prepare():
    parent = ROOT/'runs/mbpp-development40-20260907'
    composition = ROOT/'runs/mbpp-development40-public-consensus-20260908/decisions.jsonl'
    previous = ROOT/'runs/mbpp-development40-repair-20260908/new-generations.jsonl'
    public_path = parent/'linux/candidate-test-matrix.jsonl'
    public = [r for r in read_jsonl(public_path) if r['source'] == 'public']
    cohort = json.loads((parent/'manifest.json').read_text(encoding='utf-8'))['task_ids']
    split = json.loads((ROOT/'configs/split-manifest.json').read_text())
    assert len(cohort) == 40 and set(cohort) <= set(split['development'])
    tasks = []
    for row in read_jsonl(composition):
        tid, index = row['task_id'], row['sample_index']
        outcomes = [r for r in public if (r['task_id'], r['sample_index']) == (tid, index)]
        assert outcomes
        failed = any(r['status'] != 'pass' for r in outcomes)
        fraction = row['consensus_scores'][str(index)]['fraction']
        tasks.append(dict(task_id=tid, selected_index=index, public_failed=failed,
                          consensus_fraction=fraction, triggered=failed or fraction < 1))
    assert len(tasks) == 40 and {t['task_id'] for t in tasks} == set(cohort)
    sources = [composition, public_path, previous, parent/'generations.jsonl', parent/'generated-tests.jsonl',
        ROOT/'data/prompts/mbpp-v0.2.0.jsonl', ROOT/'configs/model-fingerprint.json',
        Path(__file__), ROOT/'src/verifier_study/routing_v2.py', ROOT/'scripts/routing_v2_visible.py',
        ROOT/'src/verifier_study/generation.py', ROOT/'src/verifier_study/reasoning_generation.py']
    plan = dict(run_id=RUN, phase='Adaptive development after existing labels inspected; NOT confirmation',
        task_ids=cohort, tasks=tasks, dataset_sha256=split['sha256'],
        trigger='public failure OR selected consensus fraction below one; all flagged tasks retained',
        replacement='strict public improvement; separate tie ablation accepts only all-public-pass alternatives',
        seed_rule='sha256(transfer:20260908:{task_id})[:8] hex; matches reused attempts',
        arms=[dict(method='nonthinking', sample_index=5, max_new_tokens=768, temperature=0.7, top_p=0.8, top_k=20),
              dict(method='reasoning', sample_index=7, max_new_tokens=2048, temperature=0.6, top_p=0.95, top_k=20)],
        failure_policy='Keep capped/malformed attempts; no retries. All 40 tasks in every denominator.',
        analysis='Report all seven methods, paired rescues/regressions, accuracy and cost. No confirmatory p-value claims.',
        source_hashes={str(p.relative_to(ROOT)): sha256(p) for p in sources})
    out = ROOT/'runs'/RUN; out.mkdir(parents=True, exist_ok=True)
    freeze(out/'routing-plan.json', plan)
    expected = {(t['task_id'], i) for t in tasks if t['triggered'] for i in [5, 7]}
    reused = [r for r in read_jsonl(previous) if (r['task_id'], r['sample_index']) in expected]
    assert len(reused) == len({(r['task_id'], r['sample_index']) for r in reused}) == 6
    for row in reused:
        assert row['seed'] == int(hashlib.sha256(f'transfer:20260908:{row["task_id"]}'.encode()).hexdigest()[:8], 16)
    raw = (parent/'generated-tests.jsonl').read_bytes()
    target = out/'generated-tests.jsonl'
    if target.exists(): assert target.read_bytes() == raw
    else: target.write_bytes(raw)
    freeze(out/'manifest.json', dict(task_ids=cohort, routing_plan_sha256=sha256(out/'routing-plan.json'),
        reused_calls=6, new_calls=len(expected)-6, hidden_labels_used_by_preparation=False))
    return out, plan, expected, reused, parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--model-path')
    args = parser.parse_args()
    out, plan, expected, reused, parent = prepare()
    path = out/'new-generations.jsonl'
    new = read_jsonl(path) if path.exists() else []
    records = reused + new
    done = {(r['task_id'], r['sample_index']) for r in records}
    assert len(done) == len(records) and done <= expected
    print(f'{len(done)}/{len(expected)} extension records, including {len(reused)} reused; 40 tasks retained', flush=True)
    if args.prepare_only: return
    if done != expected:
        assert args.model_path
        free = int(subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'], text=True).splitlines()[0])
        append_jsonl(out/'attempts.jsonl', dict(utc=datetime.datetime.now(datetime.UTC).isoformat(), free_mib=free))
        if free < 9216:
            print('Deferred: existing GPU workload/headroom. Do not overlap confirmation.', flush=True)
            return
        runtime = json.loads((ROOT/'configs/confirmation-protocol.json').read_text())['runtime_packages']
        assert {n: importlib.metadata.version(n) for n in runtime} == runtime
        fingerprint = json.loads((ROOT/'configs/model-fingerprint.json').read_text())
        for item in fingerprint['files']:
            assert sha256(Path(args.model_path)/item['file']) == item['sha256']
        os.environ['HF_HUB_OFFLINE'] = '1'; os.environ['TRANSFORMERS_OFFLINE'] = '1'
        from verifier_study.reasoning_generation import ReasoningLM
        model = ReasoningLM(args.model_path, 'Qwen/Qwen3-4B')
        visible = {r['task_id']: r for r in read_jsonl(ROOT/'data/prompts/mbpp-v0.2.0.jsonl')}
        for task in plan['tasks']:
            tid = task['task_id']
            for arm in plan['arms']:
                key = tid, arm['sample_index']
                if key not in expected or key in done: continue
                common = dict(task_id=tid, messages=build_prompt(visible[tid]['prompt']), sample_index=key[1],
                    seed=int(hashlib.sha256(f'transfer:20260908:{tid}'.encode()).hexdigest()[:8], 16),
                    generation_kind=arm['method']+'_resample', max_new_tokens=arm['max_new_tokens'])
                if arm['method'] == 'reasoning':
                    record = model.generate_reasoning(**common)
                else:
                    record = model._generate_messages(**common, temperature=arm['temperature'], top_p=arm['top_p']).to_dict()
                append_jsonl(path, record); records.append(record); new.append(record); done.add(key)
                write_json(out/'progress.json', dict(completed=len(done), planned=len(expected), reused=len(reused),
                    new_output_tokens=sum(r['output_tokens'] for r in new), status='complete' if done == expected else 'running'))
                print(f'{len(done)}/{len(expected)} {tid} {arm["method"]}', flush=True)
    pool = {(r['task_id'], r['sample_index']): r for r in read_jsonl(parent/'generations.jsonl')}
    base = [pool[t['task_id'], t['selected_index']] for t in plan['tasks']]
    assert done == expected
    write_jsonl(out/'generations.jsonl', base + records)


if __name__ == '__main__': main()

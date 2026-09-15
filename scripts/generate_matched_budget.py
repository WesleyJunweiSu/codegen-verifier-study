"""Development-only output-budget comparison; never execute candidate code."""
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
from verifier_study.generation import build_prompt


def freeze(path, value):
    if path.exists():
        assert json.loads(path.read_text(encoding='utf-8')) == value, path.name
    else:
        write_json(path, value)


def remaining_budget(rows, budget):
    used = sum(r['output_tokens'] for r in rows)
    assert all(r['output_tokens'] > 0 for r in rows) and used <= budget
    return budget-used


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-path', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    config_path = ROOT/'configs/matched-budget-development.json'
    cfg = json.loads(config_path.read_text(encoding='utf-8'))
    split_path = ROOT/'configs/split-manifest-v2.json'
    split = json.loads(split_path.read_text(encoding='utf-8'))
    run = ROOT/'runs'/cfg['run_id']; run.mkdir(exist_ok=True)
    sources = [config_path, split_path, Path(__file__), ROOT/'configs/model-fingerprint.json',
               ROOT/'src/verifier_study/generation.py', ROOT/'src/verifier_study/reasoning_generation.py',
               ROOT/'data/prompts/mbpp-v0.2.0.jsonl']
    tasks=[]; baselines=[]; tests=[]
    for cohort in cfg['cohorts']:
        parent=ROOT/'runs'/cohort['run']
        dp=ROOT/cohort['decisions']; mp=ROOT/cohort['matrix']
        gp=parent/'generations.jsonl'; tp=parent/'generated-tests.jsonl'
        sources += [dp,mp,gp,tp]
        decisions=read_jsonl(dp); matrix=read_jsonl(mp)
        pool={(r['task_id'],r['sample_index']):r for r in read_jsonl(gp)}
        for d in decisions:
            key=(d['task_id'],d['sample_index'])
            public=[r for r in matrix if r['source']=='public' and (r['task_id'],r['sample_index'])==key]
            assert public
            tasks.append(dict(task_id=key[0],selected_index=key[1],triggered=any(r['status']!='pass' for r in public)))
            baselines.append(pool[key])
        tests += read_jsonl(tp)
    assert len(tasks)==100 and {r['task_id'] for r in tasks}==set(split['development_primary'])
    assert sum(t['triggered'] for t in tasks)==14
    assert len(tests)==100 and {r['task_id'] for r in tests}==set(split['development_primary'])
    plan={**cfg,'tasks':tasks,'source_hashes':{str(p.relative_to(ROOT)):sha256(p) for p in sources}}
    freeze(run/'budget-plan.json',plan)
    packages={n:importlib.metadata.version(n) for n in ['torch','transformers','accelerate','tokenizers']}
    expected_packages=json.loads((ROOT/'runs/mbpp-development60-20260913/manifest.json').read_text())['packages']
    assert packages==expected_packages
    freeze(run/'manifest.json',dict(task_ids=[t['task_id'] for t in tasks],plan_sha256=sha256(run/'budget-plan.json'),packages=packages))
    for name,rows in [('baseline-generations.jsonl',baselines),('generated-tests.jsonl',tests)]:
        if (run/name).exists(): assert read_jsonl(run/name)==rows
        else: write_jsonl(run/name,rows)
    path=run/'new-generations.jsonl'; records=read_jsonl(path) if path.exists() else []
    keys={(r['task_id'],r['sample_index']) for r in records}; assert len(keys)==len(records)
    triggered={t['task_id'] for t in tasks if t['triggered']}
    assert all(r['task_id'] in triggered and (r['sample_index']==4 or 5<=r['sample_index']<2053) for r in records)
    if args.prepare_only:
        print('Frozen100 tasks,14 triggers; no model loaded',flush=True); return
    free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])
    if free<9216:
        write_json(run/'attempt.json',dict(status='deferred_insufficient_vram',free_mib=free)); return
    for item in json.loads((ROOT/'configs/model-fingerprint.json').read_text())['files']:
        assert sha256(Path(args.model_path)/item['file'])==item['sha256']
    os.environ['HF_HUB_OFFLINE']='1'; os.environ['TRANSFORMERS_OFFLINE']='1'
    from verifier_study.reasoning_generation import ReasoningLM
    model=ReasoningLM(args.model_path,'Qwen/Qwen3-4B')
    prompts={r['task_id']:r['prompt'] for r in read_jsonl(ROOT/'data/prompts/mbpp-v0.2.0.jsonl')}
    def save(r):
        append_jsonl(path,r); records.append(r); keys.add((r['task_id'],r['sample_index']))
        write_json(run/'progress.json',dict(status='running',new_calls=len(records),output_tokens=sum(x['output_tokens'] for x in records),wall_seconds=sum(x['wall_seconds'] for x in records),last_task=r['task_id']))
    for task in tasks:
        tid=task['task_id']
        if not task['triggered']: continue
        messages=build_prompt(prompts[tid])
        if (tid,4) not in keys:
            seed=int(hashlib.sha256(f'matched:20260915:{tid}:reasoning:0'.encode()).hexdigest()[:8],16)
            r=model.generate_reasoning(task_id=tid,messages=messages,sample_index=4,seed=seed,generation_kind='reasoning_budget2048',max_new_tokens=2048)
            save(r)
        iid=[r for r in records if r['task_id']==tid and r['sample_index']>=5]
        assert sorted(r['sample_index'] for r in iid)==list(range(5,5+len(iid)))
        remaining=remaining_budget(iid,2048)
        while remaining:
            index=5+len(iid); seed=int(hashlib.sha256(f'matched:20260915:{tid}:nonthinking:{index-5}'.encode()).hexdigest()[:8],16)
            r=model._generate_messages(task_id=tid,messages=messages,sample_index=index,seed=seed,generation_kind='nonthinking_budget2048',max_new_tokens=min(768,remaining),temperature=0.7,top_p=0.8).to_dict()
            save(r); iid.append(r); remaining=remaining_budget(iid,2048)
        print(f'{tid}: reasoning1, iid{len(iid)}; iid tokens2048',flush=True)
    write_jsonl(run/'generations.jsonl',baselines+records)
    write_json(run/'progress.json',dict(status='generation_complete',tasks=100,triggers=14,new_calls=len(records),output_tokens=sum(r['output_tokens'] for r in records),wall_seconds=sum(r['wall_seconds'] for r in records)))


if __name__=='__main__': main()

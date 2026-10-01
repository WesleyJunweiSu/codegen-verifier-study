"""Bounded temperature-only development intervention; isolated scoring is remote."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from verifier_study.io import read_jsonl, write_json, write_jsonl, append_jsonl, sha256
from verifier_study.generation import build_prompt
from verifier_study.matched_budget import validate_pool
from generate_matched_budget import freeze, remaining_budget

CONFIG = ROOT / 'configs/diversity-budget-development.json'
RUN = 'mbpp-diversity-budget-development-20261001'
OUT = ROOT / 'runs' / RUN
MODEL = 'C:/Users/Asuka/Documents/techblog/models/Qwen3-4B'


def seed_for(tid, call):
    return int(hashlib.sha256(f'matched:20260915:{tid}:nonthinking:{call}'.encode()).hexdigest()[:8], 16)


def validate_partial(rows, triggered):
    assert all(r['task_id'] in triggered for r in rows)
    assert len({(r['task_id'], r['sample_index']) for r in rows}) == len(rows)
    for tid in triggered:
        pool = sorted([r for r in rows if r['task_id'] == tid], key=lambda r:r['sample_index'])
        assert [r['sample_index'] for r in pool] == list(range(5, 5 + len(pool)))
        left = 2048
        for call, r in enumerate(pool):
            assert r['seed'] == seed_for(tid, call)
            assert r['generation_kind'] == 'nonthinking_temperature1_budget2048'
            assert 0 < r['output_tokens'] <= min(768, left)
            left -= r['output_tokens']


def prepare():
    cfg = json.loads(CONFIG.read_text(encoding='utf-8'))
    assert cfg['run_id'] == RUN and cfg['temperature'] == 1.0 and cfg['top_p'] == 0.8
    parent = ROOT / 'runs' / cfg['parent_run']
    old = json.loads((parent / 'budget-plan.json').read_text(encoding='utf-8'))
    for name, digest in old['source_hashes'].items():
        assert sha256(ROOT/name) == digest, name
    split = json.loads((ROOT/'configs/split-manifest-v2.json').read_text(encoding='utf-8'))
    assert {r['task_id'] for r in old['tasks']} == set(split['development_primary'])
    assert sum(r['triggered'] for r in old['tasks']) == 14
    OUT.mkdir(exist_ok=True)
    paths = [CONFIG, Path(__file__), parent/'budget-plan.json', parent/'generations.jsonl',
             ROOT/'src/verifier_study/matched_budget.py', ROOT/'scripts/matched_visible_linux.py',
             ROOT/'scripts/freeze_matched_score.py', ROOT/'scripts/analyze_matched_budget.py',
             ROOT/'scripts/continue_confirmation.py', ROOT/'.github/workflows/matched-visible.yml',
             ROOT/'.github/workflows/score-frozen.yml', ROOT/'docker/Dockerfile.matched-eval']
    plan = {**old, 'run_id':RUN, 'parent_run':cfg['parent_run'], 'intervention':cfg,
            'question':cfg['hypothesis'], 'nonthinking':'Temperature1.0,top_p0.8,top_k20; otherwise original budget/seed/selector',
            'source_hashes':{**old['source_hashes'], **{p.relative_to(ROOT).as_posix():sha256(p) for p in paths}}}
    freeze(OUT/'budget-plan.json', plan)
    old_records = read_jsonl(parent/'generations.jsonl')
    validate_pool(old, old_records)
    reused = [r for r in old_records if r['sample_index'] < 5]
    assert len(reused) == 114
    freeze(OUT/'reused-generations.json', reused)
    packages = {n:importlib.metadata.version(n) for n in ['torch','transformers','accelerate','tokenizers']}
    assert packages == json.loads((parent/'manifest.json').read_text(encoding='utf-8'))['packages']
    freeze(OUT/'manifest.json', {'task_ids':[t['task_id'] for t in old['tasks']], 'packages':packages,
                               'plan_sha256':sha256(OUT/'budget-plan.json'), 'reused_records':114,
                               'model_fingerprint_sha256':sha256(ROOT/'configs/model-fingerprint.json')})
    return cfg, plan, reused


def audit(rows):
    return {name:{'calls':len(group),'output_tokens':sum(r['output_tokens'] for r in group),
                  'input_tokens':sum(r['input_tokens'] for r in group),
                  'code_parses':sum(r['code_parses'] for r in group),
                  'wall_seconds':sum(r['wall_seconds'] for r in group),
                  'peak_vram_bytes':max((r['peak_vram_bytes'] for r in group),default=0),
                  'reused':name=='reasoning'}
            for name, group in [('reasoning',[r for r in rows if r['sample_index']==4]),
                                ('nonthinking',[r for r in rows if r['sample_index']>=5])]}


def generate():
    cfg, plan, reused = prepare()
    path = OUT/'new-generations.jsonl'
    rows = read_jsonl(path) if path.exists() else []
    triggered = [r['task_id'] for r in plan['tasks'] if r['triggered']]
    validate_partial(rows, triggered)
    if len(rows) and sum(r['output_tokens'] for r in rows) == cfg['max_new_output_tokens']:
        validate_pool(plan, reused+rows)
        write_jsonl(OUT/'generations.jsonl', reused+rows)
        write_json(OUT/'generation-audit.json', audit(reused+rows))
        write_json(OUT/'progress.json', {'status':'generation_complete','new_calls':len(rows),'new_output_tokens':28672})
        return
    free = int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])
    append_jsonl(OUT/'attempts.jsonl', {'time':time.time(),'free_mib':free,'existing_calls':len(rows)})
    if free < cfg['gpu_minimum_free_mib']:
        write_json(OUT/'progress.json', {'status':'deferred_insufficient_vram','free_mib':free})
        raise SystemExit(2)
    for item in json.loads((ROOT/'configs/model-fingerprint.json').read_text(encoding='utf-8'))['files']:
        assert sha256(Path(MODEL)/item['file']) == item['sha256']
    os.environ['HF_HUB_OFFLINE']='1'; os.environ['TRANSFORMERS_OFFLINE']='1'
    from verifier_study.generation import LocalCausalLM
    model = LocalCausalLM(MODEL, 'Qwen/Qwen3-4B')
    assert model.model.generation_config.top_k == cfg['expected_top_k']
    prompts = {r['task_id']:r['prompt'] for r in read_jsonl(ROOT/'data/prompts/mbpp-v0.2.0.jsonl')}
    for tid in triggered:
        pool = [r for r in rows if r['task_id']==tid]
        left = remaining_budget(pool, 2048)
        while left:
            assert len(rows) < cfg['max_new_calls']
            call = len(pool)
            r = model._generate_messages(task_id=tid,messages=build_prompt(prompts[tid]),sample_index=5+call,
                    seed=seed_for(tid,call),generation_kind='nonthinking_temperature1_budget2048',
                    max_new_tokens=min(768,left),temperature=cfg['temperature'],top_p=cfg['top_p']).to_dict()
            append_jsonl(path,r); rows.append(r); pool.append(r)
            left = remaining_budget(pool,2048)
            write_json(OUT/'progress.json', {'status':'running','new_calls':len(rows),
                       'new_output_tokens':sum(x['output_tokens'] for x in rows),'last_task':tid})
        print(f'{tid}: {len(pool)} calls,2048 output tokens',flush=True)
    validate_partial(rows,triggered); validate_pool(plan,reused+rows)
    write_jsonl(OUT/'generations.jsonl',reused+rows)
    write_json(OUT/'generation-audit.json',audit(reused+rows))
    write_json(OUT/'progress.json',{'status':'generation_complete','new_calls':len(rows),'new_output_tokens':28672})


def analyze_temperature():
    cfg=json.loads(CONFIG.read_text(encoding='utf-8'));parent=ROOT/'runs'/cfg['parent_run']
    old={r['task_id']:r['nonthinking_budget2048'] for r in json.loads((parent/'task-results.json').read_text(encoding='utf-8'))}
    new={r['task_id']:r['nonthinking_budget2048'] for r in json.loads((OUT/'task-results.json').read_text(encoding='utf-8'))}
    assert set(old)==set(new) and len(new)==100
    diffs=[int(new[t])-int(old[t]) for t in old];rng=random.Random(20261001)
    boot=sorted(sum(rng.choices(diffs,k=100)) for _ in range(10000))
    oldrows=read_jsonl(parent/'new-generations.jsonl');newrows=read_jsonl(OUT/'new-generations.jsonl')
    tids=[t['task_id'] for t in json.loads((OUT/'budget-plan.json').read_text())['tasks'] if t['triggered']]
    labels={(r['task_id'],r['sample_index']):r['pass'] for r in read_jsonl(OUT/'linux/evaluation.jsonl')}
    per_task=[]
    for tid in tids:
        a=[r for r in oldrows if r['task_id']==tid and r['sample_index']>=5]
        b=[r for r in newrows if r['task_id']==tid]
        per_task.append(dict(task_id=tid,old_calls=len(a),new_calls=len(b),
            old_distinct_code=len({r['code'] for r in a}),new_distinct_code=len({r['code'] for r in b}),
            new_pool_oracle=any(labels[r['task_id'],r['sample_index']] for r in b)))
    result=dict(scope=cfg['scope'],temperature07_correct=sum(old.values()),temperature10_correct=sum(new.values()),
                wins=[t for t in old if new[t] and not old[t]],losses=[t for t in old if old[t] and not new[t]],
                difference_pp=sum(diffs),exploratory_bootstrap95_pp=[boot[249],boot[9749]],per_task=per_task,
                limitation='Adaptive development,14 treated tasks; source uniqueness is not semantic correctness; shared baselines/reasoning are reused; no confirmation or causal claim.')
    write_json(OUT/'temperature-summary.json',result)
    text=f"\n\n## 2026-10-01 temperature budget control completed\n\nNonthinking T1.0 selected{sum(new.values())}/100 versus saved T0.7 {sum(old.values())}/100;{len(result['wins'])} wins,{len(result['losses'])} losses on14 triggered development tasks. Same2048 output budget per trigger; report input/latency separately. Evidence in runs/{RUN}/temperature-summary.json and generation-audit.json. This is adaptive development evidence, not independent confirmation. Reserve untouched.\n"
    progress=ROOT/'PROGRESS.md'
    if f'## 2026-10-01 temperature budget control completed' not in progress.read_text(encoding='utf-8'):
        with progress.open('a',encoding='utf-8') as f:f.write(text)


def continue_run():
    import continue_confirmation as flow
    import freeze_matched_score as freezer
    freezer.RUN=RUN
    import analyze_matched_budget as analysis
    analysis.RUN=RUN
    flow.JOURNAL=OUT/'continuation-state.json'
    state=json.loads(flow.JOURNAL.read_text()) if flow.JOURNAL.exists() else {'jobs':{}}
    if state.get('stage')=='complete':return
    source=flow.commit([str(OUT.relative_to(ROOT))],'Record completed temperature1 generation pool')
    flow.workflow(state,'diversity_visible','matched-visible.yml',RUN,'visible-evidence',OUT/'visible',source)
    freezer.main()
    source=flow.commit([str(OUT.relative_to(ROOT))],'Freeze temperature1 public decisions before development scoring')
    flow.workflow(state,'diversity_score','score-frozen.yml',RUN,'frozen-scoring',OUT/'linux',source)
    analysis.main();analyze_temperature();flow.checkpoint(state,'complete')
    flow.commit([str(OUT.relative_to(ROOT)),'PROGRESS.md'],'Record temperature1 budget-control results and costs')


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','generate','continue','execute']);a=p.parse_args()
    if a.stage=='prepare':prepare();print('Frozen100 development tasks,14 triggers; no model loaded');return
    if a.stage=='generate':generate();return
    if a.stage=='continue':continue_run();return
    prepare()
    failures=OUT/'failures.jsonl'
    if failures.exists() and any(r['type']=='TimeoutExpired' for r in read_jsonl(failures)):
        raise RuntimeError('Generation deadline already exhausted; record a resource decision before extending it')
    lock=OUT/'execution.lock'
    with lock.open('x') as f:f.write(str(os.getpid()))
    try:
        subprocess.run([sys.executable,'-X','utf8','-u',str(Path(__file__)),'generate'],cwd=ROOT,check=True,
                       timeout=json.loads(CONFIG.read_text())['max_generation_wall_seconds'])
        continue_run()
    except BaseException as e:
        append_jsonl(OUT/'failures.jsonl',{'time':time.time(),'type':type(e).__name__,
            'message':str(e),'partial_unrecorded_call_cost':'unknown if interrupted during generation; do not treat as free'})
        raise
    finally:
        lock.unlink()


if __name__=='__main__':main()

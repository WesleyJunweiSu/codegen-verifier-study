"""Descriptive audit of already-scored cohorts; never fit policies or read new labels."""
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from verifier_study.io import read_jsonl,sha256,write_json
from verifier_study.test_quality import public_assertions


def wilson(k,n):
    z=1.959963984540054; p=k/n; den=1+z*z/n
    center=(p+z*z/(2*n))/den
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [center-half,center+half]


def main():
    sources=[]
    def jsonfile(name):
        path=ROOT/name;sources.append(path);return json.loads(path.read_text(encoding='utf-8'))
    def rows(name):
        path=ROOT/name;sources.append(path);return read_jsonl(path)
    split=jsonfile('configs/split-manifest-v2.json')
    old40=jsonfile('configs/development-expansion.json')['task_ids']
    new60=split['development_newly_reassigned']
    matched='runs/mbpp-matched-budget-development-20260915/'
    confirmation='runs/mbpp-confirmation-extensions-20260911/'
    outcomes={r['task_id']:r for r in jsonfile(matched+'task-results.json')}
    outcomes.update({r['task_id']:r for r in jsonfile(confirmation+'task-results.json')})
    baselines={r['task_id']:r for r in rows(matched+'baseline-generations.jsonl')}
    conf_decisions=[r for r in rows(confirmation+'frozen-decisions.jsonl') if r['method']=='selected_baseline']
    conf_pool={(r['task_id'],r['sample_index']):r for r in rows('runs/mbpp-confirmation-20260911/generations.jsonl')}
    baselines.update({r['task_id']:conf_pool[r['task_id'],r['sample_index']] for r in conf_decisions})
    visible={r['task_id']:r for r in rows('data/prompts/mbpp-v0.2.0.jsonl')}
    trigger={t['task_id']:t['triggered'] for t in jsonfile(matched+'budget-plan.json')['tasks']}
    trigger.update({t['task_id']:t['triggered'] for t in jsonfile(confirmation+'repair-plan.json')['tasks']})
    manifests={name:jsonfile('runs/'+name+'/manifest.json') for name in ['mbpp-development40-20260907','mbpp-development60-20260913','mbpp-confirmation-20260911']}
    groups={};details=[]
    for name,ids in [('additional40',old40),('reassigned60',new60),('historical_confirmation180',split['confirmation'])]:
        assert set(ids)<=set(outcomes) and not set(ids)&set(split['reserve'])
        correct=sum(outcomes[t]['selected_baseline'] for t in ids)
        inputs=[baselines[t]['input_tokens'] for t in ids]
        chars=[len(visible[t]['prompt']) for t in ids]
        tests=[len(public_assertions(visible[t]['prompt'])) for t in ids]
        seed_matches=all(baselines[t]['seed']==int(hashlib.sha256(f"20260905:{t}:{baselines[t]['sample_index']}".encode()).hexdigest()[:8],16) for t in ids)
        assert seed_matches
        tp=sum(trigger[t] and not outcomes[t]['selected_baseline'] for t in ids)
        fp=sum(trigger[t] and outcomes[t]['selected_baseline'] for t in ids)
        groups[name]=dict(tasks=len(ids),correct=correct,accuracy=correct/len(ids),accuracy_wilson95=wilson(correct,len(ids)),
            public_failure_triggers=sum(trigger[t] for t in ids),trigger_wilson95=wilson(sum(trigger[t] for t in ids),len(ids)),
            error_detection=dict(tp=tp,fp=fp,fn=len(ids)-correct-tp,tn=correct-fp),
            median_selected_input_tokens=statistics.median(inputs),median_prompt_characters=statistics.median(chars),
            public_assertions=dict(min=min(tests),median=statistics.median(tests),max=max(tests)),candidate_seed_rule_matches=seed_matches)
        details.extend(dict(task_id=t,cohort=name,baseline_correct=outcomes[t]['selected_baseline'],trigger=trigger[t],input_tokens=baselines[t]['input_tokens'],prompt_characters=len(visible[t]['prompt'])) for t in ids)
    result=dict(scope='Post-hoc descriptive audit of already-scored cohorts; no policy fitting or new hidden evaluation',groups=groups,
        runtime_packages={n:m.get('packages') for n,m in manifests.items()},
        limitations='Marginal Wilson intervals are descriptive, not tests of equality or proof of exchangeability. No label-driven reshuffling. Original pilot20 omitted from primary cohort comparison because adaptively used during method development. Same generation seeds do not imply identical task difficulty or counterfactual outcomes.',
        source_hashes={str(p.relative_to(ROOT)):sha256(p) for p in sources})
    out=ROOT/'runs/cohort-audit-20260920';out.mkdir(exist_ok=True)
    write_json(out/'summary.json',result);write_json(out/'task-covariates.json',details)
    print(json.dumps(groups,indent=2))


if __name__=='__main__':main()

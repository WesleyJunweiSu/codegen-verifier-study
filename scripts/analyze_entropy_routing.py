"""Train-fold entropy quantiles, held-out routing; saved development data only."""
import hashlib
import json
import math
import random
import statistics
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from verifier_study.io import read_jsonl,write_json,sha256


def threshold(values, fraction):
    finite=sorted((x for x in values if x is not None and math.isfinite(x)),reverse=True)
    return finite[math.ceil(fraction*len(finite))-1] if finite else None


def confusion(rows, selected):
    tp=sum(r['error'] and r['task_id'] in selected for r in rows)
    fp=sum(not r['error'] and r['task_id'] in selected for r in rows)
    fn=sum(r['error'] for r in rows)-tp;tn=len(rows)-tp-fp-fn
    return dict(tp=tp,fp=fp,fn=fn,tn=tn,triggers=tp+fp,recall=tp/(tp+fn),precision=tp/(tp+fp) if tp+fp else None)


def main():
    run=ROOT/'runs/mbpp-matched-budget-development-20260915'
    cp=ROOT/'configs/entropy-routing-development.json';cfg=json.loads(cp.read_text())
    paths=[cp,run/'baseline-generations.jsonl',run/'task-results.json',run/'budget-plan.json',ROOT/'configs/split-manifest-v2.json',Path(__file__)]
    pool={r['task_id']:r for r in read_jsonl(paths[1])}
    labels={r['task_id']:r['selected_baseline'] for r in json.loads(paths[2].read_text())}
    triggers={r['task_id']:r['triggered'] for r in json.loads(paths[3].read_text())['tasks']}
    split=json.loads(paths[4].read_text())
    assert set(pool)==set(labels)==set(triggers)==set(split['development_primary']) and len(pool)==100
    order=sorted(pool,key=lambda t:hashlib.sha256(f'entropy-cv:20260923:{t}'.encode()).hexdigest())
    rows=[]
    for i,tid in enumerate(order):
        entropy=pool[tid]['mean_token_entropy']
        rows.append(dict(task_id=tid,fold=i%5,error=not labels[tid],public_failure=triggers[tid],
            entropy=entropy if entropy is not None and math.isfinite(entropy) else None,output_tokens=pool[tid]['output_tokens']))
    public={r['task_id'] for r in rows if r['public_failure']};chosen=set(public);folds=[]
    for fold in range(5):
        train=[r for r in rows if r['fold']!=fold and not r['public_failure']]
        test=[r for r in rows if r['fold']==fold and not r['public_failure']]
        cut=threshold([r['entropy'] for r in train],cfg['extra_training_fraction'])
        extra=[r['task_id'] for r in test if cut is not None and r['entropy'] is not None and r['entropy']>=cut]
        chosen.update(extra)
        folds.append(dict(fold=fold,training_task_ids=[r['task_id'] for r in train],test_task_ids=[r['task_id'] for r in test],threshold=cut,extra=extra))
    rng=random.Random(20260923);random_tp=[]
    for _ in range(10000):
        selected=set(public)
        for f in folds:selected.update(rng.sample(f['test_task_ids'],len(f['extra'])))
        random_tp.append(confusion(rows,selected)['tp'])
    random_tp.sort()
    usable=[r for r in rows if not r['public_failure'] and r['entropy'] is not None]
    pos=[r['entropy'] for r in usable if r['error']];neg=[r['entropy'] for r in usable if not r['error']]
    auc=sum((x>y)+0.5*(x==y) for x in pos for y in neg)/(len(pos)*len(neg)) if pos and neg else None
    correlation=statistics.correlation([r['entropy'] for r in usable],[math.log1p(r['output_tokens']) for r in usable]) if len(usable)>1 else None
    out=ROOT/'runs/entropy-routing-development-20260923';out.mkdir(exist_ok=True)
    result=dict(scope=cfg['scope'],tasks=100,missing_entropy=sum(r['entropy'] is None for r in rows),
        public_only=confusion(rows,public),entropy_out_of_fold=confusion(rows,chosen),
        matched_random=dict(repetitions=10000,mean_tp=statistics.mean(random_tp),tp_central95=[random_tp[249],random_tp[9749]],
                            interpretation='Random-route assignment distribution conditional on this dataset and fold trigger counts; not a population confidence interval'),
        public_pass_entropy_auroc_descriptive=auc,public_pass_entropy_log_output_length_pearson=correlation,
        folds=folds,source_hashes={str(p.relative_to(ROOT)):sha256(p) for p in paths},limitations=cfg['claim_limit'])
    write_json(out/'summary.json',result)
    write_json(out/'task-results.json',[dict(**r,entropy_routed=r['task_id'] in chosen) for r in rows])
    print(json.dumps({k:v for k,v in result.items() if k not in ['folds','source_hashes']},indent=2))


if __name__=='__main__':main()

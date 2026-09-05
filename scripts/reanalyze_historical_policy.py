"""Rescore the frozen historical entropy policy with Linux labels; no retuning."""
import json
import random
import sys
import argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verifier_study.io import read_jsonl,write_json

run=ROOT/"runs/historical-holdout"
parser=argparse.ArgumentParser()
parser.add_argument("--numpy-bootstrap",action="store_true",help="Also reproduce the original NumPy RNG/bootstrap algorithm")
args=parser.parse_args()
historical=read_jsonl(run/"windows-labels.jsonl")
linux={row["task_id"]:row for row in read_jsonl(run/"linux/evaluation.jsonl")}
test=[row for row in historical if row["split"]=="test"]

def auc(rows,label):
    errors=[row["entropy"] for row in rows if not label(row)]
    correct=[row["entropy"] for row in rows if label(row)]
    return sum(float(e>c)+0.5*float(e==c) for e in errors for c in correct)/(len(errors)*len(correct))

def quantile(values,q):
    values=sorted(values);position=(len(values)-1)*q;lo=int(position);hi=min(lo+1,len(values)-1)
    return values[lo]+(position-lo)*(values[hi]-values[lo])

results={}
for name,label in (("windows",lambda row:row["pass"]),("linux",lambda row:linux[row["task_id"]]["pass"])):
    accepted=[row for row in test if row["accepted"]]
    baseline=sum(label(row) for row in test)/len(test)
    selective=sum(label(row) for row in accepted)/len(accepted)
    rng=random.Random(20260709);lifts=[]
    for _ in range(10000):
        sample=rng.choices(test,k=len(test))
        kept=[row for row in sample if row["accepted"]]
        if kept: lifts.append(sum(label(row) for row in kept)/len(kept)-sum(label(row) for row in sample)/len(sample))
    results[name]={"test_tasks":len(test),"correct":sum(label(row) for row in test),"accepted":len(accepted),
        "correct_accepted":sum(label(row) for row in accepted),"baseline_accuracy":baseline,"selective_accuracy":selective,
        "realized_coverage":len(accepted)/len(test),"selective_minus_baseline_pp":100*(selective-baseline),
        "error_detection_auroc":auc(test,label),
        "lift_task_bootstrap95_pp":[100*quantile(lifts,0.025),100*quantile(lifts,0.975)]}
    if args.numpy_bootstrap:
        import numpy as np
        numpy_rng=np.random.default_rng(20260709);numpy_lifts=[]
        for _ in range(10000):
            sample=[test[i] for i in numpy_rng.integers(0,len(test),len(test))]
            kept=[row for row in sample if row["accepted"]]
            if kept: numpy_lifts.append(sum(label(row) for row in kept)/len(kept)-sum(label(row) for row in sample)/len(sample))
        results[name]["original_algorithm_bootstrap95_pp"]=[100*float(value) for value in np.quantile(numpy_lifts,[0.025,0.975])]
        results[name]["bootstrap_numpy_version"]=np.__version__
write_json(run/"policy-reanalysis.json",{"scope":"Historical exposed data; fixed accepted flags and entropy scores; no threshold retuning",
    "bootstrap":"10,000 paired task resamples, Python random.Random(20260709), interpolated 2.5/97.5 percentiles. Original blog used NumPy RNG; bootstrap realizations therefore differ.",
    "results":results})
print((run/"policy-reanalysis.json").read_text(encoding="utf-8"))

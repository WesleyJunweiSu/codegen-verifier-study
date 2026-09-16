"""All-task development outcomes and costs; no generated code execution."""
import hashlib
import json
import random
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from verifier_study.io import read_jsonl,write_json,sha256
from verifier_study.frozen_decisions import validate_decisions
from freeze_matched_score import RUN


def main():
    run=ROOT/'runs'/RUN
    plan=json.loads((run/'score-plan.json').read_text());m=json.loads((run/'linux/metadata.json').read_text())
    for field,name in [('generations_sha256','generations.jsonl'),('decisions_sha256','frozen-decisions.jsonl'),('score_plan_sha256','score-plan.json')]:assert m[field]==sha256(run/name)
    assert m['dataset_sha256']==plan['dataset_sha256']
    assert m['decision_order']=='Externally frozen decisions validated before reference loading; scorer never selects'
    assert (run/'frozen-decisions.jsonl').read_bytes()==(run/'linux/decisions.jsonl').read_bytes()
    rows=read_jsonl(run/'generations.jsonl');decisions=read_jsonl(run/'frozen-decisions.jsonl')
    validate_decisions(plan,rows,decisions)
    key=lambda r:(r['task_id'],r['sample_index'])
    ev=read_jsonl(run/'linux/evaluation.jsonl');labels={key(r):r for r in ev}
    assert len(labels)==len(ev)==len(rows)
    for row in rows:assert labels[key(row)]['code_sha256']==hashlib.sha256(row['code'].encode()).hexdigest()
    outcomes={method:{d['task_id']:labels[key(d)]['pass'] for d in decisions if d['method']==method} for method in plan['methods']}
    base=outcomes['selected_baseline'];a=outcomes['reasoning_budget2048'];b=outcomes['nonthinking_budget2048']
    stats={}
    for name,values in outcomes.items():
        stats[name]=dict(correct=sum(values.values()),tasks=100,accuracy=sum(values.values())/100,
            rescues=[t for t in base if values[t] and not base[t]],regressions=[t for t in base if base[t] and not values[t]])
    diffs=[int(a[t])-int(b[t]) for t in base];rng=random.Random(20260916)
    boot=sorted(sum(rng.choices(diffs,k=100)) for _ in range(10000))
    budget=json.loads((run/'budget-plan.json').read_text());cohorts={}
    for cohort in budget['cohorts']:
        ids={r['task_id'] for r in read_jsonl(ROOT/cohort['decisions'])}
        cohorts[cohort['run']]={name:dict(correct=sum(values[t] for t in ids),tasks=len(ids)) for name,values in outcomes.items()}
    result=dict(scope='Adaptive development100;14 treated task pairs; not independent confirmation',methods=stats,
        reasoning_minus_nonthinking=dict(wins=[t for t in base if a[t] and not b[t]],losses=[t for t in base if b[t] and not a[t]],difference_percentage_points=sum(diffs),exploratory_task_bootstrap95_pp=[boot[249],boot[9749]]),
        cohorts=cohorts,cost=json.loads((run/'generation-audit.json').read_text()),
        limitations='Identical per-task output-budget ceilings, unequal realized output/input tokens, calls and compute. Mode and sampling preset differ jointly.14 treated pairs, one seed schedule, adaptively used development tasks; no causal content attribution or independent significance claim.')
    write_json(run/'summary.json',result)
    write_json(run/'task-results.json',[dict(task_id=t,**{n:v[t] for n,v in outcomes.items()}) for t in base])
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()

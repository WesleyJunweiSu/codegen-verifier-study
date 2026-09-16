"""Validate frozen budget selection before hidden development scoring."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from verifier_study.io import read_jsonl,write_json,sha256
from verifier_study.matched_budget import select,METHODS
from verifier_study.frozen_decisions import validate_decisions
RUN='mbpp-matched-budget-development-20260915'


def main():
    run=ROOT/'runs'/RUN; plan=json.loads((run/'budget-plan.json').read_text())
    for name,digest in plan['source_hashes'].items():assert sha256(ROOT/name)==digest,name
    m=json.loads((run/'visible/metadata.json').read_text())
    assert m['hidden_benchmark_mounted'] is False and m['hidden_reference_loading'] is False
    for field,name in [('generations_sha256','generations.jsonl'),('plan_sha256','budget-plan.json'),('decisions_sha256','visible/decisions.jsonl'),('matrix_sha256','visible/candidate-test-matrix.jsonl')]:assert m[field]==sha256(run/name)
    assert m['selector_sha256']==sha256(ROOT/'src/verifier_study/matched_budget.py')
    records=read_jsonl(run/'generations.jsonl'); decisions=read_jsonl(run/'visible/decisions.jsonl')
    assert decisions==select(plan,records,read_jsonl(run/'visible/candidate-test-matrix.jsonl'))
    split=json.loads((ROOT/'configs/split-manifest-v2.json').read_text())
    assert {t['task_id'] for t in plan['tasks']}==set(split['development_primary'])
    score=dict(schema_version=1,task_ids=[t['task_id'] for t in plan['tasks']],methods=METHODS,
        generations_sha256=sha256(run/'generations.jsonl'),decisions_sha256=m['decisions_sha256'],
        dataset_sha256=split['sha256'],split_manifest_sha256=sha256(ROOT/'configs/split-manifest-v2.json'),
        visible_metadata_sha256=sha256(run/'visible/metadata.json'),freeze_script_sha256=sha256(Path(__file__)))
    validate_decisions(score,records,decisions)
    data=(run/'visible/decisions.jsonl').read_bytes()
    if (run/'frozen-decisions.jsonl').exists():assert (run/'frozen-decisions.jsonl').read_bytes()==data
    else:(run/'frozen-decisions.jsonl').write_bytes(data)
    if (run/'score-plan.json').exists():assert json.loads((run/'score-plan.json').read_text())==score
    else:write_json(run/'score-plan.json',score)
    print('Frozen100 development tasks and300 decisions; no hidden labels read')


if __name__=='__main__':main()

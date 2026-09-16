"""Public assertions only, inside restricted Linux; no hidden benchmark."""
import argparse
import json
import os
import platform
from pathlib import Path
from verifier_study.io import read_jsonl, write_jsonl, write_json, sha256
from verifier_study.matched_budget import validate_pool, select
from verifier_study.test_quality import public_assertions


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input', required=True); parser.add_argument('--output', required=True)
    args=parser.parse_args()
    assert platform.system()=='Linux' and os.environ.get('VERIFIER_ISOLATED_RUN')=='1'
    source=Path(args.input); out=Path(args.output);out.mkdir(exist_ok=True)
    plan=json.loads((source/'budget-plan.json').read_text())
    records=read_jsonl(source/'generations.jsonl');validate_pool(plan, records)
    prompts={r['task_id']:r['prompt'] for r in read_jsonl(Path('/app/mbpp-prompts.jsonl'))}
    from test_matrix_linux import check_assertion
    matrix=[]
    for row in records:
        for i, assertion in enumerate(public_assertions(prompts[row['task_id']])):
            matrix.append(dict(task_id=row['task_id'],sample_index=row['sample_index'],source='public',test_index=i,keep=True,status=check_assertion(row['code'],assertion)))
    write_jsonl(out/'candidate-test-matrix.jsonl',matrix)
    write_jsonl(out/'decisions.jsonl',select(plan,records,matrix))
    write_json(out/'metadata.json',dict(hidden_benchmark_mounted=False,hidden_reference_loading=False,
        generations_sha256=sha256(source/'generations.jsonl'),plan_sha256=sha256(source/'budget-plan.json'),
        decisions_sha256=sha256(out/'decisions.jsonl'),matrix_sha256=sha256(out/'candidate-test-matrix.jsonl'),
        selector_sha256=sha256(Path('/app/verifier_study/matched_budget.py')),runner_sha256=sha256(Path(__file__))))


if __name__=='__main__':main()

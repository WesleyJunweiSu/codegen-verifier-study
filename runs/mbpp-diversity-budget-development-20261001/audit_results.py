"""Post-batch audit of saved evidence only; no candidate execution or new labels."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'scripts')]
from verifier_study.io import read_jsonl, sha256, write_json
from verifier_study.matched_budget import validate_pool
import confirmation
import freeze_matched_score as freezer


def main():
    confirmation.load_config()
    freezer.RUN = RUN.name
    with contextlib.redirect_stdout(io.StringIO()):
        freezer.main()
    plan = json.loads((RUN/'budget-plan.json').read_text(encoding='utf-8'))
    parent = ROOT/'runs'/plan['parent_run']
    pool = read_jsonl(RUN/'generations.jsonl')
    validate_pool(plan, pool)
    scored = read_jsonl(RUN/'linux/evaluation.jsonl')
    key = lambda r: (r['task_id'], r['sample_index'])
    labels = {key(r):r for r in scored}
    assert len(labels) == len(scored) == len(pool)
    for row in pool:
        assert labels[key(row)]['code_sha256'] == hashlib.sha256(row['code'].encode()).hexdigest()
    metadata = json.loads((RUN/'linux/metadata.json').read_text(encoding='utf-8'))
    for field, filename in [('generations_sha256','generations.jsonl'),
                            ('decisions_sha256','frozen-decisions.jsonl'),
                            ('score_plan_sha256','score-plan.json')]:
        assert metadata[field] == sha256(RUN/filename)
    assert (RUN/'linux/decisions.jsonl').read_bytes() == (RUN/'frozen-decisions.jsonl').read_bytes()
    assert metadata['dataset_sha256'] == json.loads((RUN/'score-plan.json').read_text())['dataset_sha256']
    old = [r for r in read_jsonl(parent/'new-generations.jsonl') if r['sample_index']>=5]
    new = read_jsonl(RUN/'new-generations.jsonl')
    a, b = {key(r):r for r in old}, {key(r):r for r in new}
    shared = a.keys() & b.keys()
    tids = [t['task_id'] for t in plan['tasks'] if t['triggered']]
    task_rows = []
    for tid in tids:
        x=[r for r in old if r['task_id']==tid];y=[r for r in new if r['task_id']==tid]
        assert sum(r['output_tokens'] for r in x)==sum(r['output_tokens'] for r in y)==2048
        task_rows.append(dict(task_id=tid,old_distinct=len({r['code'] for r in x}),
                             new_distinct=len({r['code'] for r in y}),
                             new_oracle=any(labels[key(r)]['pass'] for r in y)))
    def cost(rows):
        return dict(calls=len(rows),input_tokens=sum(r['input_tokens'] for r in rows),
                    output_tokens=sum(r['output_tokens'] for r in rows),
                    parseable=sum(r['code_parses'] for r in rows),
                    model_wall_seconds=sum(r['wall_seconds'] for r in rows),
                    peak_allocated_vram_bytes=max(r['peak_vram_bytes'] for r in rows))
    result=dict(status='saved_evidence_verified',audited_candidates=len(pool),treated_tasks=len(tids),
                old_distinct_task_code_pairs=sum(r['old_distinct'] for r in task_rows),
                new_distinct_task_code_pairs=sum(r['new_distinct'] for r in task_rows),
                tasks_with_more_distinct=sum(r['new_distinct']>r['old_distinct'] for r in task_rows),
                new_oracle_tasks=sum(r['new_oracle'] for r in task_rows),
                shared_call_keys=len(shared),identical_code_on_shared_keys=sum(a[k]['code']==b[k]['code'] for k in shared),
                old_cost=cost(old),new_cost=cost(new),per_task=task_rows,
                interval_warning='All observed paired correctness differences are zero. The saved percentile bootstrap [0,0] is degenerate and must not be interpreted as an equivalence bound or zero uncertainty in unseen tasks/seeds.',
                cost_warning='Recorded model wall times are different desktop sessions, not a controlled latency experiment. Reasoning outputs are reused, not fresh replicated gains.',
                source_sha256={str(p.relative_to(ROOT)):sha256(p) for p in [Path(__file__),RUN/'temperature-summary.json',RUN/'generations.jsonl',RUN/'linux/evaluation.jsonl',parent/'new-generations.jsonl']})
    write_json(RUN/'audit-results.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['per_task','source_sha256']},indent=2))


if __name__=='__main__':main()

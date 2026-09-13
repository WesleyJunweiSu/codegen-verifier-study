"""Post-hoc descriptive completion audit; no generation, selection or execution."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    run = ROOT / 'runs/mbpp-confirmation-extensions-20260911'
    paths = [run/'new-generations.jsonl', run/'task-results.json']
    records = [json.loads(line) for line in paths[0].read_text(encoding='utf-8').splitlines()]
    outcomes = {r['task_id']: r for r in json.loads(paths[1].read_text(encoding='utf-8'))}
    reasoning = [r for r in records if r['sample_index'] == 5]
    control = [r for r in records if r['sample_index'] == 4]
    assert len(reasoning) == len(control) == 41
    assert {r['task_id'] for r in reasoning} == {r['task_id'] for r in control}
    rows = []
    for r in reasoning:
        t = outcomes[r['task_id']]
        assert not t['selected_baseline']
        rows.append(dict(task_id=r['task_id'], completed=r['thinking_complete'],
                         tokens=r['output_tokens'], code_parses=r['code_parses'],
                         rescue=bool(t['reasoning_resample'] and not t['selected_baseline'])))
    groups = {}
    for completed, name in [(True, 'completed'), (False, 'incomplete')]:
        group = [r for r in rows if r['completed'] == completed]
        rescues = sum(r['rescue'] for r in group)
        groups[name] = dict(attempts=len(group), rescue=rescues, no_rescue=len(group)-rescues,
                            tokens=sum(r['tokens'] for r in group),
                            parseable=sum(r['code_parses'] for r in group),
                            token_distribution=sorted(r['tokens'] for r in group))
    total = sum(r['tokens'] for r in rows)
    control_tokens = sum(r['output_tokens'] for r in control)
    rescues = sum(r['rescue'] for r in rows)
    result = dict(scope='Post-hoc descriptive; completion is post-treatment, not randomized',
                  groups=groups, nonthinking_tokens=control_tokens,
                  actual_reasoning_tokens=total, actual_token_ratio=total/control_tokens,
                  actual_extra_reasoning_tokens_per_rescue=total/rescues,
                  completed_group_tokens_per_rescue=groups['completed']['tokens']/rescues,
                  incomplete_token_fraction=groups['incomplete']['tokens']/total,
                  completed_group_to_all_control_token_ratio=groups['completed']['tokens']/control_tokens,
                  rows=rows, source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    out = ROOT/'runs/completion-audit-20260913'
    out.mkdir(exist_ok=True)
    (out/'summary.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','source_hashes')}, indent=2))


if __name__ == '__main__':
    main()

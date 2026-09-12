"""Development-only routing ablation. Pure selection; never reads correctness labels."""
from collections import defaultdict

METHODS = ['selected_baseline'] + [f'{route}_{mode}_{gate}'
    for route, gate in [('public', 'strict'), ('expanded', 'strict'), ('expanded', 'tie')]
    for mode in ['nonthinking', 'reasoning']]


def select_routing(plan, matrix):
    public = defaultdict(dict)
    for row in matrix:
        if row['source'] != 'public':
            continue
        key = row['task_id'], row['sample_index']
        assert row['test_index'] not in public[key], 'Duplicate public outcome'
        public[key][row['test_index']] = row['status']
    tasks = plan['tasks']
    assert len(tasks) == len({t['task_id'] for t in tasks})
    result = []
    for task in tasks:
        tid, base = task['task_id'], task['selected_index']
        original = public[tid, base]
        assert original and task['public_failed'] == any(s != 'pass' for s in original.values())
        assert task['triggered'] == (task['public_failed'] or task['consensus_fraction'] < 1)
        score = sum(s == 'pass' for s in original.values())
        for method in METHODS:
            chosen = base
            if method != 'selected_baseline':
                route, mode, gate = method.split('_')
                triggered = task['public_failed'] if route == 'public' else task['triggered']
                if triggered:
                    index = {'nonthinking': 5, 'reasoning': 7}[mode]
                    observed = public[tid, index]
                    assert set(observed) == set(original), 'Missing/mismatched public outcomes'
                    new_score = sum(s == 'pass' for s in observed.values())
                    # Tie acceptance requires every public assertion to pass.
                    # Partial-pass ties retain the baseline.
                    if new_score > score or (gate == 'tie' and new_score == len(original)):
                        chosen = index
            result.append(dict(task_id=tid, method=method, sample_index=chosen,
                               accepted=True, replaced=chosen != base))
    return result

"""Apply the frozen four-arm transfer using public example outcomes only."""
from collections import defaultdict


def select_transfer(plan, matrix):
    public = defaultdict(dict)
    for row in matrix:
        if row['source'] != 'public':
            continue
        key = row['task_id'], row['sample_index']
        assert row['test_index'] not in public[key], 'Duplicate public outcome'
        public[key][row['test_index']] = row['status']
    tasks = plan['tasks']
    assert len(tasks) == len({t['task_id'] for t in tasks}), 'Duplicate tasks'
    arms = plan['arms']
    assert len(arms) == len({a['sample_index'] for a in arms}) == len({a['method'] for a in arms})
    result = []
    for task in tasks:
        tid, base = task['task_id'], task['selected_index']
        original = public[tid, base]
        assert original, 'Missing original public outcomes'
        assert task['triggered'] == any(s != 'pass' for s in original.values()), 'Trigger changed on reevaluation'
        base_score = sum(s == 'pass' for s in original.values())
        for method, index in [('selected_baseline', base)] + [(a['method'], a['sample_index']) for a in arms]:
            selected = base
            if task['triggered'] and method != 'selected_baseline':
                observed = public[tid, index]
                assert set(observed) == set(original), 'Incomplete or mismatched public outcomes'
                if sum(s == 'pass' for s in observed.values()) > base_score:
                    selected = index
            result.append({'task_id': tid, 'method': method, 'sample_index': selected, 'accepted': True,
                           'triggered': task['triggered'], 'replaced': selected != base})
    return result

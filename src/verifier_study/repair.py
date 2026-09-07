"""Public-feedback repair decisions. This module never consumes correctness labels."""
from collections import defaultdict


def select_repair(plan, matrix):
    public = defaultdict(list)
    for row in matrix:
        if row['source'] == 'public':
            public[row['task_id'], row['sample_index']].append(row['status'])
    decisions = []
    for task in plan['tasks']:
        task_id, original = task['task_id'], task['selected_index']
        original_status = public[task_id, original]
        assert original_status, 'Missing public tests'
        score = sum(s == 'pass' for s in original_status)
        for method, index in [('selected_baseline', original), ('public_feedback_repair', 4), ('extra_sample_control', 5)]:
            selected = original
            if task['triggered'] and method != 'selected_baseline':
                status = public[task_id, index]
                assert len(status) == len(original_status), 'Incomplete new-candidate public matrix'
                if sum(s == 'pass' for s in status) > score:
                    selected = index
            decisions.append({'task_id': task_id, 'method': method, 'sample_index': selected,
                              'triggered': task['triggered'], 'replaced': selected != original})
    return decisions

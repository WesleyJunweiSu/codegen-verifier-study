"""Pure validation and selection for the frozen variable-size budget pools."""
METHODS = ['selected_baseline', 'reasoning_budget2048', 'nonthinking_budget2048']


def validate_pool(plan, records):
    keys = {(r['task_id'], r['sample_index']) for r in records}
    assert len(keys) == len(records)
    assert {r['task_id'] for r in records} == {t['task_id'] for t in plan['tasks']}
    for task in plan['tasks']:
        rows = [r for r in records if r['task_id'] == task['task_id']]
        base = [r for r in rows if r['sample_index'] == task['selected_index']]
        assert len(base) == 1 and task['selected_index'] < 4
        extra = [r for r in rows if r not in base]
        if not task['triggered']:
            assert not extra
            continue
        reason = [r for r in extra if r['sample_index'] == 4]
        iid = sorted([r for r in extra if r['sample_index'] >= 5], key=lambda r: r['sample_index'])
        assert len(reason) == 1 and 0 < reason[0]['output_tokens'] <= 2048
        assert len(extra) == 1 + len(iid)
        assert [r['sample_index'] for r in iid] == list(range(5, 5+len(iid)))
        remaining = 2048
        for r in iid:
            assert 0 < r['output_tokens'] <= min(768, remaining)
            remaining -= r['output_tokens']
        assert remaining == 0


def select(plan, records, matrix):
    validate_pool(plan, records)
    public = [r for r in matrix if r['source'] == 'public']
    keys = {(r['task_id'], r['sample_index']) for r in records}
    assert {(r['task_id'], r['sample_index']) for r in public} == keys
    assert len({(r['task_id'], r['sample_index'], r['test_index']) for r in public}) == len(public)
    scores = {}
    for task in plan['tasks']:
        tid = task['task_id']; indices = sorted(i for t, i in keys if t == tid)
        expected_tests = None
        for index in indices:
            rows = [r for r in public if (r['task_id'], r['sample_index']) == (tid, index)]
            tests = {r['test_index'] for r in rows}
            assert tests and tests == set(range(len(tests)))
            if expected_tests is None: expected_tests = tests
            assert tests == expected_tests
            scores[tid, index] = sum(r['status'] == 'pass' for r in rows)
        assert task['triggered'] == (scores[tid, task['selected_index']] < len(expected_tests))
    decisions = []
    for task in plan['tasks']:
        tid = task['task_id']; base = task['selected_index']
        for method in METHODS:
            selected = base
            if task['triggered'] and method != 'selected_baseline':
                candidates = [i for t, i in keys if t == tid and (i == 4 if method == 'reasoning_budget2048' else i >= 5)]
                best = min(candidates, key=lambda i: (-scores[tid, i], i))
                if scores[tid, best] > scores[tid, base]: selected = best
            decisions.append(dict(task_id=tid, method=method, sample_index=selected, accepted=True))
    return decisions

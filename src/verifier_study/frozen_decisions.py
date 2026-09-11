"""Validate complete decisions before a scorer can read hidden references."""


def validate_decisions(plan, candidates, decisions):
    assert plan['schema_version'] == 1
    tasks, methods = plan['task_ids'], plan['methods']
    assert tasks and methods and len(tasks) == len(set(tasks)) and len(methods) == len(set(methods))
    keys = {(r['task_id'], r['sample_index']) for r in candidates}
    assert len(keys) == len(candidates) and {r['task_id'] for r in candidates} == set(tasks)
    expected = {(t, m) for t in tasks for m in methods}
    actual = {(r['task_id'], r['method']) for r in decisions}
    assert actual == expected and len(actual) == len(decisions), 'Incomplete/duplicate frozen decision set'
    for row in decisions:
        assert type(row['accepted']) is bool
        if row['accepted']:
            assert (row['task_id'], row['sample_index']) in keys, 'Selected candidate absent'
        else:
            assert row['sample_index'] is None, 'Abstention must not select a candidate'

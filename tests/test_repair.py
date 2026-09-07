import unittest
from verifier_study.repair import select_repair


class RepairTests(unittest.TestCase):
    def test_public_improvement_only_and_original_ties(self):
        plan = {'tasks': [{'task_id': 'A', 'selected_index': 1, 'triggered': True},
                          {'task_id': 'B', 'selected_index': 0, 'triggered': False}]}
        matrix = [{'task_id': t, 'sample_index': i, 'source': 'public', 'status': s}
                  for t, i, s in [('A', 1, 'fail'), ('A', 4, 'pass'), ('A', 5, 'fail'), ('B', 0, 'pass')]]
        matrix.append({'task_id': 'A', 'sample_index': 5, 'source': 'generated', 'status': 'pass'})
        decisions = select_repair(plan, matrix)
        self.assertEqual([d['sample_index'] for d in decisions], [1, 4, 1, 0, 0, 0])

    def test_incomplete_matrix_rejected(self):
        plan = {'tasks': [{'task_id': 'A', 'selected_index': 0, 'triggered': True}]}
        with self.assertRaises(AssertionError):
            select_repair(plan, [{'task_id': 'A', 'sample_index': 0, 'source': 'public', 'status': 'fail'}])

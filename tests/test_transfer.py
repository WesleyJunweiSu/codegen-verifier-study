import unittest
from verifier_study.transfer import select_transfer


class TransferTests(unittest.TestCase):
    def setUp(self):
        self.plan = {'tasks': [{'task_id': 'A', 'selected_index': 2, 'triggered': True},
                              {'task_id': 'B', 'selected_index': 0, 'triggered': False}],
                     'arms': [{'method': str(i), 'sample_index': i} for i in range(4, 8)]}
        self.matrix = [{'task_id': t, 'sample_index': i, 'test_index': 0, 'source': 'public', 'status': s}
                       for t, i, s in [('A', 2, 'fail'), ('A', 4, 'pass'), ('A', 5, 'fail'), ('A', 6, 'fail'), ('A', 7, 'pass'), ('B', 0, 'pass')]]

    def test_four_arms_ties_and_nontriggered_fallback(self):
        self.matrix.append({'task_id': 'A', 'sample_index': 5, 'test_index': 0, 'source': 'generated', 'status': 'pass'})
        self.assertEqual([r['sample_index'] for r in select_transfer(self.plan, self.matrix)], [2, 4, 2, 2, 7, 0, 0, 0, 0, 0])

    def test_missing_arm_rejected(self):
        with self.assertRaises(AssertionError): select_transfer(self.plan, self.matrix[0:4] + self.matrix[5:])

    def test_duplicate_public_outcome_rejected(self):
        with self.assertRaises(AssertionError): select_transfer(self.plan, self.matrix + [self.matrix[0]])

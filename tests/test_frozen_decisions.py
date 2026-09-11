import unittest
from verifier_study.frozen_decisions import validate_decisions


class FrozenDecisionTests(unittest.TestCase):
    def setUp(self):
        self.plan = {'schema_version': 1, 'task_ids': ['A'], 'methods': ['first', 'abstain']}
        self.candidates = [{'task_id': 'A', 'sample_index': 0}]
        self.decisions = [{'task_id': 'A', 'method': 'first', 'sample_index': 0, 'accepted': True},
                          {'task_id': 'A', 'method': 'abstain', 'sample_index': None, 'accepted': False}]

    def test_complete_and_explicit_abstention(self):
        validate_decisions(self.plan, self.candidates, self.decisions)

    def test_missing_duplicate_and_invalid_selections(self):
        for rows in [self.decisions[:1], self.decisions + self.decisions[:1],
                     [{**self.decisions[0], 'sample_index': 1}, self.decisions[1]],
                     [self.decisions[0], {**self.decisions[1], 'sample_index': 0}]]:
            with self.assertRaises(AssertionError): validate_decisions(self.plan, self.candidates, rows)

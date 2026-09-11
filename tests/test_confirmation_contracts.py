import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from visible_linux import expected_candidate_keys, include_first_decisions


class ConfirmationContractTests(unittest.TestCase):
    def test_all_original_candidates_and_only_triggered_extensions(self):
        plan = {'base_candidate_mode': 'all_four', 'tasks': [
            {'task_id': 'A', 'selected_index': 2, 'triggered': True},
            {'task_id': 'B', 'selected_index': 1, 'triggered': False}],
            'arms': [{'sample_index': 4}, {'sample_index': 5}]}
        keys = expected_candidate_keys(['A', 'B'], plan)
        self.assertEqual(len(keys), 10)
        self.assertTrue({('A', 0), ('B', 0), ('A', 4), ('A', 5)} <= keys)
        self.assertNotIn(('B', 4), keys)

    def test_first_baseline_is_prespecified_and_not_duplicated(self):
        rows = include_first_decisions(['A', 'B'], [])
        self.assertEqual([(r['task_id'], r['sample_index']) for r in rows], [('A', 0), ('B', 0)])
        with self.assertRaises(AssertionError): include_first_decisions(['A', 'B'], rows)

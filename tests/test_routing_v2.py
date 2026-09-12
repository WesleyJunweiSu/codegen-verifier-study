import unittest
from verifier_study.routing_v2 import select_routing


class RoutingTests(unittest.TestCase):
    def run_case(self, baseline, new, public_failed=False, fraction=0.8):
        plan = {'tasks': [dict(task_id='x', selected_index=0, public_failed=public_failed,
                              consensus_fraction=fraction, triggered=public_failed or fraction < 1)]}
        matrix = [dict(task_id='x', sample_index=i, source='public', test_index=j, status=s)
                  for i, statuses in [(0, baseline), (5, new), (7, new)] for j, s in enumerate(statuses)]
        return {r['method']: r['sample_index'] for r in select_routing(plan, matrix)}

    def test_all_pass_tie_only_expanded_tie_replaces(self):
        rows = self.run_case(['pass'], ['pass'])
        self.assertEqual(rows['expanded_reasoning_tie'], 7)
        self.assertEqual(rows['expanded_reasoning_strict'], 0)
        self.assertEqual(rows['public_reasoning_strict'], 0)

    def test_partial_tie_and_regression_fall_back(self):
        for new in [['pass', 'fail'], ['fail', 'fail']]:
            rows = self.run_case(['pass', 'fail'], new, public_failed=True)
            self.assertTrue(all(index == 0 for index in rows.values()))

    def test_improvement_rescued_in_every_extension(self):
        rows = self.run_case(['fail'], ['pass'], public_failed=True)
        self.assertEqual(rows['public_reasoning_strict'], 7)
        self.assertEqual(rows['expanded_nonthinking_tie'], 5)

    def test_nontrigger_and_failed_alternative_retained(self):
        for new, fraction in [(['pass'], 1), (['fail'], 0.8)]:
            self.assertTrue(all(i == 0 for i in self.run_case(['pass'], new, fraction=fraction).values()))

    def test_missing_outcomes_rejected(self):
        with self.assertRaises(AssertionError):
            self.run_case(['pass'], [])


if __name__ == '__main__': unittest.main()

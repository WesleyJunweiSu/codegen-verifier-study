import unittest
from verifier_study.paired_inference import exact_mcnemar


class PairedInferenceTests(unittest.TestCase):
    def test_no_discordance_not_evidence_of_difference(self):
        result = exact_mcnemar([True, False], [True, False])
        self.assertEqual(result['exact_two_sided_p'], 1)
        self.assertEqual(result['discordant_tasks'], 0)

    def test_six_directional_discordances_and_symmetry(self):
        a, b = [True]*6, [False]*6
        result = exact_mcnemar(a, b)
        self.assertEqual(result['exact_two_sided_p'], 0.03125)
        reverse = exact_mcnemar(b, a)
        self.assertEqual(reverse['exact_two_sided_p'], result['exact_two_sided_p'])
        self.assertEqual(reverse['accuracy_difference'], -1)

    def test_balanced_discordance(self):
        self.assertEqual(exact_mcnemar([True, False], [False, True])['exact_two_sided_p'], 1)

    def test_missing_or_nonboolean_outcomes_rejected(self):
        for a, b in [([], []), ([True], [True, False]), ([True], [None]), ([1], [False])]:
            with self.assertRaises(ValueError): exact_mcnemar(a, b)

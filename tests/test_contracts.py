import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verifier_study.io import read_jsonl
from verifier_study.test_quality import assess_tests,parse_assertions


class ContractTests(unittest.TestCase):
    def test_generator_data_excludes_oracles(self):
        for row in read_jsonl(ROOT/"data/prompts/mbpp-v0.2.0.jsonl"):
            self.assertEqual(set(row),{"task_id","prompt","entry_point"})

    def test_split_is_disjoint_and_complete(self):
        split=json.loads((ROOT/"configs/split-manifest.json").read_text())
        parts=[set(split[key]) for key in ["development","calibration","confirmation","reserve"]]
        self.assertEqual(sum(map(len,parts)),378)
        self.assertEqual(len(set.union(*parts)),378)
        self.assertTrue(set(split["pilot"])<=parts[0])

    def test_public_conflict_is_filtered_without_hidden_oracle(self):
        results=assess_tests(["assert f(1) == 3","assert f(2) == 4"],"assert f(1) == 2","f")
        self.assertFalse(results[0]["keep"])
        self.assertTrue(results[1]["keep"])

    def test_unknown_expectation_is_not_claimed_valid(self):
        result=assess_tests(["assert f(77) == 999"],"assert f(1) == 2","f")
        self.assertTrue(result[0]["keep"])
        self.assertNotIn("correct",result[0])

    def test_duplicate_and_self_oracle(self):
        results=assess_tests(["assert f(1)==2","assert f(1) == 2","assert f(7)==f(7)"],"","f")
        self.assertTrue(results[0]["keep"])
        self.assertIn("duplicate",results[1]["reasons"])
        self.assertIn("tautology",results[2]["reasons"])

    def test_parser_never_executes_statements(self):
        assertions,errors=parse_assertions("raise RuntimeError('must not execute')\nassert f(1)==2")
        self.assertEqual(len(assertions),1)
        self.assertEqual(errors,["non_assert_statement:Raise"])


if __name__=="__main__": unittest.main()

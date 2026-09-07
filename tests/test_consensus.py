import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from verifier_study.consensus import literal_calls,select_consensus
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from combine_public_consensus import select as select_public_consensus


class ConsensusContracts(unittest.TestCase):
    def test_composition_uses_public_evidence_before_consensus(self):
        consensus=[{"task_id":"t","method":"execution_consensus","scores":{"0":{"fraction":0.0},"1":{"fraction":1.0}}}]
        public=[{"task_id":"t","sample_index":0,"status":"pass"},{"task_id":"t","sample_index":1,"status":"fail"}]
        self.assertEqual(select_public_consensus(public,consensus)[0]["sample_index"],0)
        public[1]["status"]="pass"
        self.assertEqual(select_public_consensus(public,consensus)[0]["sample_index"],1)

    def test_expected_values_do_not_change_extracted_inputs(self):
        a,_=literal_calls(["assert f([1,2], n=2)==999"],"f")
        b,_=literal_calls(["assert f([1,2], n=2)==-123"],"f")
        self.assertEqual(a,b)

    def test_dynamic_arguments_are_rejected_without_execution(self):
        calls,rejected=literal_calls(["assert f(open('secret'))==0","assert f(2)==3","assert f(2) == 4"],"f")
        self.assertEqual(len(calls),1)
        self.assertEqual(rejected,1)
        self.assertEqual(calls[0]["call"],"f(2)")

    def test_shared_failure_has_no_consensus_vote(self):
        candidates=[{"task_id":"t","sample_index":i,"code_sha256":str(i)} for i in range(3)]
        inputs=[{"task_id":"t","input_index":0}]
        pairs=[{"task_id":"t","input_index":0,"sample_a":i,"sample_b":j,"status":"not_comparable"}
               for i in range(3) for j in range(i+1,3)]
        rows=select_consensus(candidates,inputs,pairs)
        self.assertTrue(all(row["sample_index"]==0 for row in rows))
        self.assertTrue(all(score["fraction"]==0 for row in rows for score in row["scores"].values()))

    def test_duplicate_code_does_not_vote_for_itself_in_unique_variant(self):
        candidates=[{"task_id":"t","sample_index":i,"code_sha256":code} for i,code in enumerate(["a","a","b"])]
        inputs=[{"task_id":"t","input_index":0}]
        pairs=[{"task_id":"t","input_index":0,"sample_a":i,"sample_b":j,"status":"pass" if (i,j)==(0,1) else "fail"}
               for i in range(3) for j in range(i+1,3)]
        methods={row["method"]:row for row in select_consensus(candidates,inputs,pairs)}
        self.assertEqual(methods["execution_consensus"]["scores"][0]["fraction"],.5)
        self.assertEqual(methods["unique_code_consensus"]["scores"][0]["fraction"],0)


if __name__=="__main__": unittest.main()

import unittest
from verifier_study.matched_budget import select,validate_pool


class MatchedBudgetTest(unittest.TestCase):
    def setUp(self):
        self.plan={'tasks':[dict(task_id='x',selected_index=0,triggered=True)]}
        self.rows=[dict(task_id='x',sample_index=i,output_tokens=n) for i,n in [(0,20),(4,800),(5,768),(6,768),(7,512)]]

    def matrix(self,scores):
        return [dict(task_id='x',sample_index=i,source='public',test_index=j,status='pass' if j<scores[i] else 'fail') for i in [0,4,5,6,7] for j in range(2)]

    def test_strict_improvement_and_earliest_tie(self):
        result=select(self.plan,self.rows,self.matrix({0:1,4:1,5:2,6:2,7:0}))
        self.assertEqual([r['sample_index'] for r in result],[0,0,5])

    def test_missing_assertion_rejected(self):
        with self.assertRaises(AssertionError):select(self.plan,self.rows,self.matrix({i:0 for i in [0,4,5,6,7]})[:-1])

    def test_over_budget_rejected(self):
        self.rows[-1]['output_tokens']=513
        with self.assertRaises(AssertionError):validate_pool(self.plan,self.rows)


if __name__=='__main__':unittest.main()

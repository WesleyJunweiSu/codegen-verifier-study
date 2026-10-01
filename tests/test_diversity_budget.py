import unittest
from diversity_budget import validate_partial, seed_for


class DiversityResumeTest(unittest.TestCase):
    def row(self,index=5,tokens=768):
        return dict(task_id='fixture',sample_index=index,output_tokens=tokens,
                    seed=seed_for('fixture',index-5),generation_kind='nonthinking_temperature1_budget2048')

    def test_valid_partial_and_exact_budget(self):
        validate_partial([],['fixture'])
        validate_partial([self.row(),self.row(6),self.row(7,512)],['fixture'])

    def test_rejects_resume_corruption(self):
        for rows in [[self.row(),self.row()], [self.row(6)], [self.row(5,769)],
                     [self.row(),self.row(6),self.row(7,513)]]:
            with self.subTest(rows=rows),self.assertRaises(AssertionError):validate_partial(rows,['fixture'])
        r=self.row();r['seed']+=1
        with self.assertRaises(AssertionError):validate_partial([r],['fixture'])
        with self.assertRaises(AssertionError):validate_partial([self.row()],['other'])

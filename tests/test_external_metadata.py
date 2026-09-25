import unittest

from census_external_dates import census, project


class MetadataProjectionTest(unittest.TestCase):
    def test_never_accesses_non_metadata_fields(self):
        class Guarded(dict):
            def __getitem__(self, key):
                if key not in ("platform", "question_id", "contest_date", "difficulty"):
                    raise AssertionError("Attempt to access task content")
                return super().__getitem__(key)
        record = Guarded(platform="fixture", question_id="1", contest_date="2025-05-20T00:00:00", difficulty="easy",
                         private_test_cases="deliberately invalid encoded payload", question_content="excluded")
        result = project(record)
        self.assertEqual(set(result), {"platform", "question_id", "contest_date", "difficulty"})
        summary, eligible = census([result])
        self.assertEqual(summary["eligible_tasks"], 1)
        self.assertEqual(eligible, [result])

    def test_boundary_and_duplicates(self):
        rows = [dict(platform="fixture", question_id=str(i), contest_date=date, difficulty="easy")
                for i, date in enumerate(["2025-05-19T23:59:59", "2025-05-20T00:00:00"])]
        self.assertEqual(census(rows)[0]["eligible_tasks"], 1)
        with self.assertRaises(ValueError):
            census(rows + rows)


if __name__ == "__main__":
    unittest.main()

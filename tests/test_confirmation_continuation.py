"""No network/model calls: verify dispatch recovery avoids duplicate Actions jobs."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import continue_confirmation as runner


class ContinuationTests(unittest.TestCase):
    def test_recorded_job_is_imported_without_redispatch(self):
        state = {'jobs': {'visible': {'source_commit': 'abc', 'run_id': '123'}}}
        def fake_api(operation, *args):
            if operation == 'jobs': return [{'conclusion': 'success'}]
            if operation == 'artifacts': return [{'id': 7, 'name': 'visible-evidence', 'expired': False}]
            self.fail('Unexpected API call: '+operation)
        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, 'api', side_effect=fake_api), \
             patch.object(runner, 'python') as commands, patch.object(runner, 'checkpoint'):
            runner.workflow(state, 'visible', 'visible-evidence.yml', 'run', 'visible-evidence', Path(tmp)/'out', 'new-head')
        self.assertFalse(any('dispatch' in call.args for call in commands.call_args_list))
        imported = commands.call_args_list[-1].args
        self.assertIn('123', imported)
        self.assertIn('abc', imported)

    def test_uncertain_dispatch_is_not_repeated(self):
        state = {'jobs': {'visible': {'source_commit': 'abc', 'dispatch_pending': True}}}
        with tempfile.TemporaryDirectory() as tmp, patch.object(runner, 'api', return_value=[]), \
             patch.object(runner, 'python') as commands, patch.object(runner.time, 'sleep'), \
             patch.object(runner, 'checkpoint'):
            with self.assertRaisesRegex(AssertionError, 'Dispatch uncertain'):
                runner.workflow(state, 'visible', 'visible-evidence.yml', 'run', 'visible-evidence', Path(tmp)/'out', 'abc')
        commands.assert_not_called()


if __name__ == '__main__': unittest.main()

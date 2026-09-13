"""Finish the development concise batch after its current generator exits."""
import argparse
import json
import time
from pathlib import Path
import continue_confirmation as flow

RUN = 'mbpp-concise-development-20260913'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--generator-pid', type=int)
    args = parser.parse_args()
    run = flow.ROOT/'runs'/RUN
    flow.JOURNAL = run/'continuation-state.json'
    state = json.loads(flow.JOURNAL.read_text()) if flow.JOURNAL.exists() else dict(jobs={})
    if not args.execute or state.get('stage') == 'complete':
        print(json.dumps(state, indent=2)); return
    try:
        flow.checkpoint(state, 'waiting_for_current_generator')
        if not (run/'generations.jsonl').exists():
            import psutil
            assert args.generator_pid, 'Provide the existing generator pid, not a new generation command'
            process = psutil.Process(args.generator_pid)
            started = process.create_time()
            for _ in range(2880):
                if not psutil.pid_exists(args.generator_pid): break
                if psutil.Process(args.generator_pid).create_time() != started: break
                time.sleep(15)
            else: raise TimeoutError('Generator did not exit within the bounded wait')
        assert (run/'generations.jsonl').exists(), 'Generator exited without a complete batch'
        records = flow.read_jsonl(run/'generations.jsonl')
        plan = json.loads((run/'repair-plan.json').read_text())
        expected = {(t['task_id'], t['selected_index']) for t in plan['tasks']}
        expected |= {(t['task_id'], a['sample_index']) for t in plan['tasks'] if t['triggered'] for a in plan['arms']}
        assert len(records) == len(expected) == 46 and {(r['task_id'], r['sample_index']) for r in records} == expected
        source = flow.commit([str(run.relative_to(flow.ROOT))], 'Record completed development concise-instruction inputs')
        flow.workflow(state, 'concise_visible', 'visible-evidence.yml', RUN, 'visible-evidence', run/'visible', source)
        flow.python('freeze_score_inputs.py', '--run', RUN)
        source = flow.commit([str(run.relative_to(flow.ROOT))], 'Freeze development concise decisions before scoring')
        flow.workflow(state, 'concise_score', 'score-frozen.yml', RUN, 'frozen-scoring', run/'linux', source)
        flow.checkpoint(state, 'analyzing_complete_development_concise_batch')
        flow.python('analyze_concise_development.py')
        flow.checkpoint(state, 'complete')
        flow.commit([str(run.relative_to(flow.ROOT))], 'Record development concise-instruction results with all controls')
    except Exception as error:
        state.update(failure_type=type(error).__name__, failure_message=str(error))
        flow.checkpoint(state, 'stopped_inspect_before_resume')
        raise


if __name__ == '__main__': main()

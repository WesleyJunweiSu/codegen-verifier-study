"""Freeze final settings and existing split IDs without reading confirmation task fields."""
import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from verifier_study.io import sha256, write_json


def main():
    target = ROOT/'configs/confirmation-protocol.json'
    if target.exists():
        print('Confirmation protocol already frozen; do not rewrite it.'); return
    split = json.loads((ROOT/'configs/split-manifest.json').read_text())
    ids = split['confirmation']
    assert len(ids) == len(set(ids)) == 180
    assert not set(ids) & set(split['development'] + split['calibration'] + split['reserve'])
    sources = ['scripts/confirmation.py', 'scripts/analyze_confirmation.py', 'scripts/freeze_score_inputs.py',
        'scripts/visible_linux.py', 'scripts/evaluate_linux.py', 'scripts/consensus_linux.py',
        'scripts/combine_public_consensus.py', 'scripts/generate_development.py', 'scripts/generate_tests.py',
        'scripts/analyze_results.py', 'src/verifier_study/generation.py', 'src/verifier_study/reasoning_generation.py',
        'src/verifier_study/test_quality.py', 'src/verifier_study/selection.py', 'src/verifier_study/consensus.py',
        'src/verifier_study/transfer.py', 'src/verifier_study/frozen_decisions.py', 'src/verifier_study/paired_inference.py',
        'src/verifier_study/io.py', 'scripts/test_matrix_linux.py', 'configs/model-fingerprint.json', 'configs/split-manifest.json']
    runtime = json.loads((ROOT/'runs/mbpp-development40-repair-20260908/manifest.json').read_text())['packages']
    config = {'schema_version': 1, 'recorded_utc': datetime.datetime.now(datetime.UTC).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'phase': 'Final prespecified confirmation; no confirmation correctness labels inspected',
        'base_run': 'mbpp-confirmation-20260911', 'extension_run': 'mbpp-confirmation-extensions-20260911',
        'task_ids': ids, 'dataset': 'MBPP+ v0.2.0', 'dataset_sha256': split['sha256'],
        'source_hashes': {name: sha256(ROOT/name) for name in sources}, 'runtime_packages': runtime,
        'model': 'Fingerprint-verified Qwen3-4B BF16, one local CUDA model at a time',
        'base_generation': {'candidates_per_task': 4, 'temperature': 0.7, 'top_p': 0.8, 'top_k': 20, 'max_new_tokens': 768,
            'candidate_seed_rule': "sha256('20260905:{task_id}:{sample_index}')[:8] as hex integer",
            'test_seed_rule': "sha256('test:20260905:{task_id}')[:8] as hex integer",
            'test_responses_per_task': 1, 'test_instruction': 'Exact existing eight-assertion public-spec prompt with existing AST comparison normalization'},
        'selection': 'Existing public-first execution-consensus selection, smallest sample index on ties',
        'trigger': 'Selected baseline fails at least one public assertion; no hidden-failure trigger',
        'replacement': 'Strictly more passed public assertions; otherwise retain selected baseline',
        'arms': [
            {'method': 'nonthinking_resample', 'sample_index': 4, 'thinking': False, 'temperature': 0.7, 'top_p': 0.8, 'top_k': 20, 'max_new_tokens': 768},
            {'method': 'reasoning_resample', 'sample_index': 5, 'thinking': True, 'temperature': 0.6, 'top_p': 0.95, 'top_k': 20, 'max_new_tokens': 2048}],
        'extension_prompt': 'Exact original independent solution prompt, no feedback or analyst hints',
        'extension_seed_rule': "sha256('confirmation:20260911:extension:{task_id}')[:8] as hex integer, same seed in both arms",
        'reported_methods': ['first', 'selected_baseline', 'nonthinking_resample', 'reasoning_resample'],
        'primary_comparison': 'Conditional reasoning resampling minus conditional non-thinking resampling, correct answers / all 180 tasks',
        'primary_analysis': {'test': 'Two-sided exact McNemar on paired task correctness', 'alpha': 0.05,
            'no_discordant_pairs_p': 1, 'interval': '10,000 task bootstrap replicates; Python random seed 20260905; existing paired_interval implementation',
            'method_intervals': 'Wilson 95%', 'other_comparisons': 'Descriptive secondary outcomes; do not promote a winner after scoring'},
        'failure_policy': 'Retain all 180 tasks; capped/malformed/empty generations are failures; unfinished reasoning gives empty code; no retries or cap extensions; failed extension falls back',
        'label_boundary': 'Visible-only baseline and extension stages; freeze every final decision before hidden dataset scoring; no interim correctness analysis, optional stopping or retuning',
        'budget': 'No paid services. Guard requires 9216 MiB free. Exactly one extra call per triggered task per arm; actual input/output tokens, wall time and memory reported, not a fixed-compute claim',
        'rationale': '20-task development reasoning resample 17/20 vs nonthinking 12/20; remaining 40 tasks 33/40 vs 32/40. Feedback had no additional gain on the new cohort. All development results retained; this choice precedes confirmation outcomes.',
        'limitations': 'One model, one public benchmark, one seed schedule; pretraining contamination possible; small effects may be inconclusive with 180 tasks; no novelty or deployment claim'}
    write_json(target, config)
    print('Frozen 180 confirmation IDs, two extension arms and one primary comparison; no task text or labels read.')


if __name__ == '__main__': main()

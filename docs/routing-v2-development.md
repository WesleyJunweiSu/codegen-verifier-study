# Development routing ablation

This experiment follows inspection of the completed 40-task development results. It is adaptive development, not another independent confirmation. The existing 180-task confirmation protocol remains unchanged.

The original public-failure trigger detects 3 of 8 baseline errors. Five incorrect answers pass the public examples. Trigger expansion alone cannot repair them: the old replacement gate requires strictly more public passes, which is impossible once all examples already pass.

## Screening evidence, not answer accuracy

Positive means an incorrect baseline answer. Counts cover all 40 additional development tasks.

| Trigger | TP | FP | FN | TN | Error recall | Error precision |
|---|---:|---:|---:|---:|---:|---:|
| Public failure | 3 | 0 | 5 | 32 | 37.5% | 100% |
| Public failure or execution disagreement | 5 | 1 | 3 | 31 | 62.5% | 83.3% |
| Public failure or generated-test failure | 6 | 13 | 2 | 19 | 75.0% | 31.6% |

Execution disagreement means the stored selected candidate's consensus fraction is below one; noncomparable executions can also lower this fraction. These are post-hoc screening diagnostics, not calibrated uncertainty estimates. The second rule adds three triggers, including one correct baseline; it must retain that case when assessing regression risk.

## Frozen development intervention

Keep all 40 tasks and the selected baseline. Generate one nonthinking resample and one reasoning resample per expanded trigger. Reuse the six already completed independent resamples on the three original public-failure triggers, with exact original seeds and outputs. Only six new model calls are needed for the three newly triggered tasks. Generated tests are byte-reused, not regenerated. The paired modes have different token budgets; this is not a fixed-compute comparison.

Report seven methods: selected baseline, then both generation modes with each of (a) public-only strict replacement, (b) expanded routing with strict replacement, and (c) expanded routing with tie acceptance. Tie acceptance replaces only when every public assertion passes; partial-pass ties retain the baseline. Preserve capped and malformed responses, with no retries or task-specific hints.

The expanded strict arm isolates routing from replacement. The public-only arms must reproduce the existing 32/40 nonthinking and 33/40 reasoning results. Report every method's accuracy, rescued and regressed task IDs, the full baseline-to-method transition matrix, and generated/reused token costs. Do not pick a winning arm and present it as independently confirmed.

## Execution

1. `scripts/generate_routing_v2.py --prepare-only` freezes visible-derived tasks and source hashes. Completed: 12 planned extension records, six reused and six pending. Preparation never reads evaluation labels or the diagnostic task-features file.
2. Once the active confirmation base process finishes and GPU headroom is available, run the same script with `--model-path C:/Users/Asuka/Documents/techblog/models/Qwen3-4B`. Do not overlap GPU jobs.
3. Commit complete inputs and dispatch `routing-development.yml` with input_run `mbpp-routing-v2-development-20260911`. Its first restricted Linux job has no hidden dataset and freezes all seven decisions. A dependent job downloads those immutable decisions, then scores against the pinned benchmark in a separate restricted container.
4. Import artifacts `routing-visible-frozen` to this run's `visible/` and `routing-frozen-scoring` to `linux/`, preserving workflow/commit metadata. Run `scripts/analyze_routing_v2.py`.

Completed 2026-09-12: all seven methods scored. Every reasoning policy remains 33/40; every nonthinking policy remains 32/40. No additional rescue or regression from expanded routing/tie acceptance. Artifacts and summary are imported. The separate frozen 180-task policy reaches 118/180 versus 107/180; it does not evaluate this adaptive replacement policy. See report v0.8.

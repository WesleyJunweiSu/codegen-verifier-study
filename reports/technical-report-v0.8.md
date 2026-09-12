# Conditional reasoning improves accuracy on the frozen 180-task confirmation split

2026-09-12. Qwen3-4B BF16, MBPP+ v0.2.0. This report closes the previously frozen confirmation experiment and reports a separate negative development routing ablation. It supersedes v0.7's pending status; earlier reports remain historical records.

## Main result

| Method | Correct / 180 | Accuracy | Rescue / regression vs selected baseline |
|---|---:|---:|---:|
| First candidate | 103 | 57.22% | 0 / 4 |
| Public-first execution-consensus baseline | 107 | 59.44% | 0 / 0 |
| Conditional nonthinking resampling | 107 | 59.44% | 0 / 0 |
| Conditional reasoning resampling | **118** | **65.56%** | **11 / 0** |

The prespecified primary comparison is reasoning versus nonthinking resampling, over all 180 tasks. The absolute improvement is **6.11 percentage points**; the paired task-bootstrap 95% interval is **[2.78, 10.00] points**. The exact two-sided McNemar p-value is **0.0009765625**, below the fixed 0.05 threshold. The descriptive improvement over the first candidate is 8.33 points. Coverage is 100% because unsuccessful extensions fall back to the baseline; this is not selective abstention.

The primary contrast changes reasoning mode, sampling preset and token cap jointly. Both arms receive the same number of extra calls, but realized compute differs substantially. This supports the tested conditional pipeline on this split, not a claim that reasoning alone causes the gain or that it wins at equal compute.

## What was fixed before scoring

The task split was fixed as 60 development, 60 calibration, 180 confirmation and 78 reserve tasks. The final protocol was frozen at commit `7ef1103`; its SHA-256 is `4e9c553d85c58b9676f553ae1a999407f1a1dd73efafc9a837a989c46fb84b31`. No threshold was fitted, so calibration was not a prerequisite. Calibration and reserve remain unused.

Each confirmation task received four original nonthinking candidates and one independently generated test response: 720 candidates and 180 test responses. Public-first execution consensus selected the baseline. Only failure on at least one public example triggered another generation; 41 tasks triggered. Each triggered task received one nonthinking resample (768-token cap) and one reasoning resample (2048-token cap), with the fixed paired seed schedule. Replacement required strictly more passed public assertions. Incomplete reasoning retained an empty failed candidate and baseline fallback; no answer-quality retry or budget extension occurred.

The visible-only Docker workflow had no hidden benchmark mounted. It persisted the matrix and selected indices before the separate scorer loaded hidden references. All final decisions and their hashes were committed before hidden scoring. The scorer validates those immutable decisions and never selects. The final analysis retained every task and both generation arms, using the frozen primary test.

## Matrices

Baseline-to-reasoning transition matrix, including every confirmation task:

| Baseline outcome | Final wrong | Final correct | Total |
|---|---:|---:|---:|
| Wrong | 62 | **11** | 73 |
| Correct | **0** | 107 | 107 |
| Total | 62 | 118 | 180 |

Post-confirmation error-detection matrix for the public-failure trigger. Positive means an incorrect selected baseline:

| Trigger decision | Baseline wrong | Baseline correct |
|---|---:|---:|
| Triggered | 41 (TP) | 0 (FP) |
| Not triggered | 32 (FN) | 107 (TN) |

Error recall is 41/73 = 56.16%; observed precision is 100%. The trigger misses 32 incorrect answers. This is a descriptive failure analysis after confirmation, not a new fitted detection rule. Zero observed regressions or false positives does not establish a zero population rate.

## Measured cost and incomplete reasoning

| Generation group | Calls | Output tokens | Recorded wall-seconds |
|---|---:|---:|---:|
| Common original candidates | 720 | 29,701 | 1,438.59 |
| Common generated tests | 180 | 30,469 | 32,793.69 |
| Nonthinking extension | 41 | 2,316 | 119.25 |
| Reasoning extension | 41 | 72,297 | 4,047.39 |

Reasoning uses approximately 31.2 times as many extra output tokens as the nonthinking arm. Of its 41 attempts, 27 hit the token cap and 26 did not complete the reasoning delimiter. All attempts remain in the denominator. The model was local and no paid GPU/API was used for these calls.

The test-generation wall-time includes a large desktop stall and must not be reported as steady GPU throughput, service latency or billing time. Peak allocated model memory across common generation was about 8.2 GiB; this excludes other allocations and is not total device memory.

## Separate development routing ablation: no additional gain

This adaptive experiment used the additional 40 development tasks, not confirmation. A visible execution-disagreement condition expanded the trigger from three to six tasks. Six old independent resamples were reused; six new calls were generated. All 40 tasks and seven methods were retained.

| Method | Correct / 40 | Rescue / regression |
|---|---:|---:|
| Selected baseline | 32 | 0 / 0 |
| Public-only, nonthinking, strict replacement | 32 | 0 / 0 |
| Public-only, reasoning, strict replacement | 33 | 1 / 0 |
| Expanded trigger, nonthinking, strict replacement | 32 | 0 / 0 |
| Expanded trigger, reasoning, strict replacement | 33 | 1 / 0 |
| Expanded trigger, nonthinking, full-public-pass tie acceptance | 32 | 0 / 0 |
| Expanded trigger, reasoning, full-public-pass tie acceptance | 33 | 1 / 0 |

The sole rescue remains Mbpp/801. Expanded screening raised development error recall from 37.5% to 62.5% but produced no additional correct answer. This separates a better detection metric from end-to-end accuracy. The expanded policy is not adopted as an improvement. Reused-plus-new output costs were 329 nonthinking and 9,042 reasoning tokens; only 4,673 tokens were newly generated. The pre-generation score-plan schema correction and original plan are preserved in the run directory; it changed no scientific treatment.

## Reproduce and audit

- Confirmation base visible evidence: [34670369963](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34670369963), source `0a87cf1`.
- Confirmation extension visible evidence: [34673629219](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34673629219), source `c21dc73`.
- Final immutable scoring: [34673699627](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34673699627), source `f44fdd6`.
- Development routing: [34670358137](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34670358137), source `57a8478`.

Run `python scripts/analyze_confirmation.py`, `python scripts/build_confirmation_diagnostics.py` and `python scripts/analyze_routing_v2.py`. These analyze persisted evidence; they do not execute generated programs on the host. Candidate execution occurs only in restricted Linux containers.

## Interpretation and next work

This is evidence of a real accuracy improvement on a frozen held-out task split, with an explicit matched-call control, costs and negative ablations. One model, one public benchmark and one seed schedule limit generalization. Held out from project development does not establish absence from model training. Nearest-work reproduction, broader baselines and external validation remain necessary before a conference submission or novelty claim. No deployment or external user impact is claimed.

Further optimization should investigate incomplete reasoning and missed errors on development data. Do not tune on this completed confirmation split and then reuse its p-value as fresh evidence. Any new method needs a frozen protocol and new evaluation evidence; the 78-task reserve remains untouched.

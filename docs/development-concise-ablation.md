# Concise-instruction development ablation

A fixed, task-independent request to reason briefly and finish the implementation was appended to the original user prompt. This is an adaptive development experiment, not independent confirmation. All 40 development tasks remain in the denominator; all three public-failure triggers receive the treatment. Three original 2048-token calls are reused and exactly three new calls use the same seeds, sampling settings, model and maximum output budget. Public replacement remains strictly-more-passes. No hidden task-specific hints were supplied.

| Method | Correct / 40 | New rescues / losses versus original reasoning | Output tokens | Incomplete |
|---|---:|---:|---:|---:|
| Selected baseline | 32 | — | shared original pool | — |
| Original reasoning | 33 | control | 4580 (cached) | 1/3 |
| Concise instruction | 32 | 0 / 1 | 3991 (new) | 1/3 |

The concise arm loses the original rescue on Mbpp/801, a -2.5 percentage-point development difference. It saves 589 output tokens (12.86%) but does not improve completion count or accuracy and is not adopted. Relative to the selected baseline its transition matrix is correct→correct32, correct→wrong0, wrong→correct0, wrong→wrong8. This three-trigger sample does not establish a general prompt effect. Different desktop timing prevents a speedup claim.

The existing 180-task confirmation remains118/180 versus107/180. Calibration and reserve remain unused. The next scientifically useful intervention should address concrete failure modes on development data; neither doubling the cap nor this generic brevity instruction provides a supported improvement.

Reproduce statistics with `python scripts/analyze_concise_development.py`. Generated programs ran only in restricted Linux evaluation. The run stores source/prompt/code hashes, frozen decisions, costs and all failures.

Visible workflow: 34735732838; immutable score workflow: 34735769094. Results commit: 8f989a1.

# More Distinct Programs Did Not Improve Selection

Technical report v0.4 · 2026-09-07 · [Previous consensus experiment](technical-report-v0.3.md)

We completed the frozen temperature-only intervention on the same 20 development tasks: Qwen3-4B temperature 0.7→1.0, with four candidates per task. The 80 new generations use the same seeds and prompts, and all tests and selector rules are reused. Total distinct source programs rise from 30 to 32, but candidate-oracle accuracy stays at 12/20. Execution consensus falls from 11/20 to 10/20, and the previously chosen public-first composition falls from 12/20 to 11/20. These are development results, not independent confirmation.

## 1. Controls and provenance

The generation intervention was recorded on September 6 before this batch ran. It was initially deferred for insufficient GPU headroom. On September 7, 10,915 MiB free memory exceeded its 9,216 MiB launch threshold, so the existing local BF16 model could be used without changing precision, offloading or renting compute.

The [setup audit](../runs/mbpp-temperature-20260906/pre-score-check.json) verifies unchanged model configuration, split, task IDs, precision, thinking mode, top-p, token cap, package versions, generation backend, prompt hashes, input token counts and per-candidate seeds. Temperature is the sole changed field in the original generation metadata. Effective settings include top-p 0.8, inherited top-k 20, maximum 768 generated tokens and non-thinking mode. The complete checkpoint/tokenizer fingerprint was checked before model loading.

The same 160 normalized assertions are reused byte-for-byte. Reference-derived annotations are not supplied to selection. The public-first consensus function's AST is unchanged from commit `11a24ef`. The new mapping and fixed-policy evaluation procedure were recorded before new hidden scores were inspected.

Candidate/test decisions and input-only consensus decisions are saved by restricted Linux jobs. The composition then reads only public-test outcomes and consensus scores and persists its choices before the analysis scripts read hidden labels. The input-only consensus container has no hidden benchmark mounted. Scoring uses the same EvalPlus 0.3.1 primitives and dataset revision as before.

Artifacts: [generation manifest](../runs/mbpp-temperature-20260906/manifest.json), [evaluation mapping](../configs/temperature-evaluation-mapping.json), [consensus workflow 34151733732](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34151733732), [scorer workflow 34151735911](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34151735911). Both jobs use commit `b7d9b161c520d29742f8b9000813edb9a49189ba`.

## 2. Paired task results

| Method / diagnostic | Temperature 0.7 | Temperature 1.0 |
|---|---:|---:|
| First candidate, correct / 20 | 10 | 10 |
| Public-example selection | 11 | 11 |
| Generated-test selection | 10 | 10 |
| Filtered generated tests | 10 | 10 |
| Public-first, then filtered tests | 11 | 11 |
| Execution consensus | 11 | 10 |
| Unique-code consensus | 10 | 10 |
| Public-first, then execution consensus | 12 | 11 |
| Fixed abstention rule, correct returned / 20 | 0 | 0 |
| Candidate oracle, diagnostic only | 12 | 12 |
| Distinct source programs across all tasks | 30 | 32 |
| Tasks with all four candidates text-identical | 13 | 14 |

Every selection method except the abstention rule has 100% coverage. The abstention rule still returns nothing. The unchanged oracle concerns the same 12 tasks; it is not an accidental balance of newly gained and newly lost solvable tasks.

The decline in execution consensus and its public-first composition is entirely on Mbpp/607. Their paired task-bootstrap difference between temperatures is −5 percentage points, interval [−15, 0] points. This small, inspected development sample does not establish a general harmful effect of temperature. Likewise, identical task correctness for other methods does not demonstrate equivalence; their empirical bootstrap intervals are degenerate because every paired difference is zero.

The distinct-code count and all-identical-task count move in different directions: more variants are concentrated in fewer tasks. Neither measure establishes useful behavioral diversity or a larger correct-candidate set. The proposed intervention did not increase candidate-oracle availability in this run.

## 3. Why the previous rescue disappeared

At temperature 0.7, Mbpp/607 has two passing candidates that share a source implementation. Their repeated votes create a small agreement margin. At temperature 1.0, the four candidates are distinct and disagree on what to return when the regex has no match:

| Sample | No-match return | Hidden benchmark result |
|---|---|---|
| 0 | `(None, None, None)` | fail |
| 1 | `None` | pass |
| 2 | `("", -1, -1)` | fail |
| 3 | `(None, -1, -1)` | fail |

All four pass the public example. Each receives 21 agreements out of 24 pair comparisons over the extracted inputs. Both consensus variants therefore tie and select sample 0. Public-first composition cannot resolve the tie either.

The visible task does not define no-match behavior. The reference expects `None`, but a deployed selector cannot consult that reference. More distinct responses have exposed the ambiguity without identifying the benchmark-preferred response. This case connects the earlier specification audit to the instability of a selection gain; it does not prove that all consensus failures arise from ambiguity.

## 4. Cost and reproducibility

| Measurement | Temperature 0.7 | Temperature 1.0 |
|---|---:|---:|
| Candidate output tokens | 3,540 | 3,536 |
| Candidate generation seconds | 175.93 | 178.16 |
| New test-generation tokens in this intervention | — | 0 |

New candidate generation peaks at 8,297,903,104 allocated bytes, or 7.73 GiB. This is the new generation peak; a summary that includes reused test records also contains the earlier test-generation peak and must not be presented as new GPU consumption. Model loading and other setup are excluded from the generation timings. Different wall-clock sessions and ambient load limit timing comparisons.

The new consensus job executes 644 single-candidate and 891 pair probes in 7.75 seconds; 75 pairs are not comparable after a failed single probe. The scorer/test-matrix job takes 11.80 seconds. Those job timings exclude image building and scheduling. Public-first composition adds no new execution calls. All 80 new candidates parse as Python.

Artifacts match their recorded hashes. Fourteen contract tests pass, and rerunning the generation entry point recognizes all 80 completed keys and exits without loading the model. Raw records, decisions, per-task comparisons, reused-test provenance and the unsuccessful hypothesis are preserved.

## 5. Decision after this experiment

Do not claim that higher temperature improves useful diversity or that the initial 12/20 composition result is stable. Keep both conditions in the report. The next useful step is to hold the selection policy fixed and evaluate the remaining 40 development tasks with a recorded manifest, while preserving calibration and confirmation data. Temperature 0.7 remains the original baseline configuration, not a winner established by this small comparison. Full nearest-work reproduction and calibrated abstention remain unfinished.

Reproduce the paired summary with `python scripts/compare_temperature.py`. Evidence: [paired comparison](../runs/mbpp-temperature-20260906/comparison.json), [new consensus](../runs/mbpp-temperature-consensus-20260907/summary.json), [fixed composition](../runs/mbpp-temperature-public-consensus-20260907/summary.json). The 180 confirmation tasks remain unused.

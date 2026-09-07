# When the Evaluator Becomes the Failure

Technical report v0.2 · 2026-09-05 · Follow-up to [the first pilot](technical-report-v0.1.md)

[Version 0.3](technical-report-v0.3.md) adds execution-consensus evidence and an explicitly adaptive public-first composition; this version remains the record of evaluator and semantic diagnostics.

This update adds controlled evaluator interventions, an audit of generated-test semantics, and a historical entropy-policy reanalysis. It adds **zero model calls**, uses already exposed development/historical data, and leaves the 180 confirmation tasks untouched.

## 1. Controlled evaluator interventions

Seven unchanged historical candidates had different labels between the original Windows evaluator and Linux EvalPlus primitives. We copied the original evaluator source without edits and ran it under Linux using `spawn`, then changed one mechanism at a time: drain the multiprocessing queue before joining the worker; omit output `repr` logging; or, for large-integer cases, disable the integer string-conversion limit while retaining `repr`.

The experiment contains seven historical tasks plus two hand-written mechanism fixtures, 29 condition rows, and 30.08 seconds of diagnostic runtime excluding image/setup overhead. The historical local dataset checksum exactly matches the downloaded HumanEval+ Mini v0.1.10 data. All code runs inside the existing restricted Docker boundary. This recreates evaluator mechanisms on Linux, not the original Windows environment.

| Case | Original legacy evaluator on Linux | Drain queue first | Also omit output `repr` | Conclusion |
|---|---|---|---|---|
| HumanEval/15 | timeout at 10 s | pass, 1.08 s | pass | Queue join order reproduced the false timeout. |
| HumanEval/100 | timeout at 10 s | pass, 0.44 s | pass | Same queue mechanism reproduced. |
| HumanEval/139 | fail, `ValueError` | fail, `ValueError` | pass, all 4 inputs | Logging correct large-integer outputs causes failure. |
| HumanEval/96 | pass | pass | pass | Historical Windows timeout not reproduced. |
| HumanEval/123 | pass | pass | pass | Historical Windows timeout not reproduced. |
| HumanEval/160 | `unsafe_call:eval` | same | same | Old gate policy reproduced; not a program-correctness finding. |
| HumanEval/162 | `unsafe_import` | same | same | Old import policy reproduced. |

For HumanEval/15, serialized queue payload is **34,444,887 bytes** with output representations, versus **77 bytes** when those representations are omitted. HumanEval/100 changes from 9,000,149 to 68 bytes. The original parent waits for worker termination before reading the queue; the worker cannot finish flushing a large payload while the parent does not read. Reordering the parent operations alone makes both unchanged candidates pass.

HumanEval/139 still fails after fixing queue order. Omitting output stringification makes all inputs pass. Independently disabling Python's default 4,300-digit conversion limit also makes all inputs pass while retaining representations. A hand-written `10 ** 5000` fixture shows the same pattern. The diagnosis is therefore specific to logging, not merely a faster evaluator or longer timeout. Disabling the global conversion limit is a diagnostic intervention, not the recommended production repair; avoid unnecessary stringification of unbounded outputs.

The two smaller historical output payloads, 11,955 and 15,026 bytes, do not cause Linux timeouts. Platform pipe behavior is a possible explanation, but we have not measured the original Windows pipe behavior. These two cases remain unresolved. We do not claim to have causally explained all seven original labels.

Evidence: [workflow 33992906744](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/33992906744), source commit `b2fc1d370295964d3f9303ef0b3f11cb780e661e`, [frozen protocol](../configs/legacy-diagnostics.json), [condition-level records](../runs/legacy-diagnostics-20260905/linux/diagnostics.jsonl), [summary](../runs/legacy-diagnostics-20260905/summary.json).

## 2. Reference rejection is not a single failure category

The normalized development pilot contains 34 reference-rejecting assertions across 12 tasks. We reviewed the public prompt, assertion, and diagnostic reference/contract source for each. The following are **post-hoc AI-assisted annotations by one annotator**, with no independent human agreement check. They are judgments, not definitive ground-truth labels.

| Primary annotation | Assertions | Interpretation |
|---|---:|---|
| Wrong expected value under public evidence | 22 | Arithmetic, aggregation, substring/index or threshold mistakes supported by visible task evidence. |
| Specification ambiguity or conflict | 11 | Public prose leaves a behavior unclear, or prose and example support different interpretations. |
| Outside hidden benchmark contract | 1 | Negative input excluded by an unseen benchmark constraint; not necessarily invalid under visible prose. |

Examples demonstrate why these distinctions matter:

- **Wrong expectation:** `remove_Occ('test', 't') == 'est'` removes only one of the two required occurrences; the visible instruction supports `'es'`.
- **Description/example conflict:** Mbpp/615 says to average each tuple, but its public example and reference average columns. Five generated checks follow a reasonable row-wise reading. Three other checks match neither interpretation and copy values from a different example input.
- **Unspecified parameter:** Mbpp/564 does not explain `n`. Some generated checks count unequal pairs in the full list, while the reference considers only the first `n` entries. The public example uses `n == len(list)` and cannot disambiguate those interpretations.
- **Hidden-domain mismatch:** the negative-number test for Mbpp/479 violates the hidden `n >= 0` contract, which is absent from the generator-visible specification.

These annotations are stored under a diagnostic-only audit directory. They must not become features, training labels or filters for the deployable selector on these tasks. The selector cannot use hidden contracts merely because the analyst can inspect them after scoring. The 22/11/1 classification should be independently reviewed before publication, and possible overlap between categories should be retained in annotation rationales.

Evidence: [34 annotations](../runs/mbpp-parser-ablation-20260905/audit/annotations.jsonl), [audit summary](../runs/mbpp-parser-ablation-20260905/audit/summary.json).

## 3. Historical policy numbers require a correction

We kept all historical entropy scores and the original 71 accepted tasks fixed, changed only correctness labels to the Linux results, and recomputed the metrics. No threshold was retuned.

| Metric | Original Windows labels | Linux labels |
|---|---:|---:|
| Correct / 100 historical test tasks | 75 | 82 |
| Correct / 71 historically accepted tasks | 56 | 62 |
| Selective accuracy at 71% coverage | 78.87% | 87.32% |
| Selective minus baseline accuracy | +3.87 pp | +5.32 pp |
| Error-detection AUROC | 0.5984 | 0.6240 |
| Paired bootstrap 95% interval, original NumPy algorithm | [−1.77, +9.95] pp | [−0.08, +11.24] pp |

The original NumPy bootstrap procedure and seed reproduce the old interval. The new interval still narrowly includes zero. A separately recorded Python-RNG bootstrap realization yields [+0.08, +11.30] pp instead. This sensitivity around zero means the result should not be framed as a robust significance finding. The historical data are already exposed; these estimates do not replace independent confirmation.

The old blog's holdout numbers should be corrected, with the old results retained as an explicitly labeled Windows-evaluator result. The difference is not model improvement. No public blog was edited in this update; a [correction draft](blog-correction-draft.md) records the exact wording and limitations.

Evidence: [policy reanalysis](../runs/historical-holdout/policy-reanalysis.json), regenerated with `scripts/reanalyze_historical_policy.py --numpy-bootstrap` under NumPy 2.5.1.

## 4. Implications for the next model experiment

The pipeline now has concrete examples of infrastructure-induced false failures, genuinely questionable generated expectations, and underspecified tasks. Combining these into one “verifier error rate” would obscure different remedies.

The next bounded experiment will target candidate diversity on development tasks while keeping selectors fixed. It must record effective generation defaults and measured token/time budgets; four candidates alone do not establish equal compute. Specification-aware test signals should be designed from visible information and tested separately. Confirmation data remain reserved until generation, selection and calibration procedures are frozen.

This update strengthens the engineering and research evidence. It does not establish selector superiority, calibrated risk control or conference-level novelty.

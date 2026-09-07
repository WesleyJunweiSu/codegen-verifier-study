# Inputs Can Help Even When Expected Answers Are Wrong

Technical report v0.3 · 2026-09-06 America/New_York · [Earlier diagnostic report](technical-report-v0.2.md)

[Version 0.4](technical-report-v0.4.md) completes the temperature intervention: the candidate oracle is unchanged and fixed public-first consensus falls from 12/20 to 11/20. This version remains the record of the initial adaptive composition.

This update adds input-only execution consensus to the frozen 20-task development pool. It makes zero model calls. Ordinary consensus returns 11 correct programs, while a unique-code voting variant returns 10. An explicitly adaptive public-first composition returns 12, matching the candidate oracle on this inspected pool. No confirmation data are used and no general improvement is established.

## 1. Question and frozen comparison

Earlier generated-test selection returned 10/20 correct programs, the same as taking the first candidate. Many generated expectations were questionable. Does retaining test inputs while discarding expected answers provide useful selection evidence?

We froze [the consensus protocol](../configs/consensus-protocol.json) before execution and reused the exact 80 candidate programs and normalized test responses from the prior pilot. Literal target calls are extracted from public examples and all normalized assertions; expected outputs are discarded. AST-identical calls are deduplicated, yielding 161 task/input pairs. No nonliteral arguments were accepted, and no reference-aware filtering was applied.

Each candidate is first checked for successful execution on each input. Pairs that pass those checks are then compared with Python `bool(left == right)` using independently reconstructed literal arguments and fixed random seeds. Exceptions do not count as agreement. Output values are not serialized with `repr`, avoiding the integer-logging failure identified in v0.2. Native Python equality is not the same as every EvalPlus task-specific or floating-point equivalence rule.

Two methods were frozen: average agreement with all other candidate samples, and agreement with one representative of each distinct source-code group while excluding the candidate's own group. Ties and empty evidence select the smallest sample index. Neither method abstains or provides a correctness guarantee.

The restricted Linux container mounts only candidates, generated tests and an output directory; hidden benchmark data and prior hidden scores are not mounted. Decisions are persisted before a separate analysis joins the previously computed hidden labels. Four executor fixtures check equal outputs, unequal outputs, shared exceptions and equal 5,001-digit integers. Four added local contract tests check expected-value independence, nonliteral input rejection, shared-failure handling and duplicate-code voting.

Evidence: [workflow 34072360167](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34072360167), frozen source commit `843aba5677fa5666e31258c4889277e8902d2a7c`, [raw artifacts](../runs/mbpp-consensus-20260906/linux/), [summary](../runs/mbpp-consensus-20260906/summary.json).

## 2. Results on the same development pool

| Method | Correct / 20 | Rescues over first | Regressions |
|---|---:|---:|---:|
| First candidate | 10 | — | — |
| Generated-test pass count | 10 | 0 | 0 |
| Public examples | 11 | 1 | 0 |
| Execution consensus | 11 | 1 | 0 |
| Unique-code consensus | 10 | 0 | 0 |
| Public-first, then execution consensus — adaptive | 12 | 2 | 0 |
| Candidate oracle — non-deployable | 12 | — | — |

All deployed methods here return a candidate on every task. Execution consensus rescues **Mbpp/607**, whereas public-example selection rescues **Mbpp/564**. These are different cases. The first five rows are either previously recorded baselines or the newly frozen consensus comparison; the composition was proposed after inspecting these outcomes.

Execution-consensus accuracy is 55%, Wilson 95% interval 34.2–74.2%. Its paired task-bootstrap difference from first-candidate accuracy is +5 percentage points, interval 0–15 points. Unique-code consensus matches the first candidate's correctness on every task; its degenerate empirical difference interval is not evidence of equivalence.

## 3. What happened on Mbpp/607?

All four candidates pass the public example. On eight extracted inputs, candidates 1 and 2 each receive 22 agreements out of 24 possible sample comparisons; candidates 0 and 3 receive 21/24. The ordinary consensus rule selects sample 1, which passes hidden evaluation. Generated-test pass counts previously selected failing sample 0.

The unique-code rule removes repeated-code votes. All candidates then tie at 14/16 and the smallest-index tie-break again selects sample 0. Thus deduplication is not automatically beneficial: sample multiplicity can carry useful evidence in a particular case. This single observation does not establish that duplicates should always be retained, or that repeated samples are independent statistical evidence.

The principle under investigation is narrow: a generated input can expose a useful disagreement even when its associated expected answer is unreliable. Consensus still cannot prove which side is correct, and a majority can share the same mistake.

## 4. Adaptive public-first composition

After inspecting the complementary rescues, we recorded a lexicographic policy: maximize public-test passes, then ordinary execution-consensus score, then choose the smallest sample index. Its implementation reads only public-test outcomes and persisted consensus scores; it saves decisions before its scoring script reads hidden labels. A dedicated contract test verifies that consensus cannot override a higher public-test score.

The composition selects the passing candidate on both Mbpp/564 and Mbpp/607, yielding 12/20. Its Wilson interval is 38.7–78.1%, and its naive paired task-bootstrap difference from first-candidate selection is +10 percentage points, interval 0–25 points. **That interval is not adjusted for selecting the policy after observing development outcomes.** Reaching the candidate oracle on these 20 tasks does not establish general effectiveness.

This is a concrete candidate method for the next frozen experiment. It must be tested on further tasks and generation conditions before a headline resume or paper claim. The new CLI command displays the saved evidence and selected code:

```bash
python scripts/selector_cli.py --run mbpp-public-consensus-20260906 --task Mbpp/607 --method public_then_consensus
```

Evidence: [adaptive decisions](../runs/mbpp-public-consensus-20260906/decisions.jsonl), [composition manifest](../runs/mbpp-public-consensus-20260906/manifest.json), [result](../runs/mbpp-public-consensus-20260906/summary.json).

## 5. Cost and pending generation intervention

Consensus executed 644 single-candidate probes and 888 pair probes; 78 additional pairs were skipped because at least one candidate failed its single probe. The executor phase took 7.82 seconds, including its four fixtures but excluding image construction and scheduler overhead. The adaptive composition reused those outcomes and added zero execution or model calls. These are incremental costs; the original candidate/test-generation cost remains part of any end-to-end comparison.

The planned temperature intervention changes only temperature 0.7→1.0, retaining top-p 0.8, task IDs, candidate count, seeds, precision and token cap. Its [configuration](../configs/temperature-intervention.json) and resumable runner are prepared. Current GPU free memory was 7,147 MiB, below the recorded 9,216 MiB launch threshold; the runner recorded the deferral and did not load the model. No applications were terminated and no paid compute was started. This is a resource deferral, not a completed model experiment.

The next step is to run that frozen condition when memory is available, compare candidate diversity and oracle availability, and keep the existing selectors fixed. Equal candidate count does not imply equal realized token/time cost. Confirmation data remain reserved, and a full nearest-work reproduction plus calibrated abstention remain unfinished.

# Confirmation execution boundary

Prepared 2026-09-10 while the frozen development transfer runs. This is an implementation design, not a claim that confirmation has started or that its final manifest is frozen.

The development workflow scores the baseline before extra-generation experiments. Do not reuse that order for confirmation: the final routing and replacement decisions must be persisted before **any confirmation labels are inspected**. Avoid creating downloadable label artifacts during an intermediate visible-evidence stage.

The required sequence is:

1. Freeze a dedicated manifest containing the existing 180 confirmation task IDs, model fingerprint, original candidate and test prompts, sampling seeds and caps, parser and selection implementations, public-only trigger, extension conditions, one primary comparison and the complete analysis specification. Verify disjointness against development, calibration and reserve. Task IDs may be read from the split manifest; no hidden task fields are needed.
2. Generate four original candidates and one test response per task with resumable writes. Record all malformed, capped and empty outputs. The task specification and public examples are the only benchmark fields allowed to enter generation.
3. Use a **visible-only Linux stage** that mounts only candidate records, generated test records and the frozen manifest. Do not download or mount the hidden dataset in this stage. Compute public and generated-test outcomes and input-only consensus. Persist all original selectors and the fixed public-first consensus decision.
4. Form extension triggers from the persisted public outcomes. Generate the manifest's extension conditions without consulting hidden labels. Make no hidden-failure-selected retries. Keep untriggered tasks and unsuccessful attempts in the denominator.
5. Run a second visible-only stage for extension public outcomes. Persist the final baseline and extension decisions, including fallback, and compute their hashes. Assert one decision per task per reported method, complete input coverage and no unexpected candidate IDs. The hashed decisions become immutable inputs to scoring.
6. Only now download the pinned hidden dataset into a distinct restricted scorer. Evaluate the candidate records against the original base and additional tests. The scorer must not change selection decisions. Verify input and decision hashes, fixture results, exact task coverage and code hashes before joining labels.
7. Run the frozen task-level analysis once. Report correct counts / 180, coverage, rescues and regressions, paired uncertainty, primary test and every method's realized cost. Any later methodological changes use another explicitly identified dataset and cannot be advertised as confirmation on these same tasks.

## Statistical and cost requirements

Choose the primary comparison before the manifest is signed off. The current development comparison is reasoning resampling versus non-thinking resampling conditional on the same public-failure trigger. The intervention changes reasoning, sampling settings and output cap; it cannot identify the separate causal effect of any one of those changes.

A suitable frozen analysis reports a paired task-bootstrap interval for the accuracy difference, an exact two-sided McNemar test over discordant task outcomes, and Wilson intervals for each method's accuracy. Zero discordant tasks yield a primary p-value of 1; a zero-width bootstrap interval on such data is not proof of equivalence. Treat all other method comparisons as secondary, without promoting the best-looking one after scoring. No optional stopping or partial-result significance checks.

Record common baseline cost once and each extension's incremental model calls, input/output tokens, capped responses, wall time and memory separately. Do not claim fixed-compute superiority from matching call count alone. The prior unexplained wall-time stall motivates external runtime telemetry in a later timing study, not removal of inconvenient timings from this confirmation run.

## Implementation status

The existing restricted evaluator, input-only consensus, deterministic composition, conditional replacement and generation backends are reusable. A confirmation coordinator and visible-only workflow still need to be implemented and frozen before generation/scoring. The old `linux-eval.yml` downloads hidden data and is therefore **not an intermediate confirmation visible stage**. This boundary must remain explicit in the next continuation checkpoint.

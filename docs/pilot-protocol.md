# Pilot protocol — original design with execution addendum

Date: 2026-09-05. The design below predates implementation. This addendum records execution status and deviations; original forward-looking scope remains for comparison.

## Execution addendum

The 20-task MBPP+ development pilot and parser ablation are complete. IDs are frozen in `configs/split-manifest.json`: 60 development, 60 calibration, 180 confirmation, 78 reserve. The prior repository was audited: MBPP+ was not previously evaluated. Local BF16 inference measured 8.08 GiB peak across candidate and test generation.

Completed comparisons: first candidate, exact uniform-random expectation, public examples, raw/filtered generated tests, fixed uncalibrated abstention. The ablation adds public-first selection. Execution-consensus, full nearest-work reproduction, calibrated abstention and matched end-to-end budgets remain unfinished. The original first-week gate was accelerated to the first pilot. See the technical report and log; these are not confirmation results.

The evening follow-up adds diagnostic-only semantic annotations, historical policy reanalysis with unchanged accepted flags, and controlled legacy-evaluator interventions frozen in `configs/legacy-diagnostics.json`. It adds zero model calls. Reference-visible annotations must not become deployable selector inputs. Historical /96 and /123 timeout causes remain unresolved on Linux; all other intervention findings are qualified by platform in report v0.2.

## Research question

When generated tests are unreliable, can a small-model selector reduce incorrect acceptance under a fixed compute budget while preserving useful answer coverage?

This is a replication and extension of established test-guided code-selection work. Novelty has not been established.

## Prior evidence and reuse

The previous blog reports Qwen3-4B BF16, non-thinking mode, HumanEval+ Mini, 30 development / 34 calibration / 100 test tasks. It describes collapsed behavioral diversity, unstable uncertainty signals, and a gap between oracle and deployed selection.

Obtain original manifests, raw candidates and evaluator labels before treating any number as reproduced. Audit labels with the official EvalPlus evaluator in a suitable isolated Linux environment. Historical results were produced with a Windows evaluator according to the blog.

All 164 historical tasks are now exposed for this follow-up study. Reuse only for historical replication or development, never as a fresh confirmation holdout.

## Scope and data

- Python function tasks; one 4B model initially; four candidates per task for the pilot.
- Smoke test: 20 tasks, chosen from a newly audited MBPP+ subset, not used for headline performance claims.
- Main study target: 100–200 independent tasks if feasible, with disjoint task-level development, calibration and test manifests. Freeze actual IDs, revisions, duplicate checks and split counts before confirmation.
- Verify previous usage of MBPP+ before adoption; select an alternative unused split if necessary.
- Public benchmarks may be in pretraining data. Report this limitation, and reserve independently collected tasks for external-validity checks when possible.
- Group all candidates, generated tests and seed repetitions under their source task.

## Information boundary

The selector and test generator may access the task specification, public examples and candidate code. Hidden tests, reference implementations and hidden-test labels are available only to the scorer after selection decisions have been saved.

Validation against a reference implementation can characterize generated-test error after the fact; it must not become a deployable filtering step. A generated test rejecting a reference solution is not alone a universal proof the test is wrong: audit specification ambiguity and reference limitations.

Consensus between candidates establishes agreement, not correctness. A distinguishing input without a trustworthy expected output can expose disagreement but cannot by itself identify which candidate is right.

## Comparisons

Stage A: share a frozen candidate pool across selectors to isolate selection quality.

1. First candidate.
2. Random candidate, with repeated randomization for variance.
3. Execution-consensus selector on generated inputs.
4. Test-guided selector inspired by S*, with all deviations documented.
5. Test-guided selector with deployable test-quality filtering.
6. The same filtered selector with abstention, calibrated on the calibration split.

Include matched-coverage random abstention and public-test-only baselines. Choose tie-breaking and treatment of parsing errors/timeouts before seeing confirmation scores. Primary success comparisons should not allow missing or failed generations to disappear from the denominator.

Quality signals may include parseability, input-domain constraints derivable from the specification, contradiction with public examples, duplicate/degenerate tests, and consistency of independently generated checks. Do not label these signals as guarantees that expected outputs are correct.

Stage B: compare full pipelines including candidate generation, test generation, selection, repair if enabled, and execution. Match measured budgets, not only candidate count. If repair is introduced, report it as a separate method and include its full cost.

## Error taxonomy

Candidate side: no correct candidate; duplicate/shared failures; correct candidate discarded; selector tie failure; runtime/error parsing failure.

Test side: invalid input; wrong expected output; ambiguous specification; insufficient edge coverage; duplicate behavior; timeout caused by test rather than code; public-example contradiction.

Controlled corruptions are a mechanism study. Preserve a separate naturally generated-test set so results are not only about synthetic mistakes. A mutation score can measure fault sensitivity but does not establish validity of a generated test suite.

## Outcomes

- Correct-return rate: correct returned programs / all tasks, counting abstentions as not returned.
- Coverage: tasks with a returned program / all tasks.
- Selective error: incorrect returned programs / returned programs; undefined at zero coverage.
- Candidate oracle accuracy: tasks with at least one correct candidate / all tasks, for diagnosis only.
- Conditional selection success: correct selection among tasks that contain a correct candidate, with denominator reported.
- Incorrect-acceptance and incorrect-rejection counts, with task denominators.
- Cost: candidate/test/selection input and output tokens separately, model wall time, executor time, number of executed tests, total latency, peak VRAM.

Compare selective error at prespecified coverage levels and correct-return rate at matched cost. Plot risk–coverage and accuracy–cost curves. Do not call a system better merely because it abstains more.

Freeze a primary operating point after pilot feasibility checks but before confirmation. Choose no thresholds using confirmation labels. The draft protocol is not a public preregistration.

## Statistical treatment

Use paired task-level comparisons. Bootstrap tasks, preserving every candidate and seed belonging to a sampled task. Report numerator, denominator and uncertainty for every headline rate. Multi-seed evaluation should estimate sampling variability without treating seeds as new tasks.

If the pilot contains too few incorrect programs or too few candidate rescues, its AUROC or selection-success estimate may be unstable; expand or narrow the conclusion. Negative results remain valid outcomes.

## Evaluator and engineering checks

Pin EvalPlus and dataset revisions. Test known-correct, known-wrong, timeout, exception and malformed-response fixtures before running generated candidates. Record evaluator mismatches with the old Windows run before interpreting methodological improvements.

Use isolated Linux execution without network or secrets, constrained resources, a disposable workspace, and no writable user-home mounts. WSL availability alone is not this isolation. Do not execute generated code in the ordinary host environment.

Persist run IDs, task IDs, model revision, precision, chat-template hash, sampling parameters, candidate IDs, test provenance, selection decisions and all costs. Cache only with complete configuration keys. Save output before final scoring. Resume interrupted runs without double-counting.

## Hardware feasibility

Observed GPU: RTX 5070 Ti Laptop, 12,227 MiB VRAM. Start with Qwen3-4B, non-thinking, batch 1, short context, bounded output, one model resident at a time.

First measure peak VRAM and tokens/second. BF16 fit is a hypothesis, not a measured fact. If quantization is necessary, freeze it as a separate condition and do not attribute numerical changes to the selector. Record CUDA/PyTorch compatibility and actual device placement to detect CPU offload.

Estimate runtime from the smoke test: planned generation tokens / observed tokens per second, plus measured input-processing and execution overhead. Rent a larger GPU only if the extrapolation justifies it and a spending cap is agreed.

## Deliverables and decision gate

Deliverables: one-command reproducible run when implemented, manifest, task-level results, plots, CLI/report demo, and a technical report with limitations.

After the first week, identify the main bottleneck: candidate coverage, candidate diversity, test validity, selection, or evaluator reliability. Improve one identified bottleneck. Do not add training or multi-agent complexity to hide an inconclusive selector result.

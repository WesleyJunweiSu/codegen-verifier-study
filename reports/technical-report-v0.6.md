# Additional development tasks reproduce the candidate-coverage bottleneck

2026-09-09 (America/New_York). Forty additional MBPP+ v0.2.0 development tasks, disjoint from the inspected 20-task pilot. This is additional development evidence; the 180-task confirmation split remains unused.

## Frozen comparison

`configs/development-expansion.json` fixed these task IDs and settings before generation: Qwen3-4B BF16, non-thinking, four candidates per task, temperature 0.7, top-p 0.8, inherited top-k 20 and a 768-token cap. Candidate and test prompts and seed rules were inherited unchanged. Each task received one independent eight-assertion test response; the previously documented comparison-to-assert parser normalization was applied without editing expected values.

All 160 candidate keys and 40 test records are complete. The runner and configuration hashes match the frozen manifest. Two candidate responses hit the cap and remain in the dataset. No test-generation responses hit the cap. Candidate generation produced 7,378 output tokens; test generation produced 7,021.

The public-test matrix and original selector decisions were saved before hidden benchmark loading in Linux. Input-only consensus ran in a separate container with no hidden benchmark mounted. The public-first consensus composition was then persisted from public outcomes and consensus scores before local analysis read the candidate labels. Its selection rule was not retuned.

## Results

| Method | Correct / all 40 tasks | Coverage |
|---|---:|---:|
| First candidate | 32 | 100% |
| Public-example selection | 32 | 100% |
| Raw generated-test selection | 32 | 100% |
| Filtered generated-test selection | 32 | 100% |
| Public-first filtered selection | 32 | 100% |
| Execution consensus | 32 | 100% |
| Unique-code consensus | 32 | 100% |
| Public-first execution consensus | 32 | 100% |
| Fixed abstention heuristic | 0 | 0% |
| Candidate oracle, diagnostic | 32 | — |

There were **zero tasks with mixed candidate correctness**. Each task's four candidates were either all correct or all incorrect, and 32 tasks had four text-identical candidates. Consequently, none of these selectors could improve correctness on this realized pool. The observed 80% rate has a Wilson 95% interval of approximately 65.2–89.5%; equal observed results do not prove general equivalence. A degenerate paired bootstrap interval at zero reflects identical task outcomes here, not certainty about future samples.

The generator produced 320 assertions, 318 retained after static filtering. Fifty-one assertions rejected the reference implementation, and all 51 survived the filters. These are reference-rejection diagnostics, not automatically 51 proven-invalid tests: specification ambiguities and domain issues still require semantic review.

## What the public trigger can and cannot reach

The already frozen four-arm transfer protocol examines the final selected candidate's public-example outcomes. It triggers on **Mbpp/137, Mbpp/777 and Mbpp/801**. The public-only plan was saved before analyzing their hidden outcomes. Post-hoc scoring shows all three are among the eight incorrect tasks.

Five incorrect tasks nevertheless pass their public examples. Under this frozen trigger, even perfect new answers on all three triggered tasks would reach only **35/40**. This is a diagnostic upper bound for this cohort and this trigger, not a result already obtained. We will not add hidden-label-selected tasks to the trigger in order to increase the reported gain.

The transfer retains four arms: non-thinking feedback repair, non-thinking resampling, reasoning feedback repair and reasoning resampling. Each makes one extra call per triggered task, for 12 planned calls in total. Public-example improvement is required to replace the baseline; failed or unfinished responses fall back. All 40 tasks and every arm remain in the comparison. Source prompts, seeds, caps and fallback rules are frozen in `configs/development-repair-transfer.json` and the run's `repair-plan.json`.

## Cost and runtime anomaly

The records total **5,235.82 generation wall-seconds**: 4,602.15 for candidates and 633.67 for tests. Peak allocated model memory was 9,164,722,176 bytes (8.54 GiB). These are measured per-call wall times, not a claim of continuous active GPU work or stable serving latency.

One candidate, Mbpp/227 sample 3, took **4,089.06 recorded seconds for 20 output tokens**. The collected metadata do not establish whether this reflects a machine pause, resource contention or another runtime event. The raw duration is retained and no candidate is discarded or regenerated because of it. This anomaly makes the total unsuitable for an unqualified throughput claim. Future timing runs need explicit power/process telemetry or a controlled session before publishing a latency ranking.

The next transfer attempt correctly deferred before model loading because only 8,404 MiB was free, below its frozen 9,216 MiB guard. It spent no model calls, left user applications running, and preserved a resumable plan. This resource deferral does not justify changing precision, caps, prompts or task membership.

## Provenance and continuation

- Frozen input commit: `bece035163d8a873b35dc96b113c75fa313cc40c`.
- [Linux scoring 34422232779](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34422232779).
- [Input-only consensus 34422234386](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34422234386).
- Composition and public-only transfer plan committed at `f132231` before local label analysis.
- Saved runs: `mbpp-development40-20260907`, `mbpp-development40-consensus-20260908`, `mbpp-development40-public-consensus-20260908`, and the pending `mbpp-development40-repair-20260908`.

Resume the existing transfer runner when the local GPU has enough free memory, then commit its completed inputs and use the restricted `linux-eval.yml` workflow. `analyze_transfer.py` verifies full candidate/decision coverage, hashes and unchanged reused labels before reporting four-arm accuracy, costs, failures and the frozen primary comparison.

After that development comparison, freeze a final confirmation manifest and evaluate the 180 held-out tasks once. No calendar waiting period or unrelated calibration project is required for a threshold-free method. These results narrow the research claim toward candidate generation and the limitations of public-example routing; they do not establish novelty or conference readiness.

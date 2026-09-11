# Development transfer yields one rescue; the confirmation protocol is frozen

2026-09-11. The remaining 40 development tasks are fully evaluated. The final 180-task confirmation protocol has been frozen before generation; its first attempt deferred because the GPU had insufficient free memory. No confirmation correctness labels have been read.

## Four-arm result

The same three public-example failures, Mbpp/137, Mbpp/777 and Mbpp/801, triggered all four extra-generation conditions. Each arm made exactly three calls, one per triggered task. The other 37 tasks retained the selected baseline. A new candidate could replace it only by passing strictly more public assertions. Decisions were recorded before the development scorer loaded references; a separate visible-only execution reproduced the matrix and all 200 decisions.

| Pipeline | Correct / 40 | Rescues / regressions | Extra output tokens | Extra generation wall-seconds |
|---|---:|---:|---:|---:|
| Selected baseline | 32 | 0 / 0 | 0 | 0 |
| Non-thinking feedback repair | 32 | 0 / 0 | 123 | 43.00 |
| Non-thinking resampling | 32 | 0 / 0 | 118 | 38.48 |
| Reasoning feedback repair | 33 | 1 / 0 | 4,866 | 3,746.82 |
| Reasoning resampling | 33 | 1 / 0 | 4,580 | 1,121.06 |

Each reasoning arm rescues **Mbpp/801**. Non-thinking feedback also replaces that task's selected answer after a public-example improvement, but its replacement fails hidden tests. No arm recovers Mbpp/137 or Mbpp/777. Each reasoning arm has one unfinished, capped response; both remain failures with baseline fallback. All 52 candidate records and all 40 task denominators are retained.

The prespecified development comparison, reasoning versus non-thinking resampling, improves by **2.5 percentage points**, with a paired task-bootstrap interval of **0 to 7.5 points**. The reasoning feedback and resampling outcomes are identical. The earlier 20-task improvement was much larger; it cannot be presented as an independently confirmed 25-point gain. Neither a zero difference between feedback arms nor a degenerate bootstrap interval proves equivalence beyond this sample.

Input tokens were 783, 338, 771 and 326 for the four arms in table order. Their combined 12 calls generated 9,687 output tokens in 4,949.37 recorded wall-seconds. Desktop resource conditions were uncontrolled, and generation became slow while device memory was nearly occupied. The observations do not establish a causal explanation or stable latency ranking. These are extra costs on top of the original 160 candidates, 40 test responses and selection work; there is no fixed-compute superiority claim.

## Provenance and scoring validation

The transfer configuration was fixed before reading this cohort's scoring outcomes. The exact public trigger plan and source hashes were committed at `f132231`; complete new candidates were committed at `1205fbd`.

- Development score: [34624612668](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34624612668).
- Visible-only extension evidence: [34624610499](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34624610499).
- Immutable-decision scorer validation: [34625001045](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34625001045), source `f067e8b`.

The new scorer validates task/method coverage and dataset/generation/decision hashes before reference loading, then scores without rerunning selection. On the completed development inputs, all 52 candidate evaluation records match the original scorer and all 200 frozen decisions are byte-identical. This validates the execution boundary; it is not new model-performance evidence. Twenty-eight contract tests pass, including frozen decision completeness, first-candidate preservation and exact paired inference.

Artifacts, costs and per-task results are in `runs/mbpp-development40-repair-20260908/`. Reproduction commands:

```bash
python scripts/analyze_transfer.py
python scripts/verify_artifacts.py
python -m unittest discover -s tests -q
```

## Final confirmation

`configs/confirmation-protocol.json` was frozen at commit `7ef1103`, after implementation commit `a10f26e`, without reading confirmation task text or labels during freezing. It binds the existing 180 IDs, model/runtime fingerprints, generation and evaluation source hashes, seeds, caps, fallbacks, methods and analysis.

The primary contrast is conditional reasoning resampling versus conditional non-thinking resampling over all 180 tasks. First-candidate and selected-baseline results are prespecified secondary comparisons. Feedback repair is omitted from this final comparison because it added no new-correctness benefit on the additional development cohort. This choice is based on development, not confirmation outcomes.

The baseline uses four candidates and one independent generated-test response per task, with the original settings and fixed public-first consensus. Both extension arms use the same public-failure trigger and independent solution prompt; each gets one extra call per triggered task. The reasoning bundle changes mode, sampling and the output cap jointly. The primary analysis is exact two-sided McNemar at 0.05, with paired task-bootstrap and per-method Wilson intervals. There is one final analysis; no interim correctness peeking, optional stopping, failed-task exclusion or retuning. A small effect may remain inconclusive with 180 tasks.

The coordinator separates baseline generation, visible-only selection, extension generation, final visible decisions, freezing and hidden scoring. All original candidates remain available so the first-candidate comparator is genuine. No threshold is fitted, so the unrelated 60-task abstention calibration is not a prerequisite.

The first confirmation generation attempt observed **4,582 MiB free**, below the unchanged **9,216 MiB** guard, and returned before loading the model. There are **0/720 baseline candidates and 0/180 test responses** at this checkpoint. The next execution can resume the frozen baseline stage when memory permits; no additional methodological decision or calendar delay is required.

This remains a reproducible research prototype on one model and a public benchmark. It does not establish novelty, production deployment or generalization across models and domains.

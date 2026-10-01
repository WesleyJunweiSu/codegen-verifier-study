# Temperature-only budget control: more source variants, no observed rescue

2026-10-01. Complete adaptive-development batch, with a post-batch provenance audit. Protocol was committedd326fbf before inference. Raw results were automatically committed6fbc310 after public-only selection and frozen isolated scoring. Artifacts: `runs/mbpp-diversity-budget-development-20261001/`.

## Result

| Condition | Selected correct /100 | Triggered tasks with a correct extra candidate /14 | Extra calls | Output tokens | Input tokens |
|---|---:|---:|---:|---:|---:|
| Nonthinking T0.7, saved parent | 72 | 0 | 879 | 28,672 | 95,892 |
| Nonthinking T1.0, new | 72 | 0 | 879 | 28,672 | 95,879 |
| Reasoning, reused unchanged | 77 | 5 | 14 | 18,241 | 1,446 |

Only temperature changed in the new arm. Prompts, BF16 checkpoint, top_p0.8, inherited top_k20, per-call seed rule, output ceiling2048 per triggered task and public selector remained fixed.100 saved baselines and14 reasoning outputs were reused. Each sampling arm uses exactly2048 output tokens per trigger, but input cost and call lengths differ; this is not equal FLOPs. Reasoning's77/100 is the earlier result, **not a new replication**.

The primary new-versus-old contrast has **0 wins and0 losses**, so no selected-answer accuracy gain was observed. There are14 independently treated tasks, not879 independent scientific observations. All tasks belong to the previously exposed development cohort.

## Did the intervention change the samples?

Yes, modestly. Summing distinct source strings within each task gives48→53 task/code pairs. Three of14 tasks gained source variants; parseable outputs increased868→870. Of876 shared task/call-index keys,833 produced identical code. Changed lengths caused different call counts in four tasks despite the same total879 calls.

No new pool contained a hidden-test-correct candidate, even under post-hoc oracle selection. On this batch the current bottleneck therefore precedes selection: no selector could rescue a task from these new pools. This does not show that all sampling presets, seeds or larger models lack useful diversity. Exact text diversity is not semantic or behavioral diversity.

## Uncertainty and cost qualifications

The automatically saved percentile bootstrap for the new-versus-old difference is[0,0] because every observed paired difference is zero. This is a degenerate empirical bootstrap, **not an equivalence confidence bound**, and must not be presented as certainty that the two settings have equal population performance. Keep the raw output for reproducibility; this interpretation supersedes any unqualified reading of that interval.14 treated tasks and one shared call-seed schedule cannot rule out gains elsewhere. No new confirmatory p-value is claimed.

New generation recorded1450.43 model wall-seconds (24.17 minutes),95,879 input tokens and28,672 output tokens, with peak allocated VRAM9,164,722,176 bytes (about8.54GiB). This excludes loading and evaluator overhead. The parent recorded1590.70 model seconds on a different desktop session; their difference is not a controlled speedup estimate. No paid GPU/API calls occurred. Failed/truncated outputs remain in the denominator.

## Verification and next decision

Public-only workflow36816233139 and frozen scoring36816280405 succeeded. The saved-evidence audit verifies original confirmation source hashes, new frozen inputs/selection, all993 candidate code hashes against scored records, the fixed dataset digest, and exact2048 output budgets. Correct/wrong/exception/malformed/timeout fixtures passed their expected statuses. The actual generator exited before its90-minute limit; no active Python or Actions experiment remained at the audit.

Reproduce the additional audit without executing candidate code:

```powershell
python -X utf8 runs/mbpp-diversity-budget-development-20261001/audit_results.py
```

Do not spend another round merely increasing temperature or reporting source diversity as accuracy. The next informative development step is a prospectively frozen paired trace-content experiment with full/no-trace anchors and truncation/filler controls, retaining completion strata and the distinction between prefill and serial compute. It still needs an executable protocol and relevant method review before launching. This temperature result does not establish causal faithfulness or justify consuming reserve. External replication remains pending provider access and evaluator feasibility; the October1 access check still found no Hugging Face login.

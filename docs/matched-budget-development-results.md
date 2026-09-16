# Output-budget control: completed development comparison

2026-09-16. Adaptive development, not independent confirmation. Fixed enrollment:100 tasks,14 public-failure triggers. All other tasks retain the selected baseline. Each arm has a2048-output-token ceiling per triggered task, with the original independent prompt, fresh frozen seeds and fixed visible-only selection.

| Method | Correct /100 | Rescues / regressions vs baseline | Extra calls | Output tokens | Input tokens |
|---|---:|---:|---:|---:|---:|
| Selected baseline |72|0 /0|0|shared|shared|
| One reasoning resample |77|5 /0|14|18,241|1,446|
| Budget-limited independent nonthinking sampling |72|0 /0|879|28,672|95,892|

The reasoning arm wins on5 tasks and loses on0 relative to the independent-sampling control: a descriptive+5 percentage-point development difference. The exploratory task-bootstrap95% interval is[1,10] points; this small adaptive sample is not independent significance evidence. There are14 treated task pairs, not879 independent tasks. Mode and sampling preset vary jointly, so this is not a causal decomposition of content versus compute.

The original additional40 cohort remains32 baseline/33 reasoning/32 nonthinking. Reassigned60 yields40/44/40 respectively. Its66.67% baseline lies between additional40's80% and historical confirmation's59.44%; this descriptive gap motivates a cohort audit, not an outcome-driven split reshuffle or a proof of exchangeability.

Reasoning completes8/14 trajectories, with5 correct extensions and6 incomplete attempts retained. Nonthinking fills each task's2048 allowance with calls capped at min(768, remaining). It uses879 calls, including partial final attempts;868 parse. Identical budget ceilings are not equal realized output tokens, input tokens, FLOPs or latency. Nonthinking spends more output tokens and many more repeated prompt tokens. All costs and failures remain in the record.

A post-hoc oracle diagnostic finds no hidden-correct candidate in any of the14 nonthinking pools, despite4–171 calls per task. Twelve tasks have only2–5 unique source strings; one has12 and the remaining counts are preserved per task in posthoc-pool-diagnostics.json. This suggests low useful diversity under this specific sampling preset, rather than a selector discarding a correct candidate. It does not rule out other nonthinking temperatures, models or prompting. Hidden oracle results were not used for selection.

The result supports further external replication of this precise contrast. It does not establish general superiority, CoT faithfulness or a mechanism-specific benefit. Reserve78 and external frozen evaluation remain untouched. Avoid another adaptive confirmation on the old180 tasks.

## Audit

Run directory:runs/mbpp-matched-budget-development-20260915. Config and generator frozen atc391b99. Completed inputs and public-selector implementation at4270814;300 decisions frozen before hidden scoring atddc8b86; analyzed results committedcbd4dea. continuation-state.json records both workflow IDs. All generated code executed only inside restricted Linux Docker.39 contract tests pass and original confirmation source hashes remain valid.

Reproduce with scripts/analyze_matched_budget.py. Generation audit and raw records preserve per-call input/output tokens, seeds and wall-time; source hashes are in budget-plan.json and score-plan.json.

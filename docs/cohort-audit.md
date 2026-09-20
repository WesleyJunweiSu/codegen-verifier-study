# Cohort audit using previously scored outcomes

2026-09-20. Descriptive analysis only; no model calls, new hidden-test access, threshold fitting or split changes. The external metadata-access permission request remains pending and was not retried.

| Cohort | Baseline correct | Accuracy | Marginal Wilson95% interval | Public-failure triggers | Error recall |
|---|---:|---:|---:|---:|---:|
| Additional development40 |32/40|80.00%|65.24–89.50%|3/40|3/8=37.50%|
| Reassigned development60 |40/60|66.67%|54.06–77.27%|11/60|11/20=55.00%|
| Historical confirmation180 |107/180|59.44%|52.15–66.35%|41/180|41/73=56.16%|

The new60 is not a repeat of the additional40's80% baseline: its observed accuracy is intermediate and its error-trigger recall is closer to historical confirmation. These observations do not prove exchangeability or identify the cause of the cohort gap. Marginal interval overlap is not a hypothesis test. Preserve the original splits rather than reshuffling them based on these outcomes.

All280 selected baseline records match the same task-specific original candidate-seed rule. Recorded torch/transformers/accelerate/tokenizers versions match across these three runs. Median selected-prompt input lengths are101.5,103 and99.5 tokens respectively; median public prompt lengths are149.5,153.5 and143.5 characters. Each has one extracted public assertion per task under the existing parser. These limited checks reveal no obvious difference in these measured setup variables; they do not establish identical task difficulty or rule out every pipeline difference.

All observed public-failure triggers are baseline errors in these saved labels, with no observed false positives. The trigger still misses5,9 and32 errors respectively. This is a post-hoc description of an unchanged policy, not a threshold proposal fitted to the historical confirmation outcomes.

The original20-task pilot is excluded from this primary comparison because it was used adaptively to develop the policy. The source manifests retain it separately; omission here does not erase its experimental history. Future external validation still requires frozen independent tasks and the existing budget-aware contrast.

Reproduce with `python scripts/audit_cohorts.py`. Source hashes, per-task covariates, package versions and full intervals are in `runs/cohort-audit-20260920/`. No external task content or reserve labels are involved.

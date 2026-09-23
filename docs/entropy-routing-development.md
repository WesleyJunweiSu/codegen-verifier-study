# Entropy routing: extra detection at substantial false-trigger cost

2026-09-23. P2 diagnostic on the already-used primary100 development tasks. No model generation or code execution; no confirmation, reserve or external evaluation labels. The fixed20% training-tail fraction and five hash-assigned folds were recorded locally before this analysis; this is adaptive analysis, not public preregistration or independent validation.

Within each fold, the entropy cutoff uses only training tasks that pass their public example. Test-fold tasks are routed if they fail the public example or exceed the training entropy cutoff. Threshold estimation uses no correctness labels. Ties are retained; no fraction search was performed. All100 selected baseline candidates have finite recorded entropy.

| Policy | Routed tasks | Errors detected | Correct answers unnecessarily routed | Missed errors | Error recall | Trigger precision |
|---|---:|---:|---:|---:|---:|---:|
| Public failure only |14|14|0|14|50.00%|100%|
| Public OR out-of-fold high entropy |30|18|12|10|64.29%|60.00%|

Entropy adds16 triggers to catch4 more errors, also routing12 correct answers. These are opportunities to spend extra generation, not demonstrated rescues or regressions. No final-answer accuracy improvement has been measured for the expanded route.

A random comparator adds exactly the same number of public-pass triggers within each held-out fold. Across10,000 fixed-seed random assignments it detects16.9216 errors on average, with a central95% assignment range of14–20. Entropy's18 lies inside that range. This is not a population confidence interval or an equivalence test; the diagnostic does not establish a reliable advantage over matched-rate random routing.

On public-pass tasks, high entropy has a descriptive error-detection AUROC of0.6944. Its Pearson correlation with log(1+output tokens) is0.0985 in that subset. This single linear check does not eliminate nonlinear length effects, task confounding or selection bias. Entropy alone and its direction were not chosen through a search over this report's results.

Keep entropy as a supplementary diagnostic; retain public-only routing as the existing experimental default while prioritizing external replication and the content/compute question. No reserve confirmation for this section. The pending external-data access request is unaffected.

Reproduce: `python scripts/analyze_entropy_routing.py`. Configuration:configs/entropy-routing-development.json. The run directory runs/entropy-routing-development-20260923 contains fold membership, training thresholds, out-of-fold decisions, source hashes and every task outcome. Randomization seed20260923;10,000 assignments. Fold counts may vary after applying a training cutoff; comparisons match actual test-fold counts.

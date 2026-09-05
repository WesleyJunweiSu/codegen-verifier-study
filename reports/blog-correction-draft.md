# Draft correction for “Agreement is not confidence”

Status: private draft, not published. Date: 2026-09-05.

> **Evaluator correction.** I re-evaluated the same saved HumanEval+ Mini candidates with official EvalPlus checking primitives inside an isolated Linux container. Seven of the 134 calibration/test labels changed; all seven belong to the 100-task historical test split. Its baseline score changes from 75/100 to 82/100. Keeping the original entropy threshold and 71 accepted tasks fixed, selective accuracy changes from 56/71 (78.87%) to 62/71 (87.32%). Error-detection AUROC changes from 0.5984 to 0.6240. The selective-accuracy lift is +5.32 percentage points; the original bootstrap algorithm gives a 95% interval of [−0.08, +11.24] points.
>
> The programs did not change. A controlled Linux reproduction of the old evaluator demonstrates false timeouts from queue join order in two cases and an output-stringification failure in one large-integer case. Two gate-policy differences are reproduced; two historical Windows timeouts remain unreproduced. The earlier numbers should be read as results under the original Windows evaluator, not as independently validated model-correctness labels.
>
> These corrections do not establish a robust selective-prediction gain or a new model result. The confidence interval remains near zero and the data are already exposed. Original artifacts remain available alongside the revised labels and diagnostic interventions.

Link to [technical report v0.2](technical-report-v0.2.md) and [metric evidence](../runs/historical-holdout/policy-reanalysis.json) when publishing. Recalculate development-stage metrics separately before changing other blog numbers; this correction covers the historical calibration/test run only. The study and drafting used AI assistance; the author should review the diagnostic claims and proposed wording.

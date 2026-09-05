# Experiment log

All entries: 2026-09-05. Workflow IDs identify exact code snapshots. Model calls ran locally; generated-code execution ran only inside restricted Linux containers.

| ID | Configuration / purpose | Outcome | Evidence |
|---|---|---|---|
| E00 | First historical evaluator dispatch | Failed before scoring: missing `datasets`. Added dependency and build-time import check. No accuracy result. | [33947032133](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/33947032133), `ee1682a` |
| E01 | Historical 134 saved candidates; EvalPlus 0.3.1; HumanEval+ Mini v0.1.10 | 104/134 pass; 7 label differences. Test subset 82/100. | [33947222594](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/33947222594), `3ac8e47` |
| E02 | Qwen3-4B BF16 non-thinking, T=0.7, top-p=0.8; MBPP+ 20×4 | 80 candidates; 3,540 tokens; 175.93 generation seconds. | `runs/mbpp-pilot-20260905/manifest.json` |
| E03 | Same model; public-spec-only generation of 8 assertions/task | 20 responses; 3,546 tokens; 176.57 generation seconds; 120 assertions; 5 responses missing `assert`. | `runs/mbpp-pilot-20260905/generated-tests.jsonl` |
| E04 | Strict parser; decisions saved before hidden scoring | First/raw/filtered 10/20; public 11/20; 0% abstention coverage; oracle 12/20; 25/120 reference rejects. | [33947394519](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/33947394519), `450fc44` |
| E05 | AST normalization + public-first selector; identical candidate/raw-test pool | 40 assertions recovered; 160 total, 158 retained; 34 reference rejects. Raw/filtered 10/20, public-first 11/20. Zero new model tokens. | [33947519157](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/33947519157), `18d8301` |
| E06 | Original legacy evaluator plus queue-order / output-stringification interventions; 7 historical cases + 2 fixtures | 29 rows, 30.08 s, zero model calls. Queue mechanism reproduced for /15 and /100; integer logging for /139; two gates reproduced; /96 and /123 Windows timeouts not reproduced. | [33992906744](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/33992906744), `b2fc1d3` |
| E07 | Post-hoc source audit of 34 reference-rejecting normalized assertions | Provisional AI-assisted annotations: 22 wrong expectations, 11 specification issues, 1 hidden-domain mismatch. Diagnostic-only; no independent human agreement check. | `runs/mbpp-parser-ablation-20260905/audit/` |
| E08 | Fixed historical entropy scores and accepted flags rescored with Linux labels | AUROC 0.6240; selective 62/71; lift +5.32 pp; original-algorithm bootstrap interval [-0.08,+11.24] pp. No retuning or fresh data. | `runs/historical-holdout/policy-reanalysis.json` |

Infrastructure: stopped a redundant Torch installation after finding the compatible old environment. Plotting packages live in ignored `.analysis-packages`, separate from model inference. Those packages require user-context execution due to Windows permissions. Checkpoint hashes were recorded after generation. None of these events counts as a model experiment.

Artifact audit identified Git's initial CRLF-to-LF conversion. Recorded workflow snapshots are retained; parsed candidates and code hashes agree. `.gitattributes` now preserves JSON/JSONL/Python bytes across platforms, and `verify_artifacts.py` permits the documented legacy normalization only for the three original workflow IDs.

All dispatched experiments above finished; artifacts imported. No GPU generation remains active. Confirmation data are unused. No rented GPU or paid model API; hosted evaluation uses GitHub Actions allowance.

The first report's final push was blocked by automatic approval because usage was exhausted. The evening continuation verified the quota had reset, checked remote state, and completed that push. No reset credit was consumed. A shell inspection also encountered the Windows GBK default encoding; the retry explicitly used UTF-8 and did not change any data.

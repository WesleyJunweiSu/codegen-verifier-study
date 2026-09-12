# Experiment log

All entries: 2026-09-05. Workflow IDs identify exact code snapshots. Model calls ran locally; generated-code execution ran only inside restricted Linux containers.

Entries E09 onward are dated 2026-09-06 America/New_York (2026-09-07 UTC).

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
| E09 | Input-only execution consensus; hidden data not mounted; same 80 candidates | 161 literal inputs; 644 single probes, 888 pair probes; 7.82 s; ordinary consensus 11/20, unique-code 10/20. Zero model calls. | [34072360167](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34072360167), `843aba5` |
| E10 | Adaptive public-first, then consensus composition after inspecting complementary rescues | 12/20, two rescues, no regressions; reaches this inspected pool's oracle. Not confirmation. No new model or execution calls. | `runs/mbpp-public-consensus-20260906/` |
| R01 | Temperature intervention feasibility check | Deferred: 7,147 MiB free vs 9,216 MiB launch threshold. Config prepared; no model loaded, no generation completed. Resource check, not a scored experiment. | `runs/mbpp-temperature-20260906/attempts.jsonl` |
| E11 (2026-09-07) | Temperature-only 0.7→1.0, same prompts/seeds/model, reused normalized tests | 80 candidates; 3,536 output tokens, 178.16 generation seconds, 7.73 GiB new generation peak. Controls and unchanged composition function audited before reading new scores. | `runs/mbpp-temperature-20260906/` |
| E12 (2026-09-07) | Frozen consensus rules applied to new temperature pool | Consensus 10/20, unique-code 10/20; 644 single probes, 891 pair probes; 7.75 s. No new model calls. | [34151733732](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34151733732), `b7d9b16` |
| E13 (2026-09-07) | Test-matrix and hidden evaluation; unchanged public-first composition persisted before score analysis | Oracle unchanged 12/20; first 10/20, public 11/20, fixed public-first consensus 11/20. Previous Mbpp/607 rescue disappears. No selector tuning. | [34151735911](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34151735911), `b7d9b16`; paired comparison JSON |

Infrastructure: stopped a redundant Torch installation after finding the compatible old environment. Plotting packages live in ignored `.analysis-packages`, separate from model inference. Those packages require user-context execution due to Windows permissions. Checkpoint hashes were recorded after generation. None of these events counts as a model experiment.

Artifact audit identified Git's initial CRLF-to-LF conversion. Recorded workflow snapshots are retained; parsed candidates and code hashes agree. `.gitattributes` now preserves JSON/JSONL/Python bytes across platforms, and `verify_artifacts.py` permits the documented legacy normalization only for the three original workflow IDs.

All dispatched experiments above finished; artifacts imported. No GPU generation remains active. Confirmation data are unused. No rented GPU or paid model API; hosted evaluation uses GitHub Actions allowance.

The first report's final push was blocked by automatic approval because usage was exhausted. The evening continuation verified the quota had reset, checked remote state, and completed that push. No reset credit was consumed. A shell inspection also encountered the Windows GBK default encoding; the retry explicitly used UTF-8 and did not change any data.

2026-09-07: the initial resource deferral was resolved with 10,915 MiB free. The temperature batch finished and passed a no-model-load resume check. Generation controls and the composition function AST were audited before new hidden scores were read. The next 40 development IDs were frozen without reading their prompts or labels; that cohort is not yet a completed experiment.


## 2026-09-08: public-failure repair and bounded reasoning scored

Six public-failure triggers from the original 20-task selected pool. Non-thinking repair 13/20 vs resample and selected baseline 12/20; 6 calls per arm, 231/230 output tokens, 11.08/10.26 generation seconds. Workflow 34165966111, source 4d5e8f9. Reasoning condition: repair 16/20 vs resampling 17/20; 6 calls per arm, 7694/9378 output tokens, 760.59/484.25 seconds. Two repair and one control attempts hit the cap without completing reasoning; retained as failures. Workflow 34304923901, source ce68578. All reused baseline labels match. This is exposed development, not confirmation; no matched-realized-compute claim. Report v0.5 and exact source/decision/data hashes saved.

Started the previously frozen 40-task development generation, 160 candidates and 40 test responses, on the local GPU with resumable per-record writes. The four-arm transfer protocol was recorded before any new-cohort scoring outcomes. The 180 confirmation labels remain untouched.


## 2026-09-09: 40-task development baseline and transfer readiness

Validated all 160 candidate keys and 40 test records against frozen config/source/seed rules. Committed inputs bece035. Isolated scoring 34422232779 and input-only consensus 34422234386 both succeeded. Composition and three public-only triggers were saved at f132231 before local hidden-label analysis. First/public/generated-test/consensus/combined policies and oracle all 32/40; zero mixed-correctness pools, 32 all-text-identical tasks. 51/320 assertions reject the reference and all 51 survive static filtering. Full extra-generation transfer is not yet scored.

Measured generation: 7378 candidate plus 7021 test output tokens, 5235.82 wall-seconds. One 4089.06-second call for 20 tokens is unexplained; retained without claiming continuous GPU activity. Peak allocation 8.54 GiB. Transfer runner prepared four arms on Mbpp/137, /777, /801; all 40 task denominators retained. First attempt at 00:43:17 UTC Sept 10 deferred before loading the model with 8404 MiB free versus the 9216 MiB guard. No paid services or precision changes. Twenty contract tests pass; artifact identities verified. Report v0.6 and checkpoint updated.


## 2026-09-10: transfer resumed and visible-only boundary validated

The frozen 12-call transfer resumed after observing 9561 MiB free; same model, prompts, seeds, caps and replacement rules. Two calls persisted at the last snapshot; the model is still generating. No new correctness result is available. Do not restart while its process is active.

Added a visible-only stage that mounts candidate/test/manifest records but no hidden dataset. Validated on the already used 40-task cohort, workflow 34538843816, source c39bc0a: all seven comparisons of public matrices, selector decisions, consensus records and composition agree. No new model calls were used for this boundary validation. Added and tested the exact paired McNemar primitive; 24 contract tests pass. A separate confirmation coordinator and immutable final-decision scorer are still needed; the 180 confirmation tasks remain unused.


## 2026-09-11: transfer completed and final confirmation frozen

Four-arm transfer scored: baseline/non-thinking arms 32/40, both reasoning arms 33/40, same Mbpp/801 rescue. Two capped unfinished reasoning responses retained. Twelve calls, 9687 tokens, 4949.37 wall-seconds; desktop timing is uncontrolled. Score workflow 34624612668, visible workflow 34624610499, input commit 1205fbd. Immutable-decision scorer 34625001045 at f067e8b exactly reproduces all 52 evaluation records and 200 frozen decisions. Report v0.7 records the smaller transferred gain, costs and failures.

Implemented final coordinator, full original-pool preservation, fixed first baseline and primary analysis; 28 contract tests pass. Final 180-task protocol frozen at 7ef1103 after implementation a10f26e, before any confirmation generation. Primary: conditional reasoning vs non-thinking resampling, paired exact two-sided McNemar with fixed intervals; no retuning/optional stopping. Attempt at 17:07:20 UTC observed 4582 MiB free and deferred before model loading; zero confirmation candidates/test responses. The next step is hardware-guarded execution of the already frozen protocol.


## 2026-09-12 — confirmation completed, routing ablation negative

- Frozen 180-task confirmation finished without intermediate correctness inspection. All 720 original candidates, 180 test responses and 82 extension candidates persisted. Final decisions committed at f44fdd6 before hidden scoring; final score workflow 34673699627 succeeded. Prespecified analysis and candidate-code hashes revalidated locally.
- First 103/180; selected baseline and nonthinking resample 107/180; reasoning resample 118/180. Primary +6.11 pp, 11 wins/0 losses, exact two-sided McNemar p=0.0009765625, paired bootstrap 95% [2.78,10.00] pp. No post-hoc primary switch.
- Post-confirmation public-trigger matrix TP41/FP0/FN32/TN107. Of 41 reasoning attempts, 26 incomplete; all retained. Extension outputs 72,297 reasoning vs 2,316 nonthinking tokens. Unequal compute and desktop timing limitations disclosed.
- Routing-v2 development artifacts imported from workflow 34670358137 at 57a8478. Seven arms verified; strict public-only comparators reproduce previous decisions exactly. Expanded routing and tie acceptance add no accuracy beyond 33/40 reasoning / 32/40 nonthinking. Six new calls, 4,673 new tokens; prior calls reused.
- Report v0.8, README, claim ledger, interview bullets and continuation checkpoint updated. 36 tests pass. No active experiment remains; calibration/reserve untouched. Further tuning belongs on development data with new independent evaluation after freezing a new protocol.

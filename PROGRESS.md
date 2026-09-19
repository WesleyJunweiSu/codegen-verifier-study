# Experiment checkpoint

Updated 2026-09-12. **Frozen 180-task confirmation complete; routing v2 and reasoning-budget development ablations complete and negative.** Read report v0.8 for the confirmed result. Older pending-state notes below are historical.

## Verified results

- Private repo: https://github.com/WesleyJunweiSu/codegen-verifier-study. Local branch codex/research-protocol, push HEAD:main.
- MBPP+ v0.2.0 split: 60 development / 60 calibration / 180 confirmation / 78 reserve. Calibration and reserve remain unused. Confirmation is now scored: never treat it as fresh tuning data.
- Original 20 development: selected 12/20, reasoning resample 17/20. Additional 40: baseline/nonthinking 32/40, reasoning 33/40. Do not present the pilot gain as confirmation.
- Final confirmation: first 103/180 (57.22%), selected and nonthinking resample 107/180 (59.44%), reasoning resample 118/180 (65.56%). Primary +6.11 pp; paired wins11/losses0; exact two-sided McNemar p=0.0009765625; bootstrap95 [2.78,10.00] pp. Full coverage through baseline fallback, not abstention.
- Public-trigger detection matrix: TP41 FP0 FN32 TN107. Final reasoning transition: wrong->correct11, correct->wrong0, correct->correct107, wrong->wrong62. Post-confirmation diagnostics only.
- Both extension arms 41 calls; reasoning72,297 output tokens vs nonthinking2,316. Reasoning27 capped/26 incomplete; all attempts retained. Common inputs720 candidates+180 test responses. Uncontrolled desktop stall in common test generation; no steady GPU/serving latency claim.
- Routing-v2 development: 6 old calls reused +6 new calls (4,673 new tokens). Every reasoning arm33/40, every nonthinking arm32/40; expanded trigger and full-public-pass tie replacement produce no extra gain. All seven methods and the one correct flagged baseline retained.

## Artifacts and provenance

- Final confirmation protocol configs/confirmation-protocol.json frozen at7ef1103, SHA4e9c553d85c58b9676f553ae1a999407f1a1dd73efafc9a837a989c46fb84b31. Bound source files remain unchanged.
- Base run runs/mbpp-confirmation-20260911; complete and committed0a87cf1. Visible-only workflow34670369963.
- Extension runs/mbpp-confirmation-extensions-20260911; complete inputs c21dc73; visible workflow34673629219. Frozen decisions committed f44fdd6 before final score34673699627. Analysis committed32fa17b. Includes summary.json, task-results.json and postconfirmation-diagnostics.json.
- Routing runs/mbpp-routing-v2-development-20260911; workflow34670358137 at57a8478. Imported visible/ and linux/, summary.json and both workflow records. Pre-generation schema-only fix preserves old plan and hash audit.
- reports/technical-report-v0.8.md is current. README, claim ledger and Chinese interview notes include the confirmed result with cost limitations.

## Active jobs and resumption

No project GPU generation or Actions job remains active. Confirmation coordinator journal runs/confirmation-continuation-20260912/state.json is complete. Session57017 finished; routing session49432 finished. Do not restart completed generators or redispatch completed scoring jobs. The routing queue file's scoring_dispatched_import_artifacts_next state is historical; its artifacts have now been imported and analyzed.

Revalidate saved results using scripts/analyze_confirmation.py, scripts/build_confirmation_diagnostics.py and scripts/analyze_routing_v2.py. The frozen analyzers check protocol/input/code/decision hashes. Thirty-six unit tests pass. Never execute generated code on the Windows host; only use restricted Linux Docker workflows. No paid GPU/API without an explicit spending cap.

## Next research decision

The current policy has a confirmed split-level gain. Expanded development routing adds cost without benefit and should not be adopted. Investigate incomplete reasoning on DEVELOPMENT tasks next: test budget/completion controls with matched comparators, all triggered tasks and retained failures. Freeze any new policy before using independent new evidence. Reserve78 must not be casually opened or repeatedly reused. The completed180 results cannot serve as another untouched confirmation of an adjusted policy.

Before claiming conference readiness, finish nearest-work reproduction and broader external/model/seed validation. No novelty, SOTA, production deployment or equal-compute superiority claim. Interview-ready evidence and quantitative bullets are in docs/interview-notes.zh.md.


## 2026-09-12 13:03 UTC — next development cap ablation prepared

See docs/development-budget-ablation.md. New fixed run mbpp-budget-development-20260912 compares cached2048 (index7) versus new4096 (index8) reasoning on all three original public-failure triggers, retaining all40 tasks. Only3 new model calls, no new tests. Generator scripts/generate_budget_development.py; config configs/development-budget.json; repair-plan and cached records already saved. Both visible-evidence and score-frozen workflow choices support this run.

First attempt deferred before model load:8849MiB free versus9216MiB guard. No active job was started, zero new calls. Resume when GPU headroom permits; do not use calendar delay as a gate. Current confirmed result remains118/180. All36 tests pass and old confirmation hashes unchanged. Follow the visible -> freeze -> hidden-score order in the budget-ablation document; do not use the four-arm-only analyze_transfer.py for the two new cap arms without adapting a separate analyzer.


## Budget batch resumed after user request

GPU free9270MiB at restart; model successfully loaded. Active generation exec session55060, parentPID25940/childPID39960. Do not launch another generator. New scripts/continue_budget.py waits for this process then validates46 records, commits inputs, dispatches/imports visible-evidence, freezes decisions, dispatches/imports score-frozen, and runs scripts/analyze_budget_development.py. Its journal lives at runs/mbpp-budget-development-20260912/continuation-state.json. Inspect journal/process before manual dispatch or staging to avoid concurrent Git operations. The analyzer checks original2048 labels, all three methods, code/decision hashes, rescue/regression matrices and cached/new cost. All36 tests pass. No new accuracy claim until final artifacts are complete.

## Current completion and cross-device entry

The budget continuation journal is now `complete`; the original visible workflow 34696110293 and final score workflow 34732911557 both succeeded. Frozen decisions and Linux evaluation were imported, analyzed and committed at c7e08cc. All 40 tasks remain: baseline32/40, reasoning_2048 33/40, reasoning_4096 33/40. Both reasoning arms have one incomplete attempt among three triggers; output tokens rise4580→6628, with zero additional rescue and zero regression for the larger cap. Do not resume this completed batch. This underpowered three-trigger result is inconclusive about larger budgets; no improvement was observed here, but the route is not ruled out. Confirmation remains118/180 versus107/180.

`AGENTS.md` in the repository root gives future Codex sessions a concise research contract; `docs/remote-access.zh.md` explains Mac/iPhone Remote setup. The currently saved Codex project is the parent Project Builder folder, so add this repository as a separate local project with this folder primary to automatically load AGENTS.md in new remote tasks. The current task is renamed and pinned. Remote host pairing requires the user's QR scan and account verification on their own devices; the project files alone cannot enable remote access.


## Concise-prompt development ablation started

Run mbpp-concise-development-20260913 freezes a task-independent concise-reasoning suffix before generation. Three cached original-prompt controls versus exactly three new calls, same seeds/sampling/BF16/2048 cap, all40 tasks and strict public replacement retained. No confirmation/reserve tuning. Config development-concise.json; generator generate_concise_development.py; continuation continue_concise.py; analyzer analyze_concise_development.py. All36 existing contract tests pass. Check the process and journal before resuming; no gain claimed before immutable Linux scoring.


## Concise-prompt batch complete

All three new calls and both isolated workflows completed; journal stage complete, result commit8f989a1. Original reasoning33/40 versus concise32/40, zero wins and one loss (Mbpp/801). Costs4580 cached versus3991 new output tokens; both have1/3 incomplete. Underpowered, inconclusive three-trigger comparison; no general rejection of concise prompting; confirmed180 result unchanged. See docs/development-concise-ablation.md. No GPU generator or continuation remains active. The first continuation launch lacked psutil in the CPU environment; resuming with the existing techblog environment completed successfully without duplicate generation/dispatch. Use that environment for process-waiting continuation scripts.


2026-09-13 interpretation correction: this small development ablation is underpowered and inconclusive about general superiority or futility. Observed counts remain valid. The budget and concise comparisons have only three paired triggered tasks; the routing study has six triggers, of which only three are newly added. The full40 denominator describes pipeline accuracy, not40 independently treated tasks. Historical no-gain language must not be read as falsification. Former calibration is now reassigned to development under split-manifest-v2.json; no new generations have been made on it.


## 2026-09-13 review corrections complete; no new generation

Report v0.9 supersedes development-ablation interpretations. Completion audit reproduces15 completed/11rescues/19049tokens versus26 incomplete/0rescues/53248tokens. Parser returns empty code for unfinished reasoning; post-selected completion association is not causal faithfulness. Actual cost72297tokens remains31.22x and6572tokens per rescue; completed-subgroup1732tokens per rescue cannot replace it. Small routing/cap/concise observations are underpowered and inconclusive, not general refutations.

User authorized reassignment of calibration60. New immutable-cohort manifest configs/split-manifest-v2.json keeps the original manifest unchanged:development120, primary100=(additional40+former calibration60), legacy20, calibration0, confirmation180, reserve78. No new model calls or reserve access. Next: baseline generation for reassigned60, visible triggers, then freeze an executable paired cap2048/4096/8192 and matched-output-budget nonthinking protocol. docs/research-direction-v2.md is design only, not a runnable frozen protocol. Related work now includes Olausson2024; full reproduction pending.


## 2026-09-13 current direction v3 and protected evaluation budget

User requested transfer of the last two reviews' reasoning into future research decisions. README headline now asks when extra serial reasoning contributes information beyond compute;118/180 is retained as motivating evidence. Current roadmap docs/research-direction-v3.md supersedes v2 scheduling. P0: new60 baseline/cohort audit and matched-budget sampling, then external benchmark and model axes. P1: paired early-answer/error/paraphrase/filler interventions with full/no-trace anchors and shared cap cohort. P2: entropy diagnostic section, no independent reserve experiment. No new generations or model downloads in this revision.

Reserve78 is reserved for ONE final frozen claim, only after external-benchmark replication and prospective precision/power assessment; no cap tuning or exploratory use. Policy configs/reserve-policy.json plus digest and AGENTS instructions preserve this rule; this is a declarative restriction, not a newly implemented runtime guard. External evaluation is also finite and must be protected against adaptive reuse.

Corrections integrated: KM cannot extrapolate beyond2048 using only2048-censored observations; historical total output length is not delimiter event time. Filler prefill does not match autoregressive compute. Normalized content contrast is unstable near zero denominator and not a causal percentage. Mechanism studies on development remain exploratory without independent replication. Cohort gaps warrant an audit, not label-driven reshuffling. Qwen2.5 is not a non-Qwen family; local GPU is12GB, not24GB; no paid spend authorized. Scope excludes serving frameworks,27B,multimodal,repo repair and new repos.90days is a milestone horizon, not mandatory waiting.

Next execution starts with new60 baseline and the budget-matched control design; check active jobs before generation. Exact external checkpoints/windows and executable intervention protocol remain to be frozen. No claim that proposed tracks have run or that faithfulness has been demonstrated.


## 2026-09-13 heartbeat: reassigned60 baseline prepared

No local Python or active Actions jobs found. Frozen configs/development-reassigned60.json and scripts/generate_reassigned60.py reuse the original baseline settings/seeds on exactly60 reassigned development tasks:240 candidates plus60 public-spec test responses. No hidden scoring or reserve access in generation. Check runs/mbpp-development60-20260913 progress and live process before resume; next step after complete generation is visible-only evaluation.


## 2026-09-14 reassigned60 generation complete

Validated all240 unique candidate keys and60 test responses, frozen generator hash, and enrollment. Total21098 output tokens,909.635 recorded generation wall-seconds. No Python jobs active. Next stage is visible-only Linux evaluation; accuracy and public-failure trigger count are not yet known. Reserve untouched.


## Reassigned60 visible-stage recovery

Workflow34846853016 failed after matrix generation because consensus CLI run-name choices omitted the new60 batch. No hidden labels loaded. New consensus_development_linux.py differs only by adding the new run name; dedicated development Dockerfile leaves original confirmation sources unchanged. Retry will preserve the failed run in journal and reuse all generation bytes. User reiterated protecting independent evaluation: next optimization remains on development only, with no reserve/external holdout scoring.


## New60 visible evidence complete; next development contrast

Retry succeeded after the CLI allowlist-only fix; artifacts committed1d37756. New60 selected baselines have11 public-failure triggers. Together with the existing additional40 cohort's3, the primary100 cohort has14 triggered tasks (not100 treated pairs). Hidden new60 correctness has not been read. This supplies a larger development cohort for the priority matched-output-budget reasoning versus independent nonthinking sampling comparison; no independent holdout or reserve is used. Trigger census saved in visible-trigger-summary.json. No new intervention generation launched in this turn; exact budget-control runner and executable protocol remain next work.


## 2026-09-15 matched-output-budget development batch prepared

No running local/Actions job found;11151MiB free. Config matched-budget-development.json and generate_matched_budget.py freeze14 public-failure tasks within primary100, two2048-output-token-ceiling arms: one reasoning call versus sequential independent nonthinking sampling. Actual tokens including truncated final sample charged; no correctness-driven stopping. New seed schedule/all new extra calls. Baselines/tests reused. Public-only best-score/earliest-index selection and strict replacement fixed before hidden evaluation. No reserve/external holdout access. Generation can resume by exact keys; isolated variable-pool selection/scoring adapter remains next work.


## 2026-09-16 matched-budget generation completed

Validated993 records:100 reused baselines plus893 new calls. Reasoning14 calls/18241 output/1446 input tokens,8 completed; nonthinking879 calls/28672 output/95892 input tokens. Same2048 output-budget ceilings do not imply equal realized cost; repeated prefill is substantial. Public-only selector adapter implements frozen strict improvement and earliest-index ties;39 tests pass and old confirmation hashes valid. Continue with scripts/continue_matched_budget.py; journal in this run. No hidden outcome inspected yet; preserve reserve.

## 2026-09-16 matched-budget batch complete

Public-only selection and frozen hidden development scoring succeeded; continuation stage complete. Baseline72/100, reasoning77/100, budget-limited nonthinking72/100:5 rescues,0 regressions,14 treated pairs. New60 contributes40 baseline/44 reasoning/40 nonthinking; old40 remains32/33/32. Reasoning14calls18241output1446inputtokens versus nonthinking879calls28672output95892inputtokens. Same ceilings, unequal realized compute.8/14 reasoning completed. Post-hoc candidate-oracle audit finds0 correct nonthinking pools/14, indicating limited useful diversity for this preset, not a demonstrated selector failure.

Full results cbd4dea; docs/matched-budget-development-results.md qualifies adaptive small-sample evidence and costs. No reserve or external evaluation used. Next priority is frozen external replication and cohort audit, not claiming causal faithfulness or spending reserve. All39 tests passed; no active generator/continuation remains.


## 2026-09-17 external replication preflight

No local/Actions jobs active; matched-budget batch remains complete. Pinned official LiveCodeBench source and dataset metadata without loading tasks or labels. All10 local checkpoint fingerprints match verified remote revision. Temporal enrollment is not frozen: distinguish repository creation, snapshot update and exact-weight publication; current dataset metadata predates the conservative snapshot bound. Upstream constructor eagerly decodes private cases, so public-only projection and separate restricted scorer are required. See docs/external-preflight.md and runs/external-preflight-20260917. No new model calls, no new experiment conclusion, reserve untouched.


## 2026-09-18 historical checkpoint verified; external metadata access needs approval

All10 files match the2025-05-19 historical checkpoint; can use a conservative May20 temporal start once eligible metadata is available. Automatic approval rejected a proposed pinned-LCB metadata census because source JSONL includes private_test_cases. Command was blocked before execution; no new task data, hidden tests, generation or evaluation. Removed downloader; do not retry indirectly. Evidence/status in external-preflight-20260917/metadata-access-block.json. Next external enrollment requires explicit permission for separated metadata projection or an official metadata-only source. Reserve remains untouched; previous development result unchanged.

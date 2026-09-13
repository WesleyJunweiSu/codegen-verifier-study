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

The budget continuation journal is now `complete`; the original visible workflow 34696110293 and final score workflow 34732911557 both succeeded. Frozen decisions and Linux evaluation were imported, analyzed and committed at c7e08cc. All 40 tasks remain: baseline32/40, reasoning_2048 33/40, reasoning_4096 33/40. Both reasoning arms have one incomplete attempt among three triggers; output tokens rise4580→6628, with zero additional rescue and zero regression for the larger cap. Do not resume this completed batch or interpret the larger budget as an improvement. Confirmation remains118/180 versus107/180.

`AGENTS.md` in the repository root gives future Codex sessions a concise research contract; `docs/remote-access.zh.md` explains Mac/iPhone Remote setup. The currently saved Codex project is the parent Project Builder folder, so add this repository as a separate local project with this folder primary to automatically load AGENTS.md in new remote tasks. The current task is renamed and pinned. Remote host pairing requires the user's QR scan and account verification on their own devices; the project files alone cannot enable remote access.

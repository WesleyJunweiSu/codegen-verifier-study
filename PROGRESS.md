# Experiment checkpoint

Updated 2026-09-12. **Frozen 180-task confirmation complete; development routing v2 complete and negative.** Read report v0.8 for the current results. Older pending-state reports are historical.

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

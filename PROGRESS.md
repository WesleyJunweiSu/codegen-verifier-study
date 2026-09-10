# Experiment checkpoint

Updated: 2026-09-10 (America/New_York). Phase: **four-arm transfer running; visible-only evidence stage verified on completed development data**.

## Objective

Build an interview-ready study and practical code-selection tool with reproducible experiments, honest failure analysis, isolated execution and independent confirmation. Produce useful results quickly; do not promise conference acceptance or invent performance gains.

## Completed evidence

- Private remote: https://github.com/WesleyJunweiSu/codegen-verifier-study
- Historical private repo reused with explicit user approval; source commit recorded in provenance.
- Local Qwen3-4B environment verified; no GPU rental required.
- MBPP+ split frozen: 60 development / 60 calibration / 180 confirmation / 78 reserve. Pilot uses 20 development tasks.
- 80 candidates and 20 independent test responses generated. Combined generation time 352.50 s excluding other overhead; peak 8.08 GiB.
- Historical Linux audit: 134 candidates, 7 changed labels, test subset 75/100 old versus 82/100 Linux. This is an evaluator change.
- Strict pilot: first/raw/filtered 10/20; public 11/20; candidate oracle 12/20; abstention returns nothing. 25/120 assertions reject reference.
- Zero-generation parser ablation: 160 assertions, 158 retained, 34 reference rejects; raw/filtered still 10/20, public-first 11/20.
- Technical report v0.1, figures, raw evidence, analysis scripts, saved-evidence CLI and nine contract tests.
- Technical report v0.2: 29 diagnostic conditions, zero model calls, 30.08 s executor runtime. Two queue-order false timeouts and one integer `repr` failure reproduced on Linux; two gate restrictions reproduced; HumanEval/96 and /123 historical Windows timeouts remain unreproduced.
- Provisional audit of all 34 normalized reference rejects: 22 wrong expectations, 11 specification ambiguities/conflicts, 1 hidden-domain mismatch. AI-assisted single-annotator judgments; not independent human truth and never selector input.
- Frozen historical policy reanalysis: AUROC 0.6240, 62/71 accepted correct; +5.32 pp selective lift with original-algorithm interval [-0.08,+11.24] pp. No threshold retuning. Private blog correction draft written; public site unchanged.
- The previous report push had been blocked by automatic approval due to exhausted usage. After the quota reset was verified, the pending commits were pushed successfully; no reset credit was consumed.
- Execution-consensus experiment: 161 inputs, 644 single-candidate probes, 888 pair probes, 7.82 s, no model calls; ordinary consensus 11/20, unique-code variant 10/20. Hidden data were not mounted in the execution container.
- Adaptive public-first then consensus composition: 12/20, two rescues, zero regressions; matches this exposed pool's oracle. Proposed after viewing complementary rescues, so not confirmation. Report v0.3 and new CLI demo recorded.
- Temperature-only intervention completed after headroom recovered: 80 new candidates, 3,536 output tokens, 178.16 generation seconds, 7.73 GiB new generation peak. Same seeds/prompts/model/settings except temperature; unchanged composition function AST verified. Tests reused byte-for-byte.
- Temperature 1.0 result: oracle unchanged 12/20, first 10/20, public 11/20, raw/filtered 10/20, consensus 10/20, public-first consensus 11/20. Prior consensus and combination rescue on Mbpp/607 disappears as four distinct no-match conventions tie. No selector retuning. Report v0.4 records the negative result.
- Next cohort protocol frozen in `configs/development-expansion.json`: remaining 40 development task IDs, excluding pilot/calibration/confirmation/reserve. Its runner is implemented and generation started during the 2026-09-08 evening follow-up.
- Public-failure repair pilot: 6 triggered tasks, one repair and one resample each, shared call caps and paired seeds. Non-thinking repair 13/20 versus selected baseline and resample control 12/20; 11.08 vs 10.26 incremental generation seconds. Mbpp/722 rescued; public-passing Mbpp/734 repair remains hidden-incorrect.
- Bounded reasoning condition: repair 16/20, reasoning resampling 17/20, baseline 12/20. Six extra calls per arm; 7,694/9,378 output tokens and 760.59/484.25 generation seconds. Two repair attempts and one resample exhaust the 2,048-token cap; retained as failures with baseline fallback. All reused labels agree. No independent confirmation or fixed-compute superiority claim.
- Report v0.5 records this result. All four conditions are frozen for the next development transfer in `configs/development-repair-transfer.json`, before reading the new cohort's scores. Confirmation readiness is described in `docs/confirmation-readiness.md`; no calendar waiting period and no unnecessary calibration gate for a threshold-free policy.

## Active jobs

Local `scripts/generate_transfer.py` is running after free VRAM recovered above the unchanged 9,216 MiB guard. Unified exec session 59239; observed model Python PID 48164 (wrapper 6812). Verify process identity and current state rather than trusting stale PIDs. Last persisted count: 2/12 extra calls, third call running. Do not launch a second model or rerun this experiment while it is active. GPU utilization remained high; completed call times are slower than the original pilot. Do not infer a cause without evidence. The final four-arm scores do not exist yet.

The 40-task baseline is fully complete: 160 candidates, 40 test responses, both Linux artifacts imported. First/public/raw/filtered/consensus/public-first consensus all 32/40, oracle 32/40, no mixed-correctness candidate pools. 32 tasks have four text-identical candidates. Static filters retain all 51 reference rejects among 320 generated assertions. Report v0.6 records the finding.

Baseline generation records 14,399 output tokens and 5,235.82 wall-seconds, including an unexplained 4,089.06-second call for 20 tokens on Mbpp/227 sample 3. Preserve the record; do not equate wall-time with active GPU time or silently exclude it. Peak allocated memory 8.54 GiB.

Scoring 34422232779 and consensus 34422234386 used bece035. Composition and the transfer plan were saved at f132231 before local analysis read labels. The four-arm transfer has 3 public-only triggers (Mbpp/137, /777, /801), 12 planned calls. Its first attempt deferred; the 2026-09-10T22:38:58Z attempt observed 9,561 MiB free and started with the same plan. Check its `progress.json`, `attempts.jsonl` and process state before any resume. No paid compute is authorized without a spending cap.

The new `visible-evidence.yml` baseline stage completed successfully on the already scored 40-task cohort: workflow 34538843816 at c39bc0a. It does not download/mount a hidden dataset. All seven record comparisons agree exactly with prior public matrices, selector decisions, consensus inputs/outcomes/decisions and composition (excluding the explanatory phase field). Artifacts are under `runs/mbpp-development40-visible-20260910/visible`, verification in `verification.json`. This is an engineering boundary check, not additional accuracy evidence. No Actions job is active. Twenty-four contract tests pass, including a tested exact paired McNemar primitive for the eventual frozen primary analysis.

## Next bounded work

1. First check the current transfer process and persisted count. Let the active run finish; only resume `scripts/generate_transfer.py --model-path C:/Users/Asuka/Documents/techblog/models/Qwen3-4B` if it has stopped and incomplete records remain. The runner checks source/plan hashes and completed candidate keys. Do not regenerate baseline experiments, lower the guard or terminate user apps to force a run.
2. When all 12 extra calls finish, verify the frozen plan/source hashes and candidate keys, commit the complete transfer run and dispatch `linux-eval.yml` with input_run `mbpp-development40-repair-20260908`. The workflow chooses the four-arm selector when `repair-plan.json` includes `arms` and persists decisions before reference loading. Import with exact workflow/commit metadata; run `scripts/analyze_transfer.py`, not the older two-arm analysis.
3. Report every arm, failure, capped response and cost. The frozen public trigger reaches only 3 of 8 incorrect tasks; even perfect transfer on these triggers would yield 35/40. This is a post-hoc diagnostic, not achieved accuracy. Do not expand triggers using hidden failures. The protocol's primary comparison remains reasoning resampling versus non-thinking resampling with measured extra cost.
4. Follow `docs/confirmation-execution-design.md` before freezing the final 180-task manifest. The visible-only stage is implemented and validated on baseline development data; the confirmation coordinator, extension-stage validation, final immutable-decision scorer and complete frozen analysis still need implementation. Do not use the old hidden-data scoring workflow as an intermediate confirmation stage: all final extension decisions must be frozen before confirmation labels are inspected. The 180 tasks remain unused. Calibrate only if the final method actually fits a threshold. Nearest-work reproduction and external-validity checks remain deliverables; current consensus is not full S*.

## Continuation rules

Read this file, the protocol, claim ledger and latest summaries. Check active GPU/Actions jobs before launching. Each batch needs configuration, source revision, costs, failures and an updated report. Commit completed batches to the private remote. Preserve negative results; distinguish development adaptations from independent tests. No paid API or rented GPU without a defined spending cap. Never execute model-generated code in the ordinary Windows environment.

Daily follow-up is scheduled for 09:00 America/New_York in this task. Notify on new results, completion, failure or needed input; stay quiet when unchanged. The user may request additional runs directly.

## Commands

GPU interpreter: `C:/Users/Asuka/Documents/techblog/.venv/Scripts/python.exe`.

Model: `C:/Users/Asuka/Documents/techblog/models/Qwen3-4B`; checksums: `configs/model-fingerprint.json`.

Analysis: `python scripts/analyze_results.py mbpp-pilot-20260905` and `python scripts/analyze_results.py mbpp-parser-ablation-20260905`.

Diagnostics: `python scripts/analyze_legacy_diagnostics.py`; semantic audit: `python scripts/build_test_audit.py`. Historical correction: run `scripts/reanalyze_historical_policy.py --numpy-bootstrap` using the existing inference interpreter with NumPy. The optional NumPy mode is required to reproduce the original bootstrap algorithm, not merely the separate stdlib RNG realization.

Demo: `python scripts/selector_cli.py --task Mbpp/564 --method public_tests`.

Latest demo: `python scripts/selector_cli.py --run mbpp-public-consensus-20260906 --task Mbpp/607 --method public_then_consensus`.

Completed temperature runner: `& 'C:/Users/Asuka/Documents/techblog/.venv/Scripts/python.exe' -X utf8 -u scripts/generate_diversity.py --model-path 'C:/Users/Asuka/Documents/techblog/models/Qwen3-4B'`. It now exits without model loading because all records exist. Do not use it to start the new 40-task cohort.

Consensus analysis: `python scripts/analyze_consensus.py`; adaptive composition analysis: `python scripts/analyze_composition.py`. Do not rerun `combine_public_consensus.py` to overwrite its frozen decisions; it deliberately refuses existing output.

Temperature comparison: `python scripts/compare_temperature.py`. New consensus analysis: `python scripts/analyze_consensus.py --run mbpp-temperature-consensus-20260907`. New composition: `python scripts/analyze_composition.py --run mbpp-temperature-public-consensus-20260907`. Frozen next-cohort config is validated with `python scripts/freeze_development_expansion.py`.

Execution: dispatch `linux-eval.yml` for the intended tracked run; download/import artifacts with `github_ops.py` and `import_artifact.py`. These use existing Git Credential Manager credentials without printing them. User-context git commands may need a scoped `-c safe.directory=<this repository>`.

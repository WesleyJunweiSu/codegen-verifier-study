# Experiment checkpoint

Updated: 2026-09-07. Phase: **paired temperature intervention complete; remaining 40-task development cohort frozen**.

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
- Next cohort protocol frozen in `configs/development-expansion.json`: remaining 40 development task IDs, excluding pilot/calibration/confirmation/reserve. No new cohort prompts or labels inspected by the freezing script. Generation for that cohort has not started.

## Active jobs

None. Temperature generation is 80/80 complete; rerunning recognizes completion and loads no model. Artifacts from consensus 34151733732 and scorer 34151735911 are imported (commit b7d9b16). Prior experiments remain complete. New 40-task development cohort has only a frozen config; no GPU process or workflow is active for it.

## Next bounded work

1. Implement a manifest-driven runner for `configs/development-expansion.json`, preserving the frozen temperature-0.7 generation/test prompts and the already chosen selectors. Check GPU headroom before loading; do not terminate user applications or change precision silently. This cohort is additional development evidence, not the reserved confirmation test.
2. Generalize current evaluation/analysis adapters from the explicit 20-task pilot to the 40-task cohort with strict task-count and completeness checks. Record workflow input/output mappings before scoring. Generate 160 candidates and 40 test responses with resumability, then persist all fixed-policy decisions before analyzing hidden labels. Retain all 40 tasks, including format/empty failures.
3. Read and implement a documented nearest-work baseline; current consensus is not full S*. Obtain independent review of semantic annotations before publication. Do not keep selecting favorable temperature/threshold settings from the original 20 cases.
4. /96 and /123 historical Windows timeouts remain unresolved; they do not block new development. After generation/selection procedures stabilize, freeze calibration and confirmation protocol. Keep all 180 confirmation labels unused.

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

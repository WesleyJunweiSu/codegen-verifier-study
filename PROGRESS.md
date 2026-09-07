# Experiment checkpoint

Updated: 2026-09-06 evening (2026-09-07 UTC). Phase: **input-only execution consensus and adaptive public-first composition complete**.

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
- Temperature-only intervention frozen (0.7→1.0; other settings, seeds and task IDs held fixed). Runner/config prepared. Headroom check found 7,147 MiB free vs required 9,216 MiB; no model loaded and no new candidates generated.

## Active jobs

None. All dispatched workflows finished and artifacts are imported. Last successful workflow: 34072360167, execution consensus at commit 843aba5. Temperature run `mbpp-temperature-20260906` contains only an attempt record (0/80 candidates); it is deferred, not running. Do not regenerate old candidates or tests.

## Next bounded work

1. Run the prepared `generate_diversity.py` with the existing inference interpreter once its headroom guard passes. It changes only temperature to 1.0 and reuses parent seeds, task IDs and normalized tests. If memory remains insufficient, record that state and work on the nearest-work comparison; do not terminate user applications or silently change precision/model.
2. When the 80 new candidates finish, dispatch `linux-eval.yml` with `mbpp-temperature-20260906`, import artifacts, and compare diversity/oracle and fixed selector outcomes with realized token/time costs. `analyze_results.py` handles separate reuse of tests versus candidates. To extend execution consensus to this new pool, record a new workflow input/run mapping and preserve the same consensus policy. The adaptive public-then-consensus policy should remain fixed for the new condition.
3. Read and implement a documented nearest-work baseline; present current consensus as a simple baseline, not full S*. Consider a new development-task batch only with a recorded task manifest. Obtain independent review of semantic annotations before publication.
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

Next generation: `& 'C:/Users/Asuka/Documents/techblog/.venv/Scripts/python.exe' -X utf8 -u scripts/generate_diversity.py --model-path 'C:/Users/Asuka/Documents/techblog/models/Qwen3-4B'`. The runner checks available VRAM before importing/loading the model and records attempts. `--check-only` performs just the resource check.

Consensus analysis: `python scripts/analyze_consensus.py`; adaptive composition analysis: `python scripts/analyze_composition.py`. Do not rerun `combine_public_consensus.py` to overwrite its frozen decisions; it deliberately refuses existing output.

Execution: dispatch `linux-eval.yml` for the intended tracked run; download/import artifacts with `github_ops.py` and `import_artifact.py`. These use existing Git Credential Manager credentials without printing them. User-context git commands may need a scoped `-c safe.directory=<this repository>`.

# Experiment checkpoint

Updated: 2026-09-05. Phase: **first pilot, parser ablation and historical audit complete**.

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

## Active jobs

None. GPU generations and all three successful Linux evaluations are complete; artifacts imported. Do not repeat completed model calls. Last successful workflow: 33947519157, parser ablation at commit 18d8301. Initial failed workflow 33947032133 is retained in the log.

## Next bounded work

1. Audit the 34 normalized reference-rejecting assertions against public specifications. Separate wrong expectations, invalid inputs and ambiguity; keep reference information out of selectors.
2. Resolve four historical timeout differences and HumanEval/139 with controlled Linux evaluator diagnostics. Two static policy-gate differences already have direct source explanations.
3. Freeze one candidate-diversity intervention on development data, with selectors fixed and measured token/time costs. `generate_batch.py` currently uses `split['pilot']`; extending to all development tasks requires a recorded configuration change.
4. Implement execution-consensus and a documented nearest-work baseline. Current pass-count selection is not S* reproduction.
5. After a useful selector exists, freeze calibration rules and confirmation protocol. Do not use any of the 180 confirmation labels during development.

## Continuation rules

Read this file, the protocol, claim ledger and latest summaries. Check active GPU/Actions jobs before launching. Each batch needs configuration, source revision, costs, failures and an updated report. Commit completed batches to the private remote. Preserve negative results; distinguish development adaptations from independent tests. No paid API or rented GPU without a defined spending cap. Never execute model-generated code in the ordinary Windows environment.

Daily follow-up is scheduled for 09:00 America/New_York in this task. Notify on new results, completion, failure or needed input; stay quiet when unchanged. The user may request additional runs directly.

## Commands

GPU interpreter: `C:/Users/Asuka/Documents/techblog/.venv/Scripts/python.exe`.

Model: `C:/Users/Asuka/Documents/techblog/models/Qwen3-4B`; checksums: `configs/model-fingerprint.json`.

Analysis: `python scripts/analyze_results.py mbpp-pilot-20260905` and `python scripts/analyze_results.py mbpp-parser-ablation-20260905`.

Demo: `python scripts/selector_cli.py --task Mbpp/564 --method public_tests`.

Execution: dispatch `linux-eval.yml` for the intended tracked run; download/import artifacts with `github_ops.py` and `import_artifact.py`. These use existing Git Credential Manager credentials without printing them. User-context git commands may need a scoped `-c safe.directory=<this repository>`.

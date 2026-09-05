# Experiment checkpoint

Updated: 2026-09-05. Phase: first implementation and pilot execution.

## Current objective

Build an interview-ready, research-quality study of imperfect code verifiers, candidate selection and abstention. Move quickly through concrete experiments while preserving independent confirmation data and negative results. No claim of conference acceptance or new state of the art.

## Completed

- Created private GitHub repository and pushed initial protocol.
- Recovered prior private research with explicit user authorization.
- Located working local GPU environment and Qwen3-4B weights.
- Downloaded MBPP+ v0.2.0 and froze 60 development / 60 calibration / 180 confirmation / 78 reserve tasks.
- Exported generator-visible prompt fields without hidden data.
- Implemented resumable generation and restricted Linux evaluation workflow.

## Active work

- Local run `mbpp-pilot-20260905`: 20 development tasks × 4 candidates. Progress is saved after each generation in `runs/mbpp-pilot-20260905/progress.json`.
- Historical Linux reevaluation: 134 saved candidates; workflow dispatch and outputs tracked next.

## Next actions

1. Check the running process before starting another GPU job. Do not duplicate run IDs or re-sample completed candidate keys.
2. Validate generated outputs and the Linux evaluator with known fixtures.
3. Compare historical Windows and Linux labels and report every disagreement.
4. Generate specification-derived tests, execute a candidate/test matrix in the restricted container, and compare selector baselines on the development pilot.
5. Freeze the method/operating point before using calibration or confirmation labels for their respective roles. The 180 confirmation tasks are not part of the current run.

## Continuation rules

Read this file, `docs/pilot-protocol.md`, the claim ledger and the latest run progress. Log every experiment's exact configuration, data/model hashes, code revision, cost and failure modes. Update this checkpoint and commit meaningful completed batches to the private repository. Never claim a running or failed experiment as completed. No GPU rental or paid API calls without a defined spending cap. Do not execute generated code in the Windows host environment.

## Commands

Local generation uses the already working interpreter:

```powershell
& 'C:/Users/Asuka/Documents/techblog/.venv/Scripts/python.exe' -u scripts/generate_batch.py --model-path 'C:/Users/Asuka/Documents/techblog/models/Qwen3-4B'
```

For Linux scoring, use the `Isolated Linux evaluator` GitHub Actions workflow; choose the intended tracked run. Record the workflow run ID and download its artifacts before reporting scores.

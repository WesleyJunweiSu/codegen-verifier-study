# Code Generation Verifier Study

Status: research protocol and project planning. No new model experiments have been run in this repository.

This project follows Wesley Junwei Su's research blog, [Agreement is not confidence](https://github.com/WesleyJunweiSu/WesleyJunweiSu.github.io/blob/main/app/page.tsx).

The next question is: **when generated tests are imperfect, can a budget-limited code selector distinguish correct candidates from correlated mistakes, and recognize when it lacks enough evidence to select?**

The intended deliverable is a reproducible evaluation harness and a small local CLI that returns a candidate with execution evidence, or declines to select. Passing generated tests is evidence, not a proof of correctness.

## Contents

- [中文选题建议与求职规划](docs/project-recommendation.zh.md)
- [Pilot protocol](docs/pilot-protocol.md)
- [Related work](docs/related-work.md)
- [Claim ledger](docs/claim-ledger.md)
- [Draft pilot configuration](configs/pilot.json)

## Scope

Start with one 4B open-weight model and Python function tasks. Isolate candidate generation from selection. Compare first-candidate, execution-consensus, test-guided selection, and a quality-filtered selector with optional abstention. Preserve hidden evaluation tests for final scoring only.

This is an empirical replication-and-extension project. Test-guided selection is established prior work; no novelty or performance improvement is claimed.

## Local hardware

Observed on 2026-09-05 via nvidia-smi: NVIDIA GeForce RTX 5070 Ti Laptop GPU, 12,227 MiB memory, driver 610.62. Qwen3-4B is the initial model to preserve continuity with the previous study. Runtime compatibility, peak VRAM, and throughput still need a smoke test.

The old blog links to `WesleyJunweiSu/codegen-uncertainty-research`, which was not in the unauthenticated public repository listing. Its raw generations, split manifests and evaluator implementation were not available for this planning pass. Do not treat the blog's numbers as independently reproduced.

## Implementation status

Only planning documents and a draft configuration exist. There is no runnable experiment entry point yet. The first implementation milestone is an evaluator contract plus an isolated Linux execution environment, followed by a 20-task smoke run.

No model download, GPU rental, GitHub publication, or benchmark execution has been performed for this project.

# Provenance and environment

2026-09-05:

- User explicitly authorized reading/cloning the private previous study.
- Previous repository: `WesleyJunweiSu/codegen-uncertainty-research`, commit `de64b309a1ff1b8942916d183142b5fb1f035c6d`.
- `src/verifier_study/generation.py` is copied without changes from `src/darc/generation.py` at that revision, preserving the previous generation implementation for comparability. It is the user's own prior private research code.
- `runs/historical-holdout/` contains the prior 134 generation records, Windows labels, and frozen historical split. These are historical results, not new model samples.
- New MBPP+ dataset: official release `v0.2.0`, 378 tasks, SHA256 `b54e762755248ca411b523c917fa9f93c07b5ff2966bf60b3917b853926a3dad`.
- MBPP+ original data remain local. Only task ID, prompt and entry point are exported for generation. Hidden inputs, reference implementation, contract and assertion fields are excluded.
- Initial environment reused from `C:/Users/Asuka/Documents/techblog/.venv/`; torch `2.11.0+cu128`, transformers `5.13.0`, Python `3.12.14`; CUDA available, device capability `(12, 0)`.
- Model reused locally from the previous study. Its configuration hash is recorded per run. Full checkpoint content identity still needs a checksum manifest before publication.
- A separate torch 2.8 installation was stopped after locating the existing environment. That partial project `.venv` is not used for experiments.
- Linux evaluator pins `evalplus==0.3.1`. Official corresponding Git commit: `e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2`. The wrapper uses upstream checking primitives with custom serial orchestration; it is not a byte-for-byte run of the upstream CLI.
- Evaluation runs on a disposable GitHub-hosted Linux runner inside a non-root, network-disabled, read-only Docker container with constrained memory, CPU and processes. Only task data and the selected run are read-mounted; only the output directory is writable.

This repository is private. Public release requires reviewing the personal planning documents and inherited private material separately.

# External source discovery: LiveCodeBench Pro

2026-09-25. Preparation completed; no new model experiment or enrollment freeze. Evidence: `runs/external-source-discovery-20260925/manifest.json`.

## Source decision

The original LiveCodeBench Lite API still reports revision `0fe84c3912ea0c4d4a78037083943e8f0c4dd505`. Its previously completed census has no eligible tasks from2025-05-20. Do not repeat that4.49GB acquisition or infer that a mirror has newer contests.

The [LiveCodeBench Pro authors' toolkit](https://github.com/GavinZhengOI/LiveCodeBench-Pro) links a separate problem dataset and testcase repository. This is a different benchmark, not release_v7 of the original. Toolkit source is pinned at `d614eef4f95b3654bf0758c64e1194b2575850b8`.

| Resource | Pinned revision | Finding |
|---|---|---|
| [Problem dataset](https://huggingface.co/datasets/QAQAQAQAQ/LiveCodeBench-Pro) | `adebffce047dddb7768a86bace6aea4f7425e3bc` | Public card lists `quater_2025_7_9`,144 rows; dataset is gated (`auto`) |
| [Testcase repository](https://huggingface.co/datasets/QAQAQAQAQ/LiveCodeBench-Pro-Testcase) | `5257736c0a4e30ba0949d41c56a257c323d9c600` | Public file inventory has706 ZIPs; no archive downloaded or inspected |

The quarter name is a promising date screen, not a verified per-task date census. The declared problem schema has ID, title, difficulty, statement, platform, link and resource limits, **no individual release-date column**. Exact contest dates and overlap with the earlier LCB task IDs need independent metadata checks. Quarterly and biannual splits overlap; summing them would inflate independent task count.144 is a candidate pool size, not a guarantee of144 eligible, judgeable or adequately powered tasks. Testcase snapshot predates the latest problem-dataset update; matching coverage must be checked by ID before enrollment.

## Actual access state and user action

Anonymous HEAD of the pinned quarter Parquet returned401; no response body or task row was read. The standard Hugging Face token lookup found no existing local token. This is the data provider's access gate, not a new automatic-approval rejection or a request to reauthorize the previous metadata census.

The user needs to open the problem-dataset link, sign in, review/accept its access conditions if appropriate, then authenticate the Windows environment using the locally installed CLI:

```powershell
& 'C:/Users/Asuka/Documents/techblog/.venv/Scripts/hf.exe' auth login
```

`hf auth login --help` was checked locally and supports browser or token login. Complete the interactive login locally; do not paste a token into chat or commit it. Do not accept provider conditions on the user's behalf or use mirrors to evade the gate. After the user reports completion, check access without exposing credentials, then acquire the approved metadata/public projection at the pinned revision. No request for paid compute is involved.

## Evaluator feasibility before any model generation

The pinned [benchmark](https://github.com/GavinZhengOI/LiveCodeBench-Pro/blob/d614eef4f95b3654bf0758c64e1194b2575850b8/benchmark.py) and prompt default to C++. The [judge integration](https://github.com/GavinZhengOI/LiveCodeBench-Pro/blob/d614eef4f95b3654bf0758c64e1194b2575850b8/judge.py) lists Python3/PyPy3 support, but also launches a privileged container, downloads testcases on demand without a dataset revision, and extracts ZIP paths directly. We only read source; none of that code was imported or run.

Python availability in an enum does not establish that all tasks or custom checkers work under our constraints. Retain Python for a prospective same-model benchmark comparison only after restricted Linux fixtures verify execution and checker semantics. Otherwise treat C++ as an additional experimental factor and freeze a separate design. Do not silently attribute a language-plus-benchmark change to benchmark generalization alone. Do not run the upstream privileged launcher on the host or introduce a new serving framework.

Required adaptation: public-only prompts/examples; hidden archives available only to the frozen scorer; pinned archive hashes; safe extraction; restricted nonprivileged Linux execution with resource limits; fixture coverage for correct/wrong/timeout/exception/malformed output and checker behavior. Archive availability alone does not validate the evaluator. Use existing Docker evaluation conventions where sufficient; document any incompatibility before choosing a different candidate benchmark.

## Continuation

1. Resolve provider access, then project IDs/platform/difficulty/links and verify contest dates, duplicate IDs and testcase availability without decoding hidden tests.
2. Assess usable independent count and prospective precision; freeze separate external development/final IDs before outcomes. Preserve the2025-05-20 temporal screen and reserve78.
3. Validate public-only adapters and restricted execution on synthetic fixtures. Freeze inference prompts, the reasoning/iid control, budgets and language choice before model calls.
4. If access or evaluator feasibility remains unresolved, advance a separately frozen experiment on already-exposed MBPP development. Do not spend reserve or run more external task searches based on model scores.

No answer accuracy, faithfulness, contamination-free status or external replication is established by this preflight. Source discovery did not consume an independent scoring opportunity.

# LiveCodeBench external preflight

**Current status2026-09-24:** metadata access is authorized and the census is complete. The pinned snapshot has0 tasks meeting the prospective2025-05-20 date bound. Locate a newer official snapshot; do not repeat the completed census. Details and historical status follow.

2026-09-17. Preparation only: no benchmark tasks, private tests, labels or model calls loaded. No independent evaluation opportunity spent.

Official evaluator pinned at28fef95ea8c9f7a547c8329f2cd3d32b92c1fa24. Dataset metadata revision0fe84c3912ea0c4d4a78037083943e8f0c4dd505, files test.jsonl through test6.jsonl. Metadata does not establish eligible task dates. The homepage's older coverage description is not a reliable current enrollment inventory.

The10 files in our local checkpoint fingerprint all match Qwen/Qwen3-4B revision1cfa9a7208912126459214e8b04321603b3df60c via remote LFS digests/small-file SHA256 checks. Repository creation is2025-04-27; current revision metadata lastModified is2025-07-26. Neither establishes a training cutoff or the first publication date of every identical weight blob. Before freezing a post-release window, audit weight-history dates or conservatively use the verified snapshot publication bound. Dataset metadata lastModified is2025-06-05; if the conservative July bound yields no eligible tasks, do not silently relax the temporal criterion or pretend the evaluation is post-cutoff. Locate an appropriate newer official snapshot or verify earlier identical-weight publication.

The upstream CodeGenerationProblem constructor eagerly decodes private tests, including a pickle fallback, and its evaluation sample combines public/private cases. Do not instantiate it in the visible stage. Use an explicit public-field projection for generation and routing. Decode/evaluate private cases only in restricted Linux after decisions freeze. Implement and verify separate STDIN and functional-task harness paths; our MBPP assertion runner cannot be reused unchanged. The upstream testing utility executes candidate code and is not itself the Docker boundary.

Next bounded work: verify temporal enrollment metadata without inspecting private tests; freeze external development versus final evaluation IDs; validate public-only adapters on synthetic fixtures; estimate available task/trigger counts and interval width before committing a final cohort. Existing protected MBPP reserve remains unused. Preserve the same arm definitions and account for input/output tokens; do not select dates/tasks using model correctness.

Source digests and API metadata: runs/external-preflight-20260917/manifest.json. Exact model digest comparison: checkpoint-match.json. Upstream reference sources are cached outside the repository; never execute them on the host.

Sources: [official repository](https://github.com/LiveCodeBench/LiveCodeBench), [project](https://livecodebench.github.io/), [Qwen release overview](https://qwenlm.github.io/blog/qwen3/), [model metadata](https://huggingface.co/api/models/Qwen/Qwen3-4B), [dataset metadata](https://huggingface.co/api/datasets/livecodebench/code_generation_lite).

## 2026-09-18 update

All10 local files also match historical revision8136a03248eac0530d0f630f9a4e21810f9137de (2025-05-19T07:44:39Z). The July snapshot bound is therefore unnecessarily late; a prospective2025-05-20 start can use identical published files. This does not establish a training cutoff. Proof is historical-checkpoint-match.json.

Metadata census was NOT run: automatic approval rejected the proposed JSONL projection because raw rows include private_test_cases, even if left opaque and discarded. No task data was downloaded by that action. Downloader removed; no indirect retry. Need explicit permission for a strictly separated metadata projection or an official metadata-only artifact before enrollment can be frozen. Current work is preparation, not evaluation.

## 2026-09-24 authorization update

The user explicitly approved the pending metadata read. Scoped authorization is recorded in `runs/external-metadata-20260924/authorization.json`; the September18 rejection remains unchanged as history. The bounded downloader parses JSON framing in memory and retains only platform, question_id, contest_date and difficulty. It does not decode, display or persist private-test payloads, import the upstream loader, or score any task. This resolves the permission dependency for metadata projection only; external enrollment and model evaluation are separate future stages.

The completed census found **1055 unique tasks**, dated2023-05-07 through **2025-04-06**. **Zero tasks** satisfy the previously proposed2025-05-20 start. The pinned dataset's June5 repository update does not imply June contest coverage. All six complete-file digests matched their official LFS hashes. Four-field metadata, sources, costs and two failed resource-limit attempts are retained in `runs/external-metadata-20260924`; private-test payloads were never decoded, displayed or persisted. The six source files total4,485,994,821 bytes, illustrating why repository metadata alone was insufficient to establish enrollment.

Next decision: find a newer official dated snapshot, first using repository/file metadata, before freezing an external cohort. If none is suitable, propose a different external distribution and state its contamination limitations. Do not relax the date criterion after discovering this empty cohort; do not generate on an empty enrollment. The metadata permission issue is resolved; data-window suitability is now the obstacle. No external scores, model calls or MBPP reserve access occurred.

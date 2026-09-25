# Authorized LiveCodeBench metadata census

Completed2026-09-24 local date (UTC timestamps are2026-09-25). This is an acquisition and eligibility check, not an experiment with model answers.

- `authorization.json`: user approval resolving the earlier metadata-access rejection.
- `manifest.json`: final source/script hashes, resource bounds, actual wall time and downloaded bytes.
- `summary.json`:1055 tasks, latest contest2025-04-06, zero eligible from2025-05-20.
- `task-metadata.json`: four approved fields only; no prompts, code or tests.
- `eligible-metadata.json`: empty; do not launch generation for this cohort.
- `test*.jsonl.metadata.json`: validated per-file metadata checkpoints and original-file LFS digests. These files contain projected metadata, not source JSONL records.
- `attempt-1/`, `attempt-2/`: preserved failed manifests and exact downloader versions. Attempt1 hit the16MiB line limit (diagnosed when raising only the limit allowed the first file to finish); attempt2 exceeded2GiB. Its saved phase says `line_size_check` because that version did not update the phase before the later total-size check. The recorded total exceeds2GiB, locating the limit. Neither failure is a model negative result.

The final source size bound is the exact sum of official pinned file sizes,4,485,994,821 bytes. All final complete-file hashes match. Earlier attempts also transferred bytes; their costs must not be omitted when accounting for acquisition. Attempt1's count omits the oversized rejected line and is a lower bound. Raw task rows and private payloads were never persisted, displayed, decoded as tests or evaluated. Python parsed JSON framing in memory to project the approved fields.

Next work is newer official snapshot discovery and prospective enrollment. No date relaxation, new independent evaluation claim or reserve access is justified by this census.

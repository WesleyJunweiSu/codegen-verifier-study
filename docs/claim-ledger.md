# Claim ledger

Updated 2026-09-08. Distinguish observation, hypothesis and unfinished work.

| Claim | Evidence | Permitted wording |
|---|---|---|
| New research repository exists | Private remote, commits and Actions verified | Built and versioned a research harness. |
| Local 4B BF16 inference is feasible | 80 candidates + 20 test responses; peak 8.08 GiB | Ran Qwen3-4B locally on an RTX 5070 Ti Laptop. |
| Linux audit changes historical results | Same 134 candidates; 7 changed labels; historical test 75→82/100 | Evaluator-dependent label differences, not model improvement. |
| Old entropy metrics remain unchanged under Linux | Recomputed with fixed scores/acceptance; AUROC 0.5984→0.6240 | Label correction changes historical metrics, not model capability. |
| All seven historical discrepancies are causally explained | Two queue and one integer-logging mechanism reproduced in Linux; two gate restrictions reproduced; two timeouts unresolved | Report the mechanisms and platform limitation separately. |
| New generated-test selector improves accuracy | Not established: raw/filtered 10/20, same as first | No observed benefit in this development pilot. |
| Conditional extra generation improves this development pilot | Baseline 12/20; non-thinking repair 13, reasoning repair 16, reasoning resample 17; all six public-failure triggers retained | Observed development gains with additional generation; report full cost and independent confirmation pending. |
| Feedback repair is the best use of reasoning | Reasoning repair 16/20 versus reasoning resample 17/20; equal call caps, different realized cost | Feedback superiority is not supported by this pilot. |
| The 17/20 result generalizes | Same 20 exposed tasks; adaptive development; 40 new development tasks still generating | Do not claim a confirmed 25-point gain or use this as a production accuracy estimate. |
| Public tests beat first candidate generally | Only one pilot rescue | Public examples rescued one of 20 pilot tasks. |
| Execution consensus improves selection generally | Frozen development comparison: 11/20 versus 10/20 first; one rescue | Input-only consensus rescues one inspected development task. |
| Public-first consensus is proven better | Original adaptive pool 12/20; unchanged policy on temperature 1.0 pool 11/20; first remains 10/20 | Development behavior is sampling-dependent; no general improvement established. |
| Removing duplicate-code votes helps | Unique-code variant returns 10/20 versus ordinary consensus 11/20 | Deduplication removes the useful vote margin in one case; no universal conclusion. |
| Temperature diversity experiment has run | Completed 80 new candidates with paired seeds; 3,536 output tokens, 178.16 generation seconds | Temperature-only intervention completed locally with reused tests. |
| Higher temperature improves useful diversity | Distinct source count 30→32, all-identical tasks 13→14, oracle unchanged 12/20 | Slightly more source variants did not increase oracle availability in this run. |
| Static filtering detects incorrect tests | All reference rejections survive | Current filters miss semantic defects. |
| Assertion normalization improves correctness | Recovers 40 assertions; no selection gain | Fixed a format failure without demonstrated correctness gains. |
| Abstention controls risk usefully | Returns 0/20 | Fixed rule is unusable; calibration unfinished. |
| Reference-rejecting tests are all wrong | Post-hoc AI-assisted audit: 22 wrong expectations, 11 specification issues, 1 hidden-domain mismatch; not independently human-reviewed | Present provisional categories and rationales, not definitive labels. |
| Work is novel / conference-ready | Direct prior art; no complete reproduction or confirmation | Research prototype and exploratory technical report. |
| System is deployed / used by others | No deployment or external users | Runnable harness and saved-evidence CLI. |
| Results generalize to data-science workflows | Not tested | DS transfer is planned. |
| All resume metrics verified | Not done | Treat resumes as background. |

Evidence: `runs/`, technical report, experiment log. Never describe inherited generations as new calls or oracle/reference filtering as deployable. Confirmation data remain reserved.

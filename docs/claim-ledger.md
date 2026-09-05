# Claim ledger

Updated 2026-09-05. Distinguish observation, hypothesis and unfinished work.

| Claim | Evidence | Permitted wording |
|---|---|---|
| New research repository exists | Private remote, commits and Actions verified | Built and versioned a research harness. |
| Local 4B BF16 inference is feasible | 80 candidates + 20 test responses; peak 8.08 GiB | Ran Qwen3-4B locally on an RTX 5070 Ti Laptop. |
| Linux audit changes historical results | Same 134 candidates; 7 changed labels; historical test 75→82/100 | Evaluator-dependent label differences, not model improvement. |
| Old entropy metrics remain unchanged under Linux | Recomputed with fixed scores/acceptance; AUROC 0.5984→0.6240 | Label correction changes historical metrics, not model capability. |
| All seven historical discrepancies are causally explained | Two queue and one integer-logging mechanism reproduced in Linux; two gate restrictions reproduced; two timeouts unresolved | Report the mechanisms and platform limitation separately. |
| New generated-test selector improves accuracy | Not established: raw/filtered 10/20, same as first | No observed benefit in this development pilot. |
| Public tests beat first candidate generally | Only one pilot rescue | Public examples rescued one of 20 pilot tasks. |
| Static filtering detects incorrect tests | All reference rejections survive | Current filters miss semantic defects. |
| Assertion normalization improves correctness | Recovers 40 assertions; no selection gain | Fixed a format failure without demonstrated correctness gains. |
| Abstention controls risk usefully | Returns 0/20 | Fixed rule is unusable; calibration unfinished. |
| Reference-rejecting tests are all wrong | Post-hoc AI-assisted audit: 22 wrong expectations, 11 specification issues, 1 hidden-domain mismatch; not independently human-reviewed | Present provisional categories and rationales, not definitive labels. |
| Work is novel / conference-ready | Direct prior art; no complete reproduction or confirmation | Research prototype and exploratory technical report. |
| System is deployed / used by others | No deployment or external users | Runnable harness and saved-evidence CLI. |
| Results generalize to data-science workflows | Not tested | DS transfer is planned. |
| All resume metrics verified | Not done | Treat resumes as background. |

Evidence: `runs/`, technical report, experiment log. Never describe inherited generations as new calls or oracle/reference filtering as deployable. Confirmation data remain reserved.

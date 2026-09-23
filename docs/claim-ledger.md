# Claim ledger

Updated 2026-09-11. Distinguish observation, hypothesis and unfinished work.

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
| The 17/20 result generalizes | New 40-task transfer: reasoning 33/40 vs baseline/nonthinking 32/40; one rescue, no feedback advantage | Development effect is smaller on new tasks; no confirmed 25-point gain or production accuracy estimate. |
| Independent confirmation is complete | Frozen 180-task final score: reasoning 118/180 vs nonthinking/selected 107/180; 11 wins, 0 losses; exact p=0.0009766 | +6.11 percentage points on this held-out split; unequal compute, one model/benchmark/seed schedule. |
| Frozen decisions survive separate scoring | 52 development evaluation records and 200 frozen decisions exactly match in score-frozen validation | Validated separated visible-evidence and immutable-decision scoring paths. |
| Selection fixes the new cohort's errors | First, tested selectors and oracle all 32/40; no mixed-correctness candidate pools | No selector gain on this realized 40-task pool; generation remains the limiting factor. |
| Public-failure routing reaches all incorrect programs | Only 3 of 8 incorrect selected programs fail public examples | At most 35/40 under this frozen trigger, even with perfect new answers on triggered tasks; not achieved performance. |
| Recorded generation time is stable GPU throughput | 5,235.82 wall-seconds includes one 4,089.06-second, 20-token call with unestablished cause | Report raw wall-time and anomaly; no active-GPU or serving-latency claim. |
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
| Work is novel / conference-ready | Completed confirmation but direct prior art and no full nearest-work reproduction or broad external validation | Reproducible research prototype with a confirmed split-level gain; no novelty/SOTA or acceptance claim. |
| System is deployed / used by others | No deployment or external users | Runnable harness and saved-evidence CLI. |
| Results generalize to data-science workflows | Not tested | DS transfer is planned. |
| All resume metrics verified | Not done | Treat resumes as background. |

Evidence: `runs/`, technical report, experiment log. Never describe inherited generations as new calls or oracle/reference filtering as deployable. Confirmation scoring is complete; calibration and reserve remain unused.

2026-09-12 update: expanded-routing and full-public-pass tie acceptance remain 33/40 on development, with no extra rescue. Screening recall improvement is not an accuracy improvement. See report v0.8.

2026-09-12 budget update: increasing the reasoning cap from 2048 to 4096 on the same three development triggers leaves accuracy 33/40 and incomplete responses 1/3 in each arm, while output cost rises from 4,580 to 6,628 tokens. This underpowered comparison is inconclusive about the method; the frozen 180-task confirmation result remains unchanged.

2026-09-13 concise-instruction update: same2048 cap and seeds, all40 development tasks, three public-failure triggers. Concise32/40 versus original reasoning33/40;0 additional wins,1 loss;3991 versus4580 output tokens,1/3 incomplete each. Cost reduction is not an accuracy improvement; this underpowered comparison is inconclusive about general effectiveness. Full evidence in docs/development-concise-ablation.md.


2026-09-13 interpretation correction: this small development ablation is underpowered and inconclusive about general superiority or futility. Observed counts remain valid. The budget and concise comparisons have only three paired triggered tasks; the routing study has six triggers, of which only three are newly added. The full40 denominator describes pipeline accuracy, not40 independently treated tasks. Historical no-gain language must not be read as falsification. Former calibration is now reassigned to development under split-manifest-v2.json; no new generations have been made on it.

2026-09-13 v0.9: completion11/15 versus0/26 is descriptive post-treatment grouping, not causal effect. Actual31.22x token ratio stays;8.22x is completed-subgroup accounting only. No demonstrated4x optimization or CoT faithfulness result. Former calibration is now development under split v2; old statements about unused calibration are historical. New experiments remain planned.

2026-09-13 direction v3: content-versus-compute is now the research question, not a proven causal claim.118/180 remains motivating evidence. No external replication or trace intervention has run. Reserve policy is standing; mechanism ratios, filler controls, censoring and cohort diagnostics carry the limitations in direction-v3. No verified contamination or code-domain novelty claim.

2026-09-16 matched-output-ceiling development comparison:77/100 reasoning versus72/100 baseline and independent nonthinking sampling;5 wins0losses on14 triggered tasks. Reasoning uses18241outputtokens;879 nonthinking calls use28672outputtokens and95892inputtokens. This is adaptive development evidence with unequal realized compute, not independent confirmation or content causality. Post-hoc nonthinking oracle pools have0/14 correct candidates. See docs/matched-budget-development-results.md.

2026-09-20 cohort audit:reassigned60 baseline66.67% lies between additional40 80% and historicalconfirmation59.44%. Seed-rule/runtime checks pass; measured prompt lengths are similar. This descriptive audit does not prove exchangeability, absence of contamination, or a broken split. No outcome-driven reshuffle justified.

2026-09-23 entropy diagnostic:out-of-fold routing detects4 additional development errors at16 extra triggers, including12 correct baselines. Recall64.29% vs50%,precision60% vs100%; matched random distribution contains the entropy count. This is detection only, not rescue or reliable superiority; no reserve experiment warranted.

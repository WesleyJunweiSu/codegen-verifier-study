# Conditional resampling: completion bottleneck and budget-aware next experiments

2026-09-13. Supersedes v0.8's interpretation of the development ablations; historical protocols and raw results remain unchanged. Qwen3-4B BF16, MBPP+ v0.2.0.

## Main result and its limits

The frozen 180-task comparison remains reasoning118/180 versus nonthinking107/180: +6.11 percentage points, 11 wins and0 losses, paired-bootstrap95% interval[2.78,10.00] points and prespecified exact McNemar p=0.0009765625. The selected baseline is107/180 and first candidate103/180. These are the original result, not a fresh replication. Mode, sampling settings and caps differ jointly; the arms are matched in calls, not compute.

New post-hoc accounting shows that26 unfinished attempts consumed53,248 of72,297 reasoning output tokens (73.65%) and yielded no selected-answer rescue. This identifies a concrete completion bottleneck worth intervening on, not an established fourfold optimization. Actual extra reasoning cost remains31.22 times the nonthinking arm and6,572 tokens per rescue, excluding shared baseline generation and tests.

## Completion by rescue: descriptive 2×2

| Reasoning outcome | Rescue | No rescue | Attempts | Conditional rescue rate |
|---|---:|---:|---:|---:|
| Closed reasoning delimiter | 11 | 4 | 15 | 73.33% |
| No closing delimiter | 0 | 26 | 26 | 0% |
| All triggered tasks | 11 | 30 | 41 | 26.83% |

Completion is a post-generation variable, not a randomized assignment. Task difficulty can affect both completion and success. Therefore11/15 is an observed subgroup rate, not a causal effect or a replacement for11/41. Completed and incomplete groups are different tasks, not paired interventions on the same tasks.

The frozen extractor explicitly returns empty code when the closing delimiter is absent. All26 incomplete records therefore have code_parses=False by construction; this is not independent evidence that their internal reasoning contains no useful information. All15 completed records parse. One completed successful record uses exactly2048 output tokens; this alone does not locate its closing delimiter or prove that removing one token would erase the answer.

Completed token lengths:533,572,576,699,791,971,1289,1293,1496,1680,1700,1706,1838,1857,2048. All26 incomplete outputs have length2048. These are censored trajectories: their eventual completion times and correctness under a larger budget are unknown.

## Cost decomposition: retain every consumed token

| Group | Calls | Output tokens | Rescues |
|---|---:|---:|---:|
| Reasoning, completed | 15 | 19,049 | 11 |
| Reasoning, incomplete | 26 | 53,248 | 0 |
| Reasoning, total | 41 | 72,297 | 11 |
| Nonthinking, total | 41 | 2,316 | 0 |

19,049/11=1,732 is completed-subgroup token accounting.19,049/2,316=8.22 compares a post-selected15-call subset against all41 controls. Neither is deployable pipeline cost: completion is not known before generation and failures have already consumed compute.72,297/19,049=3.80 would require eliminating all failed-attempt costs while preserving every rescue; this is an unverified counterfactual, not a measured speedup or attainable bound. Larger caps may increase cost without completing or repairing those tasks.

Shared baseline costs remain720 candidate calls/29,701 output tokens and180 test calls/30,469 tokens. Wall-times and their desktop stalls remain as documented in v0.8; output-token matching is not equal FLOPs or latency.

## Small development ablations are underpowered and inconclusive

| Experiment | Paired triggered tasks | Observed full-cohort result | Interpretation |
|---|---:|---|---|
| Expanded routing | 6, only3 newly triggered | reasoning33/40 unchanged | No additional rescue observed; insufficient basis to reject routing generally |
| Cap2048 versus4096 | 3 | 33/40 versus33/40;1 incomplete each | Underpowered, inconclusive; does not establish equivalence or futility |
| Original versus concise prompt | 3 | 33/40 versus32/40 | One observed loss; underpowered, inconclusive about general effectiveness |

These remain useful observations and reproducibility checks. Forty tasks in the accuracy denominator do not supply forty treated pairs. No power calculation supports a general negative conclusion. The existing default stays unchanged pending evidence, while the larger-budget hypothesis remains open.

## Cohort amendment and direction

User-authorized configs/split-manifest-v2.json reassigns the previously unused60 calibration tasks to development. Original development was60 (pilot20 plus additional40), so total development is now120. The primary expanded cohort is additional40 plus reassigned60=100; legacy pilot20 stays separately identified. Confirmation180 and reserve78 are unchanged. The original manifest and confirmation source hashes remain untouched. Reassigned tasks are no longer eligible as independent calibration or validation data.

Next focus: completion-aware allocation of inference budget for code resampling. Compare2048/4096/8192 caps on the entire prespecified visible-trigger cohort, with completion rate as the primary mechanism outcome and all-task correctness, rescues/regressions and total cost retained. Trigger count is unknown until visible evaluation; do not assert adequate power from an expected count of8–10. See docs/research-direction-v2.md for budget controls, entropy screening and the boundary to faithfulness.

## Reproduction and nearest work

Run scripts/analyze_completion_audit.py to rebuild runs/completion-audit-20260913/summary.json from saved generations and task outcomes; no generated code is executed. The artifact includes per-task rows and source hashes. Original confirmation provenance and matrices remain in v0.8 and its cited immutable run artifacts.

[Olausson et al., ICLR2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/9ddc141bdbf9d1db510cefff56c586ad-Abstract-Conference.html) directly motivates cost-aware self-repair versus independent sampling. Its abstract reports modest, subset-dependent or absent gains after accounting for cost. [Official implementation](https://github.com/theoxo/self-repair) provides budget-analysis code. Full methodological reproduction remains pending; a Qwen/MBPP adaptation must be labeled as such.

# Next direction: completion-aware inference budgets

2026-09-13. Research design, not an executed experiment or frozen executable generator protocol. Cohort amendment is frozen separately in configs/split-manifest-v2.json. Do not start a new confirmation from the old180 outcomes.

## Immediate sequence

1. Generate the unchanged baseline on the60 newly reassigned tasks and run only visible evidence to establish public-failure triggers. Reuse the additional40 baseline. Preserve the legacy20 as a separate stratum. No hidden correctness may determine enrollment.
2. Freeze all resulting primary100 task IDs and public-failure trigger IDs, exact prompts, model/runtime and seeds before cap intervention. Use paired2048/4096/8192 caps, unchanged prompt/sampling and strict public replacement. Retain all triggered tasks, not only ones failing at2048. Do not silently reuse an old seed cohort as fresh independent evidence.
3. Primary mechanism outcome: fraction with a closing delimiter at each cap. Also report final parseability, all100 selected-answer accuracy, trigger-level rescue/regression, emitted tokens and task-paired uncertainty intervals. Delimiter completion does not ensure a complete/correct program. Multiple seeds must be summarized within task or task-clustered; they do not create new independent tasks. Report observed discordance and interval width; no unsupported claim of statistical power.
4. Add a nonthinking independent-sampling control at the same prespecified per-task output-token budgets2048/4096/8192. Each new sample uses at most min(768, remaining tokens); stop when budget exhausted, retain partial final samples and charge their tokens. Rank only by public assertions, deterministic earliest-index ties, and strict improvement over baseline. No hidden oracle selection. Report realized tokens, input tokens, calls and wall-time separately; equal output caps are not equal FLOPs. Distinguish this sequential budget-limited best-of-N from fixed-N pass@k.
5. Compare cap policies on the same tasks; freeze decisions before hidden scoring. Reproduce the nearest paper's actual budget estimator after reading its full method/code; label the new Qwen experiment an adaptation until that audit is done. Do not claim reproduction merely for implementing a similarly named baseline.

The number of public-failure triggers may remain small even on100 tasks. Report it before choosing further scope. If too sparse, a separately declared all-task development generation study can estimate completion behavior, but it answers a different question from conditional rescue. No outcome-driven task replenishment, optional stopping for significance, or spending reserve to tune policies.

## Entropy as a development-only routing diagnostic

Reuse mean_token_entropy of the baseline-selected original candidate. Audit missing values, sequence length and aggregation first. Evaluate public-failure OR high-entropy thresholds using task-level cross-validation on development only, with threshold fitting confined to training folds. Report error recall, false-trigger count/precision, coverage and expected extra calls at matched trigger rates, including public-only and random-routing controls. Existing60 tasks permit a zero-new-generation diagnostic; the newly reassigned60 need baseline generation first. Better screening does not establish additional correct answers: shortlisted policies still require actual generation and hidden scoring. No threshold fitting on the completed180 confirmation labels.

## Why faithfulness is not yet the headline

The completed15 and incomplete26 are distinct observational groups; they are not paired truncations of the same trajectory. The parser guarantees empty code for unfinished thinking, so zero rescue there cannot establish absence of causal reasoning value. A later causal study would pair retained-prefix, truncated-prefix and matched-length control interventions on each task, allow an identical separate answer budget, use multiple paired seeds, and evaluate resulting programs. Distinguish damage from malformed delimiters/context from semantic reasoning interventions. Execution establishes answer correctness, not by itself faithfulness of an explanation. Keep this as exploratory future work until such interventions exist.

## Scope and engineering

Prioritize a larger controlled evidence base over another serving framework, 27B training, multimodal features or a new repository. Reuse the existing generation/scoring pipeline with minimal new code. Once a useful budget policy is established, repository-level repair is an external-validity extension. The current function-level result remains the supported resume evidence.

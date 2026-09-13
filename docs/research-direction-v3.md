# When does extra reasoning supply useful content beyond additional computation?

2026-09-13. Current research roadmap, superseding direction-v2 priorities. This is a question and proposed intervention study, not a demonstrated faithfulness result or executable frozen protocol. Existing118/180 versus107/180 is motivating evidence with unequal compute. Preserve its factual result and historical provenance.

## Constraints and allocation

Independent evaluation opportunities are scarce. Protect reserve78: use only once for a final frozen claim, only after external-benchmark replication, and only if a prospective precision/power assessment supports its use. External success does not automatically authorize opening reserve. No cap tuning, routing threshold fitting, or mechanism exploration on it. External datasets are finite and also lose independence through adaptive reuse: distinguish external development from frozen evaluation, pin dated versions and task IDs, and keep a record of every label exposure.

Development remains120: legacy pilot20 plus primary100 (additional40 and reassigned calibration60). The old confirmation180 is already analyzed. Mechanistic exploration can use development, but generalizing a selected mechanism still requires independent tasks or a preregistered replication. Calling an estimand mechanistic does not remove selection bias or multiple-testing concerns.

Local hardware is an RTX5070Ti Laptop with12227MiB, not a24GB card. No paid GPU spending cap is approved. New8B BF16 inference cannot be assumed to fit locally; checkpoint, precision, context and memory benchmarks precede model selection. Quantization changes are explicit experimental factors, not silent substitutes. Do not infer model memory from the4B8.2GiB measurement.

## P0: external validity and the missing budget control

First complete the new60 baseline and visible triggers with the existing pipeline. Hidden scoring of frozen baseline decisions can then support descriptive cohort comparisons; visible pass rates alone cannot establish hidden accuracy or exchangeability. Compare prompt lengths, test counts, source/task characteristics, trigger rates and accuracy with uncertainty across legacy20, additional40, new60 and the historical confirmation. A performance gap does not itself invalidate a random split. Audit sampling and pipeline differences; never reshuffle after seeing labels to make cohorts look similar. Mark any outcome-informed redesign adaptive and use new independent external evaluation.

Add the direction-v2 budget-limited nonthinking independent-sampling control alongside reasoning. Preserve its deterministic visible-only selector, account for partial final samples, report input/output tokens, calls and wall-time, and distinguish output-token matching from equal FLOPs. Olausson2024 is a necessary methodological comparator; full estimator reproduction remains pending.

External benchmark axis: prioritize a pinned LiveCodeBench date window after a documented training cutoff of every compared checkpoint. If cutoff is unknown, use tasks published after the exact released checkpoint as a conservative temporal screen where available, disclose remaining limitations, and do not label it verified contamination-free. Date-filtering and benchmark branding do not establish absence of overlap. BigCodeBench-Hard is a second domain/evaluation axis, not automatically a post-cutoff or contamination-free set. Pin public/hidden test boundaries, versions, dependencies and task enrollment before scoring. No claim that MBPP is definitely in training without evidence.

Model axis: Qwen3-8B is a proposed scale comparison; a genuinely non-Qwen checkpoint such as an appropriate Llama checkpoint is a separate family comparison. Qwen2.5-Coder is still Qwen. Verify licenses, runtime feasibility and reasoning interface before freezing exact variants. A model without a thinking toggle cannot be treated as the same mode ablation; label prompt-induced reasoning and avoid attributing a size/family/precision bundle to one factor. First add one benchmark with the current model and one model on a shared benchmark; subsequently fill the crossed cells if feasible. Do not select only cells with favorable effects.

Report the signed paired effect and interval in each cell, cost curves and failures. Replication means a predeclared comparable contrast, not an expectation of exactly+6.11pp. Two cells alone do not prove universal generalization or novelty.

## P1: paired trace interventions, incorporating the cap study

Collect source trajectories on a prespecified development task/seed cohort without selecting by hidden success. Retain incomplete cases. Restrict complete-trace analyses explicitly to that stratum and report enrollment/attrition; never present that stratum as all tasks. Existing confirmation trajectories motivate the design but are not fresh replication data.

Every task has full-trace and no-trace anchor conditions, plus four intervention families:

| Family | Intervention | Main control/limit |
|---|---|---|
| Early answering | Retain0,25,50,75,100% of reasoning tokens | Same delimiter and separate answer budget; no trace includes the final answer |
| Error injection | Alter one verifiable visible fact or intermediate value | Predefined eligibility/edit rules; no hidden-answer hints; record intended and actual effect |
| Paraphrase | Meaning-preserving rewrite | Check semantic preservation independently; record token-length changes and edit failures |
| Filler | Replace trace content with tokenizer-length-matched filler | Context-length control; not automatically a serial-compute control |

Reset state/KV caches between conditions and use paired answer seeds, consistent templates, identical answer budgets, task-clustered intervals and prespecified contrasts. Synthetic injected errors must not be instructions to the operator. Run all resulting code only in restricted Linux containers. A test suite is an objective benchmark outcome, not a proof of complete semantic correctness or faithful explanation; prior multiple-choice tasks also have objective labels. No claim that code faithfulness is novel without a code-domain prior-art search.

Distinguish two filler interventions: (a) replay a filler prefix through prefill, which probes sensitivity to supplied textual content at matched context length; (b) force filler tokens through actual autoregressive decoding with equal step counts, which controls serial opportunities more closely. Pasting filler does not reproduce the cost or state history of generating a trace. Even(b) changes token distributions and may be out of distribution; a pretrained model may not know how to use filler. Pfau et al. demonstrate the possibility under task-specific training, not a guarantee for unmodified Qwen. Report prefill/decode costs separately and verify full-trace replay as a control.

Primary descriptive contrasts: accuracy(full)-accuracy(filler), accuracy(full)-accuracy(no trace), and paired changes under errors/paraphrases. The proposed ratio (acc(full)-acc(filler))/(acc(full)-acc(no trace)) is secondary, called a normalized intervention contrast, not a causal percentage of reasoning. Report numerator/denominator and task-bootstrap uncertainty; if the denominator is near zero or its interval spans zero, mark the ratio unstable/undefined. Do not clip it to[0,1]; interactions can produce values outside that range.

Cap and truncation share a task cohort and plots, not an estimand. Store generated token IDs and first closing-delimiter position, final-answer boundary, EOS and cap status prospectively. Longer unmodified trajectories permit censoring/completion summaries at2048/4096/8192 if prefix consistency holds; intervened early answers still require new generation with a separate answer budget. One long generation does not supply every intervention outcome for free. Historical output_tokens includes answer tokens and is not the closing-token time; do not use it directly as a reasoning-completion event time.

Kaplan-Meier can summarize observed time-to-delimiter with administrative right censoring after event-time validation. It cannot nonparametrically extrapolate beyond the observed2048 cap or determine how many of the26 censored traces would finish at4096/8192. Obtain longer traces to identify that tail; any parametric extrapolation must be separately labeled assumption-dependent. Show at-risk counts, uncertainty and correctness alongside completion curves.

## P2: entropy diagnostic, no separate confirmation

Use existing baseline-selected mean_token_entropy, audit missingness/length effects, fit thresholds only inside task-level training folds, and compare out-of-fold public-only, entropy-extended and random routing at matched trigger rates. Report error recall, false positives and projected calls. Existing development permits zero-new-generation analysis; adding the new60 first requires baseline generation. Better detection is not demonstrated rescue. Keep as one report section; do not open reserve for it.

## Milestones: a90-day planning horizon, not mandatory waiting periods

| Weeks | Work | Reviewable output |
|---|---|---|
| 1–2 | New60 baseline, cohort audit, budget-matched control | Actual trigger count, paired accuracy/cost table and uncertainty |
| 3–5 | Dated external benchmark and second feasible model | Frozen-cell replication results, including absent/reversed effects |
| 6–9 | Paired interventions with shared cap cohort | Completion curves, intervention contrasts, v1.0 only after evidence |
| 10–11 | Entropy section, literature synthesis | Reviewer-facing limitations and mechanism interpretation |
| 12 | Consolidation | Research writeup and two-page research statement |

Advance sooner when evidence and resources permit; do not claim a deadline guarantees significance or novelty. Read foundational papers now, before implementing their interventions. Each batch has bounded tasks/calls, a stop condition for operational failures, and a stated decision it informs. No new serving framework,27B,multimodal work,repository-level repair or new repository in this phase.

## Sources and reading status

- [Lanham et al.2023](https://arxiv.org/abs/2307.13702): early-answering and perturbation motivation.
- [Turpin et al.2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/ed3fea9033a80fea1376299fa7863f4a-Abstract.html): explanations can omit influential biasing factors.
- [Pfau, Merrill, Bowman2024](https://arxiv.org/abs/2404.15758): filler-based computation in controlled algorithmic tasks; training dependence matters.
- [LiveCodeBench](https://livecodebench.github.io/): date-annotated tasks support temporal evaluation windows.
- [BigCodeBench official repository](https://github.com/bigcode-project/bigcodebench): separate library-oriented benchmark and Hard subset.

Official abstracts/project descriptions checked2026-09-13; detailed methods, evaluator integration, checkpoint cutoffs and code-domain novelty review remain pending. No claim of completed reproduction.

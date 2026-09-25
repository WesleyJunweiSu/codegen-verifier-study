# Research agent operating program

Updated 2026-09-24. Read this with [AGENTS.md](AGENTS.md). This is a repository-specific Markdown operating guide, adapted from [Karpathy autoresearch](https://github.com/karpathy/autoresearch) and the research-agent sources in [autoresearch-methods.md](docs/autoresearch-methods.md). It is not a new agent framework, an installed global skill, or evidence that our research is fully autonomous. User instructions and frozen experimental protocols govern execution.

## Objective and scarce resources

Answer: **when does additional serial reasoning contribute useful information beyond additional computation?** Optimize credible information gained per experiment and the usefulness of the final engineering/research artifact. Higher development accuracy is useful evidence; it is not the sole objective and cannot justify changing the evaluator or searching held-out labels.

Independent evaluation opportunities, researcher attention and available GPU memory are limited. Prefer a discriminating control or external replication over another report version or infrastructure layer. A small inconclusive experiment is not a general negative result. Do not promise a positive result, novelty, a conference acceptance, or production deployment.

## Resume before proposing work

1. Read `PROGRESS.md` (latest entries), `docs/research-direction-v3.md`, `docs/claim-ledger.md`, the latest report and relevant run manifests/journals. `docs/pilot-protocol.md` is historical; its dated status is not the current queue.
2. Check Git status, actual local generator processes and GitHub Actions. A stale journal marked running does not prove a live process; verify before restarting. Resume missing exact keys and reuse verified artifacts. Never duplicate a live run or silently overwrite completed evidence.
3. Identify the next unresolved scientific decision and what can proceed with existing authorization. Persist the next command, dependencies and resume keys when stopping. Continue authorized work without calendar waiting or repeated permission requests.

## Choose one informative experiment

Write a short experiment card in the run directory before new generation. Reuse an existing config/manifest rather than create a second registry. The card must cover:

```text
Run ID / parent run / source commit:
Question, hypothesis and strongest alternative explanation:
Decision changed by a positive, null or ambiguous outcome:
Estimand, primary metric and paired control:
Dataset revision, IDs, exposure status and independent task count:
Arms, seeds, stopping rule and allowed implementation edits:
Shared baselines and exact cache keys:
Per-call and total token/call limits, wall-time limit, VRAM and spending cap:
Required fixtures, visible-stage artifacts and decision-freeze boundary:
Uncertainty method; failures and missing outputs in the denominator:
Result / limitations / next decision: [fill only after the planned batch]
```

Compare a few candidate hypotheses using existing evidence, then choose one with a useful control and feasible cost. Link it to a parent run; do not build a new search orchestrator. State one changed factor, or explicitly describe a joint treatment without attributing its effect to one component. An operational repair such as a CLI allowlist fix is a separate change, not a scientific improvement.

Before expanding, ask whether more tasks, another model or a stronger control could change the conclusion more than another hyperparameter value. Record why the selected experiment wins this comparison. Avoid re-running a known saturated control without a new diagnostic question.

## Bounded experiment loop

1. **Freeze.** Pin task IDs, model/tokenizer/runtime versions, prompts, sampling, selector, seeds, metrics and explicit resource ceilings. Preserve the existing evaluator and hash-bound confirmation sources. New conditions use separate unbound scripts/configs with explicit allowed edit paths. Never lower quality checks to obtain a better score.
2. **Check cheaply.** Verify relevant contracts and synthetic fixtures before spending generation budget. Use existing fingerprinted baselines when compatible. Evaluate task programs only in restricted Linux Docker; host-side JSON analysis and model generation must not execute generated code.
3. **Run the planned batch.** Prefer the Windows local GPU, retain BF16 and the 9216 MiB free-memory guard. Do not kill user apps. No paid API/GPU without an approved spending ceiling. Checkpoint outputs and consumed budget by exact task/arm/seed keys. A timeout/crash still incurs cost; preserve it and retry only under a documented policy.
4. **Select using visible evidence.** No hidden labels, reference solutions or private-test contents in prompts, routing, candidate selection or early stopping. Complete the planned arms and freeze decision artifacts before hidden scoring. Metadata access approval is not hidden-scoring approval.
5. **Analyze.** Report full-cohort accuracy and paired wins/losses, treated-task count, completion and parser failures, plus uncertainty. Keep all consumed input/output tokens, calls, wall time and peak memory; separate shared costs. Equal caps are not equal realized compute. A completion subgroup is not a causal treatment or free removal of failed costs.
6. **Review against evidence.** Take a separate critique pass: challenge the alternative explanation, leakage, denominators, cost accounting, statistical power and claims. This can be the same agent changing review role; it is not independent peer review and does not require spawning more agents. Check tables against saved per-task data. Do not optimize an LLM review score as a substitute for evidence.
7. **Record and continue.** Save config, source hashes, all arms, task outputs, errors and interpretation. Update `PROGRESS.md` and `docs/claim-ledger.md` only where claims changed. Run relevant checks; commit and push completed batches to the existing private repository. Choose the next bounded experiment from what was learned, not from pressure to report gains.

The default unit is one frozen batch followed by analysis, not an unlimited loop. A new batch may start immediately when its dependencies, protocol and resource ceilings are settled within user authorization. A resource or approval blocker stops only the dependent action; proceed with useful independent work. Do not route around a rejected action. Keep ordinary user updates concise; heartbeat notifications are only for new conclusions, completed batches, failures or needed user action.

## Decision vocabulary and evidence preservation

| Status | Meaning and next action |
|---|---|
| Development candidate | A prespecified metric/control contrast is promising enough to replicate; not confirmed superiority |
| Observed regression / no observed gain | State the measured contrast and uncertainty; decide whether it narrows a useful hypothesis |
| Inconclusive | Too few independent tasks, wide uncertainty, confounding or failed measurement; do not claim disproof |
| Invalid measurement | Broken evaluator or protocol deviation; retain evidence, repair separately and explain which comparisons cannot be used |
| Execution failure / resource deferred | Scientific result is unavailable; record partial cost, failure cause and exact resume step |
| Independently replicated | A previously frozen claim was evaluated on eligible unexposed evidence; report scope and precision |

Keep unsuccessful branches and artifacts in Git/history with parent IDs. Do not use destructive reset or deletion to erase failed experiments. Selecting a development candidate need not mean that its code is permanently adopted; implementation and scientific claims have separate acceptance decisions. Never repeat significance testing until a desired threshold appears.

## Dataset and claim boundaries

- MBPP primary development100 is already exposed; legacy20 is also development. Confirmation180 is completed evidence, not a tuning set or a fresh test. Preserve the original manifests.
- Reserve78 stays sealed under `configs/reserve-policy.json`: only one final frozen claim after external replication and a prospective precision/power assessment. This guide grants no release.
- External datasets are finite evaluation opportunities too. Separate development and final IDs using metadata before outcomes. Do not select dates, difficulty or platforms based on model success. A post-checkpoint publication window is not proof of a training cutoff or absence of contamination.
- Trace completion depends on task difficulty; the unfinished-trace parser also affects observed failure. Paired interventions are required for stronger mechanism claims. Filler prefill does not match sequential decoding, and survival analysis cannot recover an unobserved tail beyond a shared censoring cap.
- Preserve current limitations in applications and blogs. The original +6.11 pp is single-model, single-benchmark, unequal-compute evidence. The later +5 pp is adaptive development evidence. Workflow automation does not upgrade either claim.

## Current continuation priorities

1. The user-authorized LiveCodeBench census is complete:1055 tasks, latest date2025-04-06, **zero** eligible under the prospective2025-05-20 start. See `runs/external-metadata-20260924/summary.json`; authorization and historical failures are retained. Locate a newer official snapshot using source metadata, or explicitly propose another external benchmark with its limitations. Do not widen the date window to rescue this empty cohort or start generation on it. Keep private-test payloads opaque during any authorized metadata projection.
2. Freeze metadata-based external enrollment and expected precision; validate public-only STDIN/function adapters with synthetic fixtures. Preserve a final evaluation boundary. Then replicate the existing reasoning versus independent-sampling contrast with explicit cost accounting. Change benchmark first with the existing model; change model as a separately identified axis.
3. On exposed development only, investigate the low-diversity nonthinking control with a prospective diagnostic and then paired full/no-trace, truncation, error, paraphrase and filler interventions. Freeze executable arms and resource ceilings first. Do not promote a standalone cap sweep to the headline.
4. P2 entropy analysis is already complete. Extend it only if a clear new control or end-to-end answer experiment changes a decision; detection recall alone is not an accuracy improvement.

Follow result-dependent next steps recorded in `PROGRESS.md`; this priority list does not assert that a future batch is already running. No new serving stack, 27B model, multimodal task, repository-repair benchmark or separate repository in this phase.

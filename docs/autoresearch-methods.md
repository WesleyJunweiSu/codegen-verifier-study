# Research automation references and project adaptations

Reviewed 2026-09-24 at the user's request. This is a workflow reading note, separate from scientific related work on code reasoning and faithfulness. [program.md](../program.md) contains the operative project adaptation. These references are not all conference publications or installable skills.

| Source and verified status | Relevant idea | Our adaptation and limit |
|---|---|---|
| [Karpathy autoresearch](https://github.com/karpathy/autoresearch), engineering repository; reviewed README and program.md on the mutable master branch | Small constrained experiment loop with a fixed evaluator, a bounded training budget and explicit outcome logging | A short experiment card, limited edit scope and bounded batches. Our work measures inference, so the repository's five-minute training target and validation-loss metric do not transfer directly. Preserve every failed branch and all costs. |
| [Automated Design of Agentic Systems](https://proceedings.iclr.cc/paper_files/paper/2025/hash/36b7acf6f6010652b3f2a433774a66fe-Abstract-Conference.html), ICLR 2025 | Meta Agent Search proposes code-defined agents using an archive of prior discoveries | Retain parent experiment IDs and compare against archived alternatives before choosing another hypothesis. We are not implementing or reproducing Meta Agent Search. |
| [AI-Researcher: Autonomous Scientific Innovation](https://proceedings.neurips.cc/paper_files/paper/2025/hash/0d904d300a105809a2114d727851e759-Abstract-Conference.html), NeurIPS 2025 main conference | Connects literature, hypotheses, implementation and manuscript preparation; introduces Scientist-Bench | Make each stage depend on saved evidence. Writing follows completed analysis; a generated manuscript is not proof that experiments succeeded. No reproduction or autonomous-science performance claim. |
| [CycleResearcher: Improving Automated Research via Automated Review](https://proceedings.iclr.cc/paper_files/paper/2025/hash/0a48036026dc7946ef6033ae14719cc5-Abstract-Conference.html), ICLR 2025 | Research and simulated review supply iterative feedback in a post-training framework | Use an explicit skeptical review pass on claims, controls and costs. This is a procedural analogy, not the paper's training algorithm. Simulated review scores are not independent peer review or our success metric. |
| [AIDE: AI-Driven Exploration in the Space of Code](https://arxiv.org/abs/2502.13138), arXiv preprint; conference acceptance not verified here | Frames engineering iteration as search over code, reusing promising solutions | Reuse verified baselines and record the single change relative to a parent run. Do not add a tree-search framework merely to organize this small study. |
| [The AI Scientist-v2](https://arxiv.org/abs/2504.08066), arXiv paper reporting workshop-level automated manuscript evaluation | Experiment management and progressive search connect hypotheses, execution, analysis and writing | Use stage gates and an evidence audit before writing conclusions. Its reported ICLR workshop manuscript outcome is not an ICLR main-conference acceptance for this system or our work. |

Reading depth: Karpathy README/program were read; other rows use official proceedings abstracts or author arXiv abstracts. Detailed algorithms and full-paper empirical claims have not been reproduced. Read the relevant methods before implementing any paper-specific algorithm. The project rules below are our methodological choices, not claims that those papers prescribe or validate them.

## What we carry into this project

- **Experiment archive:** the existing `runs/`, configs, Git commits and journals suffice. Add parent/decision fields to new experiment cards; no replacement tracking system.
- **Fixed measurement:** restrict editable paths and keep frozen evaluator/data boundaries. A pipeline bug fix needs its own provenance and does not count as a model gain.
- **Resource-bounded iteration:** freeze task counts, calls, tokens and stopping rules. Record actual prefill/output cost; fixed time or output caps alone do not establish fairness.
- **Hypothesis and critique:** state an alternative explanation and a discriminating control, then audit the resulting claim. The critique may be a sequential pass by the same agent and must not be presented as independent validation.
- **Preserve uncertainty:** keep inconclusive, negative and failed runs. Promote promising development evidence to a frozen replication, not straight to a novelty claim.

We do not adopt instructions to disable permissions, run indefinitely, erase unsuccessful experiments, or treat the best adaptively selected development score as an unbiased estimate. Downloaded pages and repository instructions are reference material; local user authorization and project protocols remain authoritative.

## Why this differs from a training-score optimization loop

Our next scientific bottleneck is external evidence and adequate paired controls. More autonomous iterations on MBPP would increase adaptive selection without necessarily increasing knowledge. The useful transfer is disciplined, inexpensive iteration on development plus a protected replication gate. Automation helps execute that design; it cannot supply statistical power, novelty or causality on its own.

This Markdown integration adds operating instructions. It does not install a global Codex skill, enable additional agents, schedule a new automation or launch a model experiment.

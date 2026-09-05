# Related work and novelty boundaries

Retrieved on 2026-09-05. These notes summarize official abstracts, records, and selected source material; they are not a completed full-text systematic review.

| Work | Status | Relation to this project |
|---|---|---|
| [S*: Test Time Scaling for Code Generation](https://aclanthology.org/2025.findings-emnlp.865/) | EMNLP 2025 Findings | Direct nearest neighbor: hybrid scaling and distinguishing inputs for execution-grounded selection. A simplified implementation must not be described as a faithful full reproduction. |
| [HARDTESTGEN](https://iclr.cc/virtual/2026/poster/10006843) | ICLR 2026 main-conference poster | High-quality synthetic tests/verifiers; motivates measuring verifier validity rather than assuming tests are correct. |
| [Dynamic-Static Synergistic Selection Method for Candidate Code Solutions with Generated Test Cases](https://ojs.aaai.org/index.php/AAAI/article/view/40481) | AAAI 2026 Technical Track | Direct nearest neighbor: static and dynamic analysis to handle defective generated tests. Filtering tests and combining execution with static signals is established work. |
| [CodeHacker](https://aclanthology.org/2026.acl-long.108/) | ACL 2026 main conference | Test generation targeting defects in competitive-programming solutions; useful counterexample-oriented comparison. |
| [AlgoVeri](https://arxiv.org/abs/2602.09464) | Listed in [ICML 2026 official downloads](https://icml.cc/Downloads/2026); single-paper official page not loaded in this pass | Formal verification of algorithms in Dafny, Verus and Lean. Executable Python tests do not provide equivalent guarantees. |
| [DSCodeBench](https://ojs.aaai.org/index.php/AAAI/article/view/40540) | AAAI 2026 Technical Track | Potential data-science transfer setting after the function-level pipeline works. |
| [Themis](https://ojs.aaai.org/index.php/AAAI/article/view/40741) | AAAI 2026 Technical Track | Constraint-aware test synthesis and test-quality effects on code RL. Do not claim constraint filtering as a new idea. |
| [EvalPlus](https://github.com/evalplus/evalplus) | Official evaluation implementation; foundational tooling rather than a 2026 novelty claim | Independent hidden-test scoring and reproduction of historical results. Pin exact code/data versions during implementation. |
| [Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) | Official model card | Start from the same model family and explicit non-thinking mode as the existing blog. |

The plausible contribution is a carefully controlled study of selection and abstention under unreliable tests in a constrained local-compute setting, with a usable tool and transparent negative results. Small GPU size alone is not scientific novelty. Before a paper submission, read the full nearest-neighbor methods, inspect their code, and test whether the planned abstention/calibration setting is already covered.

Other directions examined during selection:

- [FaithCoT-Bench, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/6c7154e394e24c69409256ccf8bf0804-Abstract-Conference.html): instance-level CoT unfaithfulness detection.
- [CoT intervention robustness, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/a03037317560b8c5f2fb4b6466d4c439-Abstract-Conference.html): recovery from reasoning-trace interventions. Answer invariance cannot alone diagnose unfaithfulness.
- [When Good OCR Is Not Enough, ACL 2026 Industry](https://aclanthology.org/2026.acl-industry.60/): document parsing errors and downstream RAG failures, relevant to a later Obsidian extension.
- [Long-document factuality metric stress tests, ACL 2026](https://aclanthology.org/2026.acl-long.1472/): evaluation metrics themselves need auditing.
- [FaithJudge, EMNLP 2025 Industry](https://aclanthology.org/2025.emnlp-industry.54/): supplementary context-faithfulness evaluation, not a correctness oracle.
- [Frozen-PINN, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/ab435f7130455143fd9489f389777552-Abstract-Conference.html): optimization/solver architecture matters alongside derivative backends.

Contextual faithfulness, causal faithfulness of reasoning traces, test-supported correctness, and formal verification are different claims and should remain separate in both reports and resumes.

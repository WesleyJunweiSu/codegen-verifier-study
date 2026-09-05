# When Should a Code Selector Abstain?
## A development study of imperfect generated tests on a local 4B model

Wesley Junwei Su · Working technical report v0.1 · 2026-09-05

**Status:** exploratory pilot and evaluator audit, not a peer-reviewed paper or a demonstrated new method.

### Abstract

Test-guided code selection assumes that generated checks provide useful evidence about candidate correctness. We examine this assumption using Qwen3-4B on 20 development tasks from MBPP+, with four frozen candidates per task. First-candidate selection returns 10 correct programs; public-example selection returns 11; generated-test and syntactically filtered selection each return 10. The candidate oracle is 12/20. Of 120 strictly parsed generated assertions, 25 reject the benchmark reference implementation. An AST normalization ablation recovers 40 assertions from five malformed test responses but does not improve generated-test selection. A fixed abstention rule returns no programs, demonstrating an unusable operating point rather than successful error avoidance. Separately, a Linux audit changes seven historical Windows labels for unchanged code. These observations motivate separating evaluator reliability, candidate diversity, test semantics and abstention calibration before claiming useful inference-time scaling.

### 1. Motivation and related work

The previous project, [Agreement is not confidence](https://github.com/WesleyJunweiSu/WesleyJunweiSu.github.io/blob/main/app/page.tsx), investigated code-generation uncertainty and a gap between candidate availability and useful selection. This study asks whether additional generated tests close that gap, and whether their unreliability can be detected using deployable information.

Test-guided selection is established prior work. [S*](https://aclanthology.org/2025.findings-emnlp.865/) combines test-time scaling with execution-grounded selection. [Dynamic-Static Synergistic Selection](https://ojs.aaai.org/index.php/AAAI/article/view/40481) directly addresses generated-test defects. [HARDTESTGEN](https://iclr.cc/virtual/2026/poster/10006843) motivates stronger test/verifier construction. Our pass-count baselines are not faithful reproductions of those full systems. The current contribution is an auditable failure analysis under limited local compute; novelty remains to be established.

We distinguish four questions: does the evaluator measure the program correctly; does the pool contain a correct alternative; do deployable tests distinguish that alternative; and can a selector abstain at useful coverage?

### 2. Experimental setup

**Data.** MBPP+ v0.2.0 contains 378 tasks. SHA256 ordering with seed 20260905 freezes 60 development, 60 calibration, 180 confirmation and 78 reserve tasks. The pilot uses the first 20 development IDs. The prior project's checkpoint recorded that MBPP+ had not been evaluated. No calibration or confirmation scores have been used. Public benchmark training contamination remains possible.

**Generation.** Qwen3-4B runs locally in BF16 and non-thinking mode, temperature 0.7, top-p 0.8, 768-token cap, using the inherited generation implementation. Each task receives four seeded sampling calls. Test generation sees only the public specification and requests eight independent assertions; it never sees candidate code or hidden solutions. Unspecified generation defaults are inherited from the fingerprinted checkpoint and recorded package versions. This is one seeded configuration, not a multi-seed study.

**Information boundary.** Generator-visible JSONL contains only task ID, prompt and entry point. The Linux executor constructs the candidate/test matrix and writes decisions before loading references and hidden inputs. Reference execution of generated tests is an after-the-fact diagnostic; it is never supplied to selection.

**Execution.** A GitHub-hosted Ubuntu runner executes a non-root Docker container with no network, read-only filesystem, restricted capabilities, bounded memory/processes and a disposable temporary directory. The evaluator uses `evalplus==0.3.1` primitives with custom serial orchestration, not the upstream CLI. Base and plus suites must both pass. The pilot validates correct, wrong, malformed, exception and looping fixtures. The loop fixture is reported as `fail` by upstream's internal time-limit handling. The historical audit used the first three fixtures. Dataset/candidate hashes and source commits accompany artifacts.

**Baselines.** First candidate; uniform-random expectation; maximum public-test passes; maximum generated-test passes; filtered generated-test passes. Ties select the smallest sample index. Filters check duplicates, missing target calls, obvious tautologies, self-oracles and contradiction with literal public examples. They do not validate arbitrary expected outputs. The fixed development abstention rule requires at least one kept assertion, all kept assertions passing, and a margin of one over a distinct-code alternative. It is not calibrated.

**Adaptive ablation.** After inspecting initial failures, a second run transforms only top-level AST comparisons into assertions, preserves expected values, and reuses the exact candidates and raw test responses. It adds a public-first lexicographic selector: public-test pass count, then filtered generated-test pass count. This is a development adaptation, not independent confirmation.

### 3. Results

| Selector | Strict parser: correct / 20 | Normalized parser: correct / 20 | Returned / 20 |
|---|---:|---:|---:|
| First candidate | 10 | 10 | 20 |
| Uniform random, exact expectation | 10.75 | 10.75 | 20 |
| Public examples | 11 | 11 | 20 |
| Generated tests | 10 | 10 | 20 |
| Filtered generated tests | 10 | 10 | 20 |
| Public-first, then filtered tests | Not run | 11 | 20 |
| Fixed filtered abstention | 0 | 0 | 0 |
| Candidate oracle, non-deployable | 12 | 12 | — |

First-candidate accuracy is 50%, task-level Wilson 95% interval 29.9–70.1%. Public-example accuracy is 55%, interval 34.2–74.2%. Its gain is one rescued task and zero regressions; the paired task-bootstrap interval is 0–15 percentage points. This small inspected development result does not establish a general improvement. Identical task outcomes produce a degenerate empirical bootstrap interval, not evidence of statistical equivalence.

**Candidate availability.** Thirteen tasks have four text-identical candidates. Only two contain a mix of passing and failing candidates, so the pool offers only two possible rescues over the first candidate. Text identity is not a claim of behavioral equivalence between nonidentical programs.

**Test quality.** The strict parser retains 120 assertions across 15 tasks; none trigger the initial filters. Twenty-five reject the reference. The other five responses contain comparisons without `assert`. Normalization produces 160 assertions across 20 tasks; two duplicates are filtered, leaving 158. Thirty-four of 160 reject the reference, all surviving filtering. Assertions within a task are correlated; 160 assertions are not 160 independent observations of general test reliability.

**Parsing versus reasoning.** Assertion repair fixes test availability but leaves selection at 10/20. Missing `assert` is therefore not a sufficient explanation for this pilot's selection failure. This does not show that parsing never matters.

**Abstention.** Coverage is zero. Selective accuracy is undefined, not 100%. The rule is unusable in this configuration. Its thresholds have not been optimized using confirmation data.

![Pilot counts and reference diagnostics](figures/pilot-results.png)

### 4. Concrete failure cases

**Mbpp/564: a rescue supported by public evidence.** The first candidate fails hidden evaluation; sample 3 passes. Generated tests initially omit `assert`. The public example selects sample 3, while strict and normalized generated-test ranking select a failing candidate. The CLI displays the saved decision and selected program without executing it.

**Mbpp/607: more tests do not resolve the choice.** Two candidates pass hidden evaluation, but first, public-test and generated-test selectors choose failing sample 0. The suite includes `find_literals('no match here', 'match') == ('match', 0, 0)`, which rejects the reference. This is a case for specification-level audit, not proof that every reference disagreement means an incorrect expected value.

**Mbpp/615: syntax is insufficient.** All eight generated assertions reject the reference while passing the static filters. One is `average_tuple(((10, 10, 10, 12),)) == [30.5]`. Valid Python cannot establish that an expected output follows from the specification.

### 5. Historical evaluator audit

The 134 saved samples comprise 34 calibration and 100 historical test tasks. Linux scoring agrees on all calibration labels and changes seven test labels from failure to pass. Calibration remains 22/34. Historical test scoring changes from 75/100 to 82/100, and historically accepted candidates from 56/71 to 62/71. Acceptance decisions are reused without retuning the entropy threshold.

| Tasks | Old status | Linux status | Source-level evidence |
|---|---|---|---|
| HumanEval/15, /96, /100, /123 | timeout | pass | Old worker queues full output representations; parent joins before draining. Queue backpressure is plausible, not yet a causal reproduction. |
| HumanEval/139 | fail | pass | Old worker applies `repr` to outputs; large integers can hit Python's conversion limit. Controlled reproduction pending. |
| HumanEval/160 | unsafe | pass | Candidate uses `eval`, explicitly blocked by the old gate. |
| HumanEval/162 | unsafe | pass | Candidate imports `hashlib`, absent from the old allowlist. |

These are protocol/runtime differences, not new model capability. The old script scored the plus suite; this audit requires both base and plus. Source inspection explains the static gate differences; other causes remain hypotheses. Historical data are exposed and cannot serve as independent confirmation.

### 6. Cost, reproducibility and limitations

Candidate generation uses 3,540 output tokens and 175.93 generation seconds; test generation uses 3,546 tokens and 176.57 seconds. Combined generation is 352.50 seconds; peak allocated VRAM is 8,676,990,976 bytes (8.08 GiB). Timings exclude loading, entropy postprocessing, setup, image construction and queue delays. The strict pilot executes 560 candidate/test pairs including public examples; normalization executes 720. Hidden scoring and reference diagnostics are additional work. The ablation adds zero model tokens; copied costs describe the inherited pool, not new calls.

Artifacts include raw outputs, seeds, prompt hashes, model/tokenizer fingerprints, per-test outcomes, decisions, labels and workflow commits. The Dockerfile pins key dependencies, but its base-image tag and transitive dependencies are not content-locked. Full checkpoint checksums were recorded after the pilot from unchanged local files.

The pilot is too small and adaptively inspected for a headline effectiveness claim. One model, one sampling configuration and short functions do not establish performance on repositories, DS workflows or production code. Full S* reproduction, execution-consensus, calibrated risk guarantees and matched end-to-end compute comparisons are unfinished.

### 7. Next experiment

Address candidate diversity and discriminating-test quality separately. Compare existing sampling with one recorded diversity intervention on development tasks, holding selectors fixed and measuring oracle gap and token/time cost. Audit reference-rejecting tests into wrong expectations, invalid inputs and ambiguous specifications before designing richer deployable signals. Freeze generation, selection and calibration procedures before using the 180 confirmation tasks.

Evidence: [strict pilot](../runs/mbpp-pilot-20260905/summary.json), [parser ablation](../runs/mbpp-parser-ablation-20260905/summary.json), [historical comparison](../runs/historical-holdout/comparison.json), [experiment log](experiment-log.md).

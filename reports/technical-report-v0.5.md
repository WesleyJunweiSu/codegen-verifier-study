# Public failures can route extra reasoning, but feedback is not yet the winner

2026-09-08. Development report v0.5. Qwen3-4B BF16 on one RTX 5070 Ti Laptop; MBPP+ v0.2.0; the same 20 exposed development tasks used in v0.1–v0.4. This is a new generation intervention, not independent confirmation.

## Question and intervention

The original public-first execution-consensus selector returned 12 correct programs out of 20, matching the four-candidate pool's oracle. Selecting differently cannot recover a task with no correct candidate. Six selected programs also failed a public example, providing an observable trigger for generating another answer without consulting hidden labels.

For each triggered task, generate one feedback-based repair and one independent resample. Both receive the task specification. Repair additionally receives the selected program and the public assertions it failed. Replace the selected program only when the new answer passes strictly more public assertions; otherwise retain the original. Nontriggered tasks remain unchanged. Both arms retain all 20 tasks, including unsuccessful repairs, in the denominator.

We first used the original non-thinking settings: temperature 0.7, top-p 0.8, top-k 20 and a 768-token cap. After observing persistent public-example errors in the generated repair text, we froze a second paired condition using Qwen's [documented thinking preset](https://huggingface.co/Qwen/Qwen3-4B): temperature 0.6, top-p 0.95, top-k 20, and a 2,048-token total generation cap. This changes multiple factors, so it is not a pure causal test of thinking alone. A reasoning response without its closing reasoning token becomes an empty failed answer; it does not receive an automatic retry or larger budget.

## Results

All correctness counts require both EvalPlus base and additional tests to pass. Coverage is 100%, because failed attempts fall back to the baseline answer.

| Pipeline | Correct / 20 | Rescues / regressions vs baseline | Extra calls | Extra output tokens | Extra generation seconds |
|---|---:|---:|---:|---:|---:|
| Original selected answer | 12 | 0 / 0 | 0 | 0 | 0 |
| Non-thinking resample | 12 | 0 / 0 | 6 | 230 | 10.26 |
| Non-thinking feedback repair | 13 | 1 / 0 | 6 | 231 | 11.08 |
| Reasoning feedback repair | 16 | 4 / 0 | 6 | 7,694 | 760.59 |
| Reasoning resample | 17 | 5 / 0 | 6 | 9,378 | 484.25 |

These are **incremental** costs. Every pipeline inherits the original candidate generation, test generation and selection costs reported in v0.3. Non-thinking repair/control prefill totals were 1,745/793 tokens; reasoning repair/control totals were 1,721/769. Equal calls and caps do not mean equal realized compute. The two reasoning arms together generated 17,072 tokens in 1,244.84 seconds. Runtime ordering and desktop GPU conditions were not controlled; do not infer a stable latency ranking from these sequential runs. The reasoning backend omits vocabulary-logit retention and entropy computation; entropy is explicitly null, not zero.

Non-thinking repair recovers Mbpp/722. It also replaces Mbpp/734 with code that passes the public example but still fails hidden tests: public-example success remains an imperfect signal. The new reasoning candidates make more correct answers available. However, the resampling control beats the feedback repair arm by one task. The current evidence supports further testing of **conditional extra reasoning**, not a claim that feedback repair is superior.

Three reasoning attempts hit the 2,048-token cap without completing the reasoning block: two feedback repairs and one resample. They remain failures and retain the baseline output. No failed task was removed. All reused baseline programs received exactly the same labels on reevaluation.

The paired task-bootstrap interval for reasoning repair versus the original selector is +5 to +40 percentage points; versus reasoning resampling it is −15 to 0 points. These intervals describe this small development sample and are **not adjusted for repeated development choices**. Neither general superiority nor statistical confirmation is established.

## Execution boundary and provenance

Generation reads public specifications, saved public outcomes and original candidate code. No reference solutions, hidden tests, hidden-domain annotations or hidden-label failure triggers are supplied to the model. The Linux scorer writes the public matrix and final repair/control decisions before loading benchmark references. Candidate execution uses the established disposable Docker restrictions; the ordinary Windows host only generates and analyzes text.

- Non-thinking trigger/prompt freeze: `1f1811d`; inputs committed at `4d5e8f9`; [scoring run 34165966111](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34165966111), 5.91 seconds inside the executor.
- Reasoning configuration freeze: `c9925f3`; inputs committed at `ce68578`; [scoring run 34304923901](https://github.com/WesleyJunweiSu/codegen-verifier-study/actions/runs/34304923901), 6.60 executor seconds.
- Data: `runs/mbpp-repair-20260907/` and `runs/mbpp-reasoning-repair-20260907/`. Plans, model/source fingerprints, prompts, raw responses, candidate IDs, costs, matrices, saved decisions and per-task labels are retained.

Reproduce statistics without executing generated code:

```bash
python scripts/analyze_repair.py
python scripts/analyze_repair.py --run mbpp-reasoning-repair-20260907
python scripts/verify_artifacts.py
```

## Next decision

The remaining 40 development tasks have entered generation under their original frozen protocol. Before reading their scoring outcomes, `configs/development-repair-transfer.json` records all four extra-generation arms and the same public-only trigger and fallback. The primary development comparison is conditional reasoning resampling versus non-thinking resampling, with actual cost reported. We will retain both feedback arms even if they lose.

The 180 confirmation tasks remain untouched. They can be evaluated after the final procedure and analysis are frozen; no two-week delay is required. A threshold-free method need not wait for the separate abstention-calibration project. See `docs/confirmation-readiness.md`. This remains a research prototype with development evidence, not a conference-ready novelty claim or a deployed service.

> 2026-09-12 completion update: all 180 tasks have been generated, selected and scored under the frozen protocol. Reasoning 118/180 vs selected/nonthinking 107/180. See [report v0.8](../reports/technical-report-v0.8.md). Read the readiness discussion below as historical planning, not current pending status.

# When the 180-task confirmation split can be used

Updated 2026-09-11 (America/New_York). The development check is complete and the final protocol is frozen at `7ef1103` in `configs/confirmation-protocol.json`. The coordinator and primary analysis are implemented; the first generation attempt deferred for GPU memory. No additional methodological decision or calendar waiting period is required to resume it. Follow the exact staged commands in `PROGRESS.md`.

The confirmation set is available as soon as the final procedure is frozen. A positive development result is not a prerequisite. Repeatedly changing the method after reading confirmation scores would turn that set into development data.

## Current path

1. Complete the already frozen 20-task public-feedback repair and extra-sampling comparisons, including the bounded reasoning condition. Keep all capped and malformed outputs in the denominator.
2. Run the remaining 40 development tasks using `configs/development-expansion.json`. Candidate and test generation settings and the original selectors stay fixed. The runner has now been implemented. These tasks remain development data.
3. Before reading those 40 tasks' repair outcomes, record which repair conditions will be transferred, their public-only trigger, prompt, budgets, fallback and comparisons. No additional prompt search on the original 20 tasks is needed to begin this transfer. Preserve failed/negative conditions in the report.
4. Freeze the final algorithm and primary comparison, all 180 task IDs, seeds, generation caps, error handling, cost accounting and analysis code in a dedicated confirmation manifest. Verify generation completeness and that selector decisions are saved before the scorer reads references. Analyze once and report the result, positive or negative.

The 60-task calibration split is required only for a final method that fits a threshold or risk/coverage operating point. A threshold-free repair policy does not need to wait for an unrelated abstention experiment. Do not describe ordinary public-test success as a calibrated correctness guarantee.

## Budget and claims

The repair pilot matches extra model-call count and maximum generated tokens within each pair. It does not exactly match realized prefill tokens, output tokens or wall time. Report those costs explicitly. A reasoning-mode benefit over non-thinking generation cannot be attributed solely to feedback, because sampling settings, reasoning and the output cap also change. The reasoning resampling arm is the relevant feedback control.

Confirmation estimates performance for one model on a public benchmark. It does not establish novelty, generalization to other models, production deployment or conference readiness. Nearest-work reproduction and external-validity checks remain research deliverables, rather than calendar-based delays before a frozen evaluation.

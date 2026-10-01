# Temperature-only test of the budget-limited sampling control

Frozen2026-10-01 before new generation. Parent: `mbpp-matched-budget-development-20260915`. Protocol: `configs/diversity-budget-development.json`; executable and input hashes: `budget-plan.json`. This is adaptive development, with100 full-cohort tasks and14 treated task pairs, not a fresh confirmation.

The parent control produced many repeated programs and no correct extra-candidate pool. We test whether increasing nonthinking temperature alone from0.7 to1.0 improves selected-answer correctness at the same2048-output-token budget per triggered task. More distinct strings without more correct candidates is an informative alternative. Earlier pilot temperature results are retained; this expanded budget comparison is not independent evidence against that pilot.

Reuse100 exact saved baseline records and14 reasoning records. Generate only the new nonthinking arm; top_p0.8, inherited model top_k20, prompt, BF16 checkpoint, selector and per-call seed rule remain fixed. Shared call indices have shared seeds, but changed output lengths alter sample counts. The old control and reasoning costs are reused evidence, not new generation costs.

Use the existing deterministic public-only selector and freeze decisions before isolated Linux hidden development scoring. Primary comparison is new versus old selected nonthinking accuracy. Report wins/losses and an exploratory task-bootstrap interval, plus diversity, parser failures, candidate-oracle diagnostics and actual input/output/wall/VRAM costs. Shared caps do not mean identical total compute.14 treated tasks may remain inconclusive; no target gain or significance threshold controls stopping.

At most28672 new output tokens,768 per call,2048 per task; at most28672 positive-length calls. Local generation has a5400-second process deadline and9216MiB free-VRAM guard. No paid API/GPU. Preserve partial outputs and failures; a timeout does not trigger automatic budget expansion. Source code is never executed on the host. Both remote evaluation jobs retain their20-minute limits and restricted Docker configuration.

Run `python -X utf8 scripts/diversity_budget.py execute` in the existing GPU environment. It generates, commits the pool, runs visible selection, freezes decisions, runs isolated scoring, saves results and updates PROGRESS. Its exclusive lock is only a duplicate guard; verify the actual recorded PID before treating an abandoned lock as active. For a completed generation with interrupted evaluation, inspect the journal and use `continue` rather than rerunning inference. Logs are outside the repository under `../tmp/diversity-budget-20261001.*.log`.

No external/confirmation/reserve labels are used. The pending Hugging Face login affects external replication only. This batch can progress while that access remains unavailable.

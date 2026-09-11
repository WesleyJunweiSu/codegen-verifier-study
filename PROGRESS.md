# Experiment checkpoint

Updated: 2026-09-11 (America/New_York). Phase: **development transfer scored; final 180-task confirmation frozen, generation deferred for GPU headroom**.

## Objective and evidence

Build an interview-ready research and engineering project with reproducible code, honest claims, isolated execution and independent confirmation. Private remote: https://github.com/WesleyJunweiSu/codegen-verifier-study. Earlier historical audits and original experiments remain recorded in reports v0.1–v0.6 and the claim ledger; do not regenerate them.

- Data: MBPP+ v0.2.0, 60 development / 60 calibration / 180 confirmation / 78 reserve. Hidden data never enter generation, trigger selection or replacement.
- Original 20 development tasks: first 10/20, selected public-first consensus 12/20; non-thinking feedback 13/20, reasoning feedback 16/20, reasoning resampling 17/20. Adaptive development, not a confirmed 25-point gain.
- Remaining 40 tasks: original first/selection/oracle all 32/40; no mixed-correctness pools. Three public-failure triggers. Both non-thinking extension arms remain 32/40; both reasoning arms reach 33/40, recovering Mbpp/801. Two incomplete reasoning attempts retained. All 40 denominators and four arms preserved.
- Transfer cost: 12 new calls, 9687 output tokens, 4949.37 wall-seconds; uncontrolled desktop timing, not active-GPU throughput. Reports v0.6–v0.7 disclose timing anomalies and limitations.
- Transfer score 34624612668 and visible extension 34624610499 used 1205fbd. All 200 visible decisions match the original scorer. Immutable-decision scoring validation 34625001045 at f067e8b reproduces all 52 candidate records and the exact frozen decision bytes.
- Baseline visible-only validation 34538843816 at c39bc0a reproduces all seven earlier evidence/decision record sets. Twenty-eight contract tests pass. These are engineering validations, not extra accuracy samples.
- Final confirmation implementation a10f26e; final protocol frozen at 7ef1103 in configs/confirmation-protocol.json. One primary comparison: conditional reasoning resampling vs conditional non-thinking resampling, over all 180 tasks. First and selected baseline are secondary. No fitted threshold; calibration is not a gate. No confirmation correctness labels have been inspected.

## Active jobs

No model process or Actions job is active for this project. The development transfer finished; do not resume its completed generator.

Confirmation base run: runs/mbpp-confirmation-20260911. Its first attempt at 2026-09-11T17:07:20Z observed 4582 MiB free, below the frozen 9216 MiB guard, and returned without loading a model. Manifest/test manifest/attempt log exist; 0/720 candidates and 0/180 test responses have been generated. Inspect process state and GPU headroom before retrying. No paid GPU/API without an explicit spending cap, no user-app termination and no silent precision changes.

## Next execution: use this order

All Python generation commands use C:/Users/Asuka/Documents/techblog/.venv/Scripts/python.exe with -X utf8. Model path: C:/Users/Asuka/Documents/techblog/models/Qwen3-4B. Working directory is this repo. The frozen coordinator verifies all configured source hashes and runtime versions; do not edit bound code or rewrite the protocol casually.

1. Check there is no active project GPU job. Run `scripts/confirmation.py base --model-path ...`. It resumes existing keys, observes the memory guard and generates only public-spec inputs. Wait for all 720 candidate records and 180 test responses; preserve capped/malformed outputs. Commit complete inputs to private main before Actions. Do not view any confirmation correctness results.
2. Dispatch **visible-evidence.yml**, input_run **mbpp-confirmation-20260911**. This workflow does not download/mount hidden data. Import its artifact to **runs/mbpp-confirmation-20260911/visible** with workflow/source metadata. Never dispatch old linux-eval.yml for intermediate confirmation.
3. Run `scripts/confirmation.py prepare-extension`; it reads only visible outcomes and freezes public-only triggers. Then run `scripts/confirmation.py extension --model-path ...`. There are two paired extra-generation arms, one call each per triggered task. Failed or unfinished answers fall back. All original 720 candidates are preserved for the first-candidate comparator. Keep every task, no retries for bad model answers, no hidden-label routing.
4. Commit complete extension inputs, then dispatch **visible-evidence.yml**, input_run **mbpp-confirmation-extensions-20260911**. Import to **runs/mbpp-confirmation-extensions-20260911/visible**. The stage appends the fixed first-candidate comparator; no hidden reference dataset is mounted.
5. Run `scripts/freeze_score_inputs.py --run mbpp-confirmation-extensions-20260911`. This validates visible hashes, all task/method keys and selected IDs, then writes frozen-decisions.jsonl and score-plan.json. Commit these immutable inputs. Only then dispatch **score-frozen.yml**, input_run **mbpp-confirmation-extensions-20260911**. Import the output to **runs/mbpp-confirmation-extensions-20260911/linux**. The scorer validates dataset/input/decision hashes before reference loading and does not run selection.
6. Once the entire final score exists, run `scripts/analyze_confirmation.py` exactly with the frozen protocol. It reports the prespecified primary exact two-sided McNemar test, task bootstrap, all method counts/180, rescues/regressions and costs. No interim result inspection, optional stopping or primary-comparison substitution. Report inconclusive/negative results as obtained.

The separate score-frozen development validation is under runs/mbpp-development40-repair-20260908/frozen-score; do not overwrite its original linux results. The earlier freeze_score_inputs.py source hash differs from the version now supporting the extra first baseline; existing development frozen inputs remain valid. Do not re-freeze old completed runs merely to update script hashes.

## Continuation rules

Read this checkpoint and current protocol/claim ledger, inspect local/Actions activity, and avoid duplicate runs. Save all raw responses, hashes, failures and measured costs. Do not execute generated code on ordinary Windows; only the restricted Linux Docker workflows. Publish completed batches to the existing private repository. Notify only for meaningful results, completion, failure or necessary user action; routine unchanged checks remain quiet.

Nearest-work reproduction, external validity and independent review of provisional test annotations remain research deliverables. The project is not a novel/SOTA/conference-ready claim, nor a deployed service. The old unresolved Windows timeout mechanisms do not block confirmation.

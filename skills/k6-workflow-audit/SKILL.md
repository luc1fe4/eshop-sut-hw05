---
name: k6-workflow-audit
description: Design and verify a data-driven local k6 API workflow, collect performance evidence, and audit AI analysis against raw sample logs. Use for performance assignments on authorized test environments.
---

Read the assignment, repository instructions and Git status before editing. Preserve existing work. Identify SUT commit; when an archive lacks Git metadata, state that limitation and hash runtime source rather than inventing provenance.

Build a method/path contract from specification, routes and handlers with file:line sources. Check teammate workflow overlap before changing scope. Probe a synthetic account on the authorized local/test instance to establish exact statuses, response schemas and correlation. Never print passwords, reset tokens, JWTs, cookies or full auth bodies. A seed module may DROP tables when imported: isolate an unchanged runtime copy and its DB before starting it.

Use a shared workflow for all profiles. Load synthetic CSV with SharedArray; use scenario.iterationInTest without wrapping. Partition by scenario if there is more than one. Create a new namespace and adequate row count per run; abort on exhaustion. Correlate each token to its own account and iteration. Check status and business outcomes, stop on a failed step, and measure failed E2E as well as successful E2E. Count starts/finalizations to expose interruption; keep pacing on early exits. Define whether E2E includes think-time.

Run smoke first; present assertions, contract and draft profiles for human review when the assignment calls for it. Record actual feedback separately from agent self-correction. Use pilot evidence to choose Load, stepped Stress, baseline/peak/recovery Spike and 10-15 minute Soak. Label draft, pilot, official and rerun. Do not claim maximum stability from a single stable level.

For each run save sample JSON, separate summary, dashboard HTML with aggregation period short enough for charts, run manifest and resource time series. Capture real tool + backend resource monitor in one frame and real hardware evidence on the required host. Distinguish environment connection failure from SUT failure. Never fabricate screenshots, links, human review or runs. Require the user's existing authorization before publishing/pushing/issues/uploads.

Independently recompute p95 HTTP per endpoint, E2E distributions, HTTP RPS and successful E2E throughput with explicit time windows and denominators. Analyze steady phases, stress holds and spike recovery separately; absent dropped_iterations is not measured zero. Audit actual AI claims against raw files/tags/time windows; record genuine mistakes only. Check optimization claims against code and label hypotheses needing measurement. Preserve actual prompts/outputs; label excerpts and missing transcript rather than reconstructing it.

M5 use in this repository: ../../docs/api-contract.md and ../../docs/review-workload.md; smoke raw data under ../../results/smoke-load-20261119-141451-dc433d78. The skill was authored after that smoke; do not claim it drove the earlier run. A future explicit replay/demo must cover all five M5 steps. Proposed video segment 05:00-06:30; actual recording/link remains pending.

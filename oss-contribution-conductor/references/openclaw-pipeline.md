# OpenClaw PR Pipeline Pattern

This reference describes the reusable OpenClaw workflow pattern behind the skill. Adapt it to your own account, repos, and risk tolerance.

## Goals

- keep a steady queue of high-probability OSS fixes
- avoid duplicate work across autonomous agents
- finish review and CI follow-up instead of endlessly opening new PRs
- preserve GitHub account isolation when multiple agents/workspaces exist
- keep machine state in files instead of chat-only memory

## Suggested lane split

### 1. Queue refill and triage lane

Responsibilities:
- gather candidate issues from trusted sources
- dedupe against previous attempts and already-open PRs
- block broad, duplicate, obsolete, or hard-to-validate issues early
- keep the queue stocked with small surgical candidates

Good candidate profile:
- clear narrow bug
- likely fixable in one branch
- small validation surface
- low maintainer coordination cost

Bad candidate profile:
- broad feature work
- reproduce-heavy bugs with unclear root cause
- toolchain or platform work your host cannot validate easily
- issues already covered by another open PR

Recommended helper sequence:
1. `python3 scripts/validate_state.py --queue ... --tracker ...`
2. `python3 scripts/refill_queue.py --queue ... --tracker ...`
3. optional manual triage pass for broad or ambiguous candidates

### 2. Opener lanes

Run one or more opener lanes in parallel, but give them guardrails:
- claim work strictly in queue order
- use a short lock during planning and claiming
- use a dedicated worktree or branch per PR
- set repo-local git identity before commit
- inspect repo contribution etiquette before opening the PR
- keep fixes small and honest

Typical opener flow:
1. verify `gh whoami`
2. `python3 scripts/claim_next.py --queue ... --lock ... --lane opener-a`
3. inspect templates and contribution rules
4. implement a surgical fix
5. run narrow honest validation
6. open PR with exact template and validation notes
7. `python3 scripts/update_item_status.py ...`
8. persist queue/tracker state

### 3. PR monitor and sync lane

Responsibilities:
- scan all open agent-managed PRs
- detect unresolved review feedback
- detect failing or stale actionable CI
- repair PR-body or template-compliance problems
- push follow-up fixes and re-run checks when appropriate

Recommended helper sequence:
1. `python3 scripts/validate_state.py --queue ... --tracker ...`
2. `python3 scripts/sync_tracker.py --tracker ...`
3. inspect highest-priority follow-up candidates
4. make the smallest needed follow-up patch

Recommended priority order:
1. unresolved review feedback
2. failing or stale actionable CI
3. PRs closest to merge or blocking other work
4. reviewer follow-up after updates
5. stale PR cleanup

## Persistence pattern

Keep machine-readable state outside chat history:
- queue file for candidate issues
- tracker file for opened PRs and issue origins
- short-lived claim lock
- dedicated worktree directories
- optional per-lane run summaries

Why this matters:
- agents reboot
- cron sessions accumulate history
- file-based state survives session resets better than memory alone

See `references/state-schema.md` for concrete fields and status rules.

## Contribution etiquette checks

Make these mandatory before opening or advancing a PR:
- assignment-first rules
- maintainer/admin assignment gates
- star-before-PR expectations
- PR template compliance
- CLA/DCO requirements

Treat etiquette checks as part of correctness, not optional polish.

## Validation philosophy

Prefer honest narrow validation over fake breadth.

Good:
- `git diff --check`
- targeted lint/test/typecheck
- focused manual repro notes

Bad:
- claiming full local validation without having dependencies or setup
- ticking repo checkboxes that are not actually true

## CI triage philosophy

Usually actionable:
- failures tied to touched code
- requested code changes
- CLA or DCO blockers
- template or policy bots when you can satisfy them

Usually non-actionable:
- third-party preview authorization gates
- unrelated flaky infra
- failures that require permissions the agent does not have

## Human interaction philosophy

- keep reviewer replies short and concrete
- thank maintainers when they help
- use emoji reactions to acknowledge comments without clutter
- optimize for maintainers feeling that the agent is easy to work with

## Scaling notes

When the system grows:
- split opener lanes by capacity, not by repo theme alone
- exclude noisy or low-fit repos from intake
- recreate long-lived cron jobs if their session history becomes bloated
- compact durable policy into files so new sessions inherit the workflow quickly
- wrap the helper scripts in a thin `oss-pr` CLI only after the scripts and schema have stabilized

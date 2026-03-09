# Cron Setup

Use cron for exact timing and isolation. Use heartbeat for looser, batched checks. For this workflow, queue refill, opener lanes, and monitor lanes usually fit cron best.

## Recommended lane split

- queue refill + triage: isolated cron job
- opener lane A: isolated cron job
- opener lane B: isolated cron job
- PR monitor + sync: isolated cron job

## Why isolated jobs help

Benefits:
- each lane gets a stable prompt
- queue/tracker state lives in files, not in chat history
- failures stay contained to one lane

Caution:
- isolated cron jobs keep a persistent session per job id
- if one job accumulates too much history, recreate the job to reset its context

## Example schedules

### Queue refill and triage

Suggested cadence:
- every 6 to 12 hours
- or once each morning if rate limits are tight

Prompt shape:

```text
Use the oss-pr-workflow skill. Refill and triage the OSS issue queue.
1. Run the queue validation helper first.
2. Re-triage the front of the queue and block duplicates, obsolete items, and broad low-fit work.
3. If actionable queue depth is below target, run the refill helper with the current discovery profile.
4. Persist queue updates and emit a short JSON-like summary.
5. Stay conservative about noisy repos and non-surgical issues.
```

### Opener lane

Suggested cadence:
- every 1 to 3 hours
- stagger opener lanes so they do not claim at the same second

Prompt shape:

```text
Use the oss-pr-workflow skill. Run opener lane A.
1. Validate state.
2. Verify GitHub identity.
3. Claim exactly one queued issue with the claim helper.
4. Inspect repo etiquette before coding.
5. Implement the smallest credible fix.
6. Run honest narrow validation.
7. Open or update the PR.
8. Persist queue/tracker state and exit.
If nothing claimable exists, stay quiet.
```

### PR monitor and sync lane

Suggested cadence:
- every 2 to 4 hours
- faster only if you have many open PRs and enough quota

Prompt shape:

```text
Use the oss-pr-workflow skill. Run the PR monitor and sync lane.
1. Validate state.
2. Sync tracker against GitHub.
3. Prioritize unresolved review feedback, then actionable failing or stale CI.
4. Repair template-compliance issues when possible.
5. Push only minimal follow-up changes.
6. Persist tracker updates and exit.
If nothing changed and nothing needs action, stay quiet.
```

## Queue depth targets

Useful default targets:
- minimum actionable queue: 8 to 12 items
- opener concurrency: 1 to 2 lanes unless follow-up debt is low
- soft PR cap: stop opening more once follow-up load is clearly outrunning merge rate

## Practical scheduling advice

- stagger jobs to reduce lock contention
- keep opener jobs less frequent than monitor jobs if review debt is growing
- run validation before mutating queue or tracker state
- prefer no-op exits over chatty status spam

## Heartbeat use

Heartbeat is still useful for:
- summarizing lane health
- reporting low queue depth
- reminding the main session about a stuck high-priority PR

Do not move claim-sensitive queue mutation into heartbeat unless you intentionally want looser timing and more context coupling.

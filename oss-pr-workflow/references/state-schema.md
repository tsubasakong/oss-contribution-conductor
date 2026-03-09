# State Schema

Use file-backed state so queue, opener, and monitor lanes can survive chat compaction, cron-session drift, and agent restarts.

## Files

Recommended files:
- queue file: candidate issues waiting to be claimed
- tracker file: opened PRs and their issue origins
- short-lived claim lock: protects queue claiming and status transitions
- optional per-run summaries: debug output only, not authoritative state

## Queue item schema

Minimum shape:

```json
{
  "repo": "owner/repo",
  "issue": 123,
  "title": "Fix sidebar focus state",
  "url": "https://github.com/owner/repo/issues/123",
  "status": "queued",
  "priority": "normal",
  "claimed_by": null,
  "claimed_at": null,
  "source": "gh-search",
  "created_at": "2026-03-09T19:00:00Z"
}
```

Useful optional fields:
- `labels`: string[]
- `updated_at`: issue updated timestamp from GitHub
- `blocked_reason`: short human-readable reason
- `opened_pr`: PR number once a PR exists
- `discovery`: search metadata such as labels/languages/query
- `notes`: short freeform operator notes

## Queue statuses

Use these statuses consistently:
- `queued` — eligible to claim
- `claimed` — currently reserved by one opener lane
- `blocked` — intentionally skipped for a concrete reason
- `deferred` — maybe useful later, but not now
- `opened` — PR created; queue item should no longer be claimable
- `merged` — PR merged
- `closed` — issue/PR path ended without merge

Rules:
- only `queued` items are claimable
- `claimed` items should have `claimed_by` and `claimed_at`
- `opened`, `merged`, and `closed` items should never be claimed again

## Tracker item schema

Minimum shape:

```json
{
  "repo": "owner/repo",
  "issue": 123,
  "pr": 456,
  "status": "open",
  "author": "tsubasakong",
  "lane": "opener-a",
  "title": "Fix sidebar focus state",
  "url": "https://github.com/owner/repo/pull/456",
  "created_at": "2026-03-09T19:10:00Z",
  "last_checked_at": "2026-03-09T21:00:00Z"
}
```

Useful optional fields:
- `review_decision`: `CHANGES_REQUESTED`, `APPROVED`, `REVIEW_REQUIRED`, or `null`
- `merge_state_status`: GitHub merge status summary
- `ci`: summarized CI rollup counts
- `attention`: machine-readable list like `unresolved_review_feedback` or `failing_ci`
- `status_reason`: short human note for blocked/closed/deferred cases

## Tracker statuses

Use these statuses consistently:
- `open` — active PR
- `draft` — active draft PR
- `blocked` — active but waiting on something external
- `deferred` — deliberately paused
- `merged` — merged PR
- `closed` — closed without merge

Rules:
- one active tracker item per `repo + pr`
- tracker is authoritative for PR lifecycle
- queue is authoritative for intake order

## Status transition pattern

Typical lifecycle:

```text
queued -> claimed -> opened -> merged
queued -> claimed -> blocked
queued -> claimed -> deferred
opened -> closed
opened -> merged
open -> blocked -> open
```

When opening a PR:
1. queue item moves from `claimed` to `opened`
2. tracker item is created or updated with PR number and status `open`
3. queue item should record `opened_pr`

When a PR merges:
1. tracker item moves to `merged`
2. queue item moves to `merged`
3. claim metadata is cleared if still present

## Lock semantics

Use a short-lived lock for queue mutation.

Recommended behavior:
- create one lock file before claiming or bulk status updates
- keep the critical section short
- write queue state atomically
- remove the lock even on failure
- treat stale locks as recoverable after a conservative timeout

Do not hold the lock while:
- cloning repos
- running tests
- waiting on network-heavy GitHub inspection
- opening the PR itself

Lock scope should be only the read-modify-write cycle for state files.

## Validation rules

Validate at least:
- queue/tracker files parse as JSON arrays
- `repo` is `owner/repo`
- `issue` and `pr` are positive integers when present
- statuses are in the allowed sets
- no duplicate active queue entries for the same issue
- no duplicate tracker entries for the same PR
- `claimed` items include claimant metadata

## Practical advice

Keep the schema boring. Add fields only when they support:
- scheduling
- dedupe
- claim safety
- PR follow-up priority
- honest debugging

Do not let the schema become a second brain. The skill holds policy; the state files hold execution state.

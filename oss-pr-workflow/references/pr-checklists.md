# PR Checklists

## 1. Preflight checklist

- Confirm active GitHub account with `gh whoami`
- Confirm repo-local `git config user.name` and `git config user.email`
- Confirm fork remote points at the intended account
- Prefer SSH remote if multiple GitHub identities may be cached
- Create or switch to a dedicated branch/worktree

## 2. Issue selection checklist

- Is the issue still open and not already fixed?
- Is there already an active PR for the same problem?
- Is the requested change narrow enough for a surgical patch?
- Can the current host validate the relevant path without heroic setup?
- Is the issue likely to help maintainers instead of creating broad review debt?

## 3. Repository etiquette checklist

Read the issue, PR template, contributing guide, and bot comments. Check explicitly:

- Assignment required before PR?
- Maintainer/admin approval required before assignment?
- Star required or strongly expected before first PR?
- CLA required?
- DCO or signed-off commits required?
- Exact PR body template required?
- Screenshots, reproduction steps, or tests required?

If the repo sets a gate you cannot honestly satisfy, follow the documented process instead of bluffing.

## 4. Patch checklist

- Reproduce enough to understand the bug
- Keep the change surface as small as possible
- Avoid opportunistic cleanup in unrelated files
- Add focused tests only when they increase confidence materially
- Keep commit history simple unless the repo prefers otherwise

## 5. Validation checklist

Only report checks you actually ran. Typical options:

- `git diff --check`
- targeted tests for touched files/modules
- lint on touched paths
- typecheck or compile for touched paths
- focused manual reproduction notes

Never claim full local testing if you only reviewed the diff.

## 6. PR body checklist

- Clear title tied to the user-visible bug
- Link to issue when appropriate
- Short explanation of root cause
- Short explanation of fix
- Exact validation run, not inflated validation
- Template fields completed honestly

## 7. Follow-up checklist

Prioritize in this order:

1. unresolved review feedback
2. failing or stale actionable CI
3. PRs closest to merge
4. reviewer follow-up after updates
5. stale low-value PR cleanup

### Actionable vs non-actionable blockers

Usually actionable:
- requested code changes
- missing template sections
- CLA or DCO issues
- lint/test/typecheck failures related to the patch

Usually non-actionable unless a maintainer asks:
- external preview auth gates
- unrelated flaky infrastructure failures
- environment failures you cannot influence from the patch

## 8. Maintainer interaction checklist

- Acknowledge feedback quickly
- Keep replies short and specific
- Use emoji reactions to show appreciation or acknowledgment without spamming comments
- Avoid arguing with bots; satisfy the template or policy instead
- If wrong, correct the branch and say so plainly

# Example Walkthrough

This walkthrough shows the intended end-to-end shape of a small OSS PR.

## Scenario

Issue:
- repo: `owner/repo`
- issue: `#123`
- bug: inactive sidebar items still receive active styling because a presence selector treats `data-active="false"` as present

## 1. Intake and triage

Check the issue:

```bash
gh issue view 123 --repo owner/repo --comments
gh issue view 123 --repo owner/repo --json title,body,labels,assignees,url
```

Decide whether it is a good fit:
- narrow bug
- small UI surface
- likely one-branch fix
- validation can be honest on the current host

If still promising, add it to the queue or claim it directly if running an opener lane.

## 2. Etiquette inspection

Inspect contribution rules before touching code:

```bash
gh api repos/owner/repo/contents/.github/pull_request_template.md
gh api repos/owner/repo/contents/CONTRIBUTING.md
```

Ask:
- assignment required first?
- exact template required?
- screenshots required?
- CLA or DCO required?

If the repo requires a gate you cannot satisfy, stop here.

## 3. Local branch prep

Create a dedicated branch or worktree and verify identity:

```bash
gh whoami
git config user.name
git config user.email
```

Then implement the narrowest credible fix.

Example change:
- omit `data-active` entirely when the value would be false
- preserve current behavior when true
- keep unrelated cleanup out of the diff

## 4. Honest validation

Run only what you can actually support:

```bash
git diff --check
npm test -- sidebar-button.test.ts
```

If full project setup is unavailable, keep the validation narrower and say so plainly.

## 5. Render and open PR

Generate a starting PR body with the helper script, then adapt it to the repo template.

```bash
python3 scripts/render_pr_body.py \
  --issue 123 \
  --problem "Inactive sidebar items still match active-state presence selectors." \
  --fix "Stop emitting data-active when the item is not active." \
  --validation "git diff --check" \
  --validation "npm test -- sidebar-button.test.ts" \
  --output ./pr-body.md
```

Open or update the PR, making sure the body matches the repo template exactly.

## 6. Persist state

Move queue/tracker state forward:
- queue item: `claimed -> opened`
- tracker item: create `open` record with PR number

## 7. Follow-up loop

Later, if review requests arrive:
1. prioritize the PR ahead of new opener work
2. apply the smallest follow-up diff
3. rerun honest narrow validation
4. update the tracker after pushing

If CI fails:
- fix it if it is tied to the touched path
- ignore it if it is a known external gate and not actionable

## 8. Merge or close-out

When merged:
- tracker status becomes `merged`
- queue item becomes `merged`
- note any reusable lesson in the skill or workflow files if it is durable

If closed without merge:
- mark the tracker `closed`
- mark the queue item `closed` or `deferred`
- record the reason so the system does not retry blindly

## What this walkthrough is teaching

The goal is not just “open PRs.” The goal is to:
- pick work likely to land
- avoid etiquette mistakes
- validate honestly
- keep machine state synchronized
- spend follow-up energy before opening fresh branches

# gh Command Patterns

Use these as building blocks. Adjust fields and filters per repo.

## Identity and repo sanity

```bash
gh whoami
git config user.name
git config user.email
git remote -v
```

## Inspect an issue before starting

```bash
gh issue view 123 --repo owner/repo
gh issue view 123 --repo owner/repo --comments
```

Check linked PRs or duplicate signals:

```bash
gh issue view 123 --repo owner/repo --json title,body,assignees,labels,comments,url
```

## Inspect contribution requirements

```bash
gh api repos/owner/repo/contents/.github/PULL_REQUEST_TEMPLATE.md
gh api repos/owner/repo/contents/.github/pull_request_template.md
gh api repos/owner/repo/contents/CONTRIBUTING.md
gh api repos/owner/repo/contents/.github/ISSUE_TEMPLATE
```

If one path 404s, try the others. Many repos vary.

## Create a fork if needed

```bash
gh repo fork owner/repo --clone=false
```

## Check open PRs and review state

List your open PRs:

```bash
gh pr list --author @me --state open --limit 100
```

Inspect one PR in detail:

```bash
gh pr view 55 --repo owner/repo --comments
gh pr view 55 --repo owner/repo --json number,title,state,isDraft,reviewDecision,mergeStateStatus,statusCheckRollup,url
```

## Check CI

```bash
gh pr checks 55 --repo owner/repo
gh run list --repo owner/repo --limit 10
gh run view <run-id> --repo owner/repo
gh run view <run-id> --repo owner/repo --log-failed
```

## Review feedback loop

Find PRs that likely need attention:

```bash
gh pr list --author @me --state open --limit 100 --json number,title,reviewDecision,updatedAt,url
```

Then inspect the highest-priority PR individually:

```bash
gh pr view 55 --repo owner/repo --comments
gh pr checks 55 --repo owner/repo
```

## Update PR body if a bot enforces a template

```bash
gh pr edit 55 --repo owner/repo --body-file ./pr-body.md
```

## React like a human

Use the GitHub web UI for emoji reactions when that is fastest and clearest. If you are scripting heavily, use `gh api` against the reactions endpoint, but do not over-automate social signals.

## Notes

- Prefer narrow, repeated `gh` calls over one giant opaque script when debugging.
- Always keep validation notes honest in the PR body and comments.
- If your host has multiple GitHub accounts, verify identity before every push, not just once per day.

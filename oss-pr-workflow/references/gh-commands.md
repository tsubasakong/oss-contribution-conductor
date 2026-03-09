# gh Command Patterns

Use these as building blocks. Adjust fields and filters per repo.

## Identity and repo sanity

```bash
gh whoami
git config user.name
git config user.email
git remote -v
```

## Issue discovery

### Search for good-first issues in a language

```bash
gh search issues \
  --state open \
  --label "good first issue" \
  --language python \
  --sort updated \
  --limit 20 \
  --json number,title,url,updatedAt,repository,labels
```

### Search for help-wanted work

```bash
gh search issues \
  --state open \
  --label "help wanted" \
  --language typescript \
  --sort updated \
  --limit 20 \
  --json number,title,url,updatedAt,repository,labels
```

### Search by raw query when labels are inconsistent

```bash
gh search issues "sidebar bug label:bug state:open" \
  --limit 20 \
  --json number,title,url,updatedAt,repository,labels
```

### Drive queue refill through the helper script

```bash
python3 scripts/refill_queue.py \
  --queue ~/code/oss/.ai-pr-targets.json \
  --tracker ~/code/oss/.ai-pr-origin-tracker.json \
  --label "good first issue" \
  --language python \
  --limit 20
```

## Inspect an issue before starting

```bash
gh issue view 123 --repo owner/repo
gh issue view 123 --repo owner/repo --comments
gh issue view 123 --repo owner/repo --json title,body,assignees,labels,comments,url
```

## Detect duplicate work or related PRs

### Check the issue itself for linked signals

```bash
gh issue view 123 --repo owner/repo --json title,body,labels,comments,url
```

### Search open PRs in the same repo for similar issue references

```bash
gh pr list --repo owner/repo --state open --search "123" --limit 20
```

### GraphQL pattern for richer dedupe checks

Use this when you need to inspect issue references or cross-links more precisely than the basic CLI search allows.

```bash
gh api graphql -f query='\
query($owner:String!, $repo:String!, $number:Int!) {\
  repository(owner:$owner, name:$repo) {\
    issue(number:$number) {\
      title\
      url\
      timelineItems(first:50, itemTypes:[CONNECTED_EVENT, CROSS_REFERENCED_EVENT]) {\
        nodes {\
          __typename\
        }\
      }\
    }\
  }\
}' -F owner=owner -F repo=repo -F number=123
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

## Tracker sync helper

```bash
python3 scripts/sync_tracker.py \
  --tracker ~/code/oss/.ai-pr-origin-tracker.json
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

Generate a starting body with the helper script, then adapt it to the repo template:

```bash
python3 scripts/render_pr_body.py \
  --issue 123 \
  --problem "Explain the bug clearly." \
  --fix "Explain the narrow fix clearly." \
  --validation "git diff --check" \
  --output ./pr-body.md

gh pr edit 55 --repo owner/repo --body-file ./pr-body.md
```

## React like a human

Use the GitHub web UI for emoji reactions when that is fastest and clearest. If you are scripting heavily, use `gh api` against the reactions endpoint, but do not over-automate social signals.

## Notes

- Prefer narrow, repeated `gh` calls over one giant opaque script when debugging.
- Always keep validation notes honest in the PR body and comments.
- If your host has multiple GitHub accounts, verify identity before every push, not just once per day.

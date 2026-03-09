---
name: oss-pr-workflow
description: Plan and execute efficient open-source pull requests on GitHub from OpenClaw or the gh CLI. Use when an agent needs to choose a good OSS issue, check contribution etiquette (assignment-first, star-before-PR, templates, CLA, DCO), prepare a small fix, validate honestly, open or update a PR, handle review feedback and CI follow-up, or design a reusable PR automation workflow.
---

# OSS PR Workflow

## Overview

Use this skill to contribute small, high-leverage fixes to open-source repositories without wasting maintainer time.

Optimize for:
- small surgical fixes
- honest validation
- fast maintainer-friendly communication
- finishing existing PRs before opening more

## Operating Loop

### 1. Preflight identity and repo setup

- Run `gh whoami`.
- Check `git config user.name` and `git config user.email` in the actual repo/worktree before commit.
- Prefer fork remotes that cannot silently use the wrong GitHub identity; SSH is usually safer than HTTPS when multiple accounts are cached.
- Use a dedicated branch or worktree per PR.

### 2. Pick work with a high chance of landing

Prioritize:
- clear bug reports with a narrow blast radius
- docs, config, validation, UI, TypeScript, Python, and similar small fixes
- issues that already point at the failing file or behavior
- PRs already close to merge but blocked on review feedback or actionable CI

Avoid or defer:
- broad feature requests
- duplicates or already-fixed issues
- issues with another active PR unless you are explicitly taking over
- reproduce-heavy problems you cannot validate
- infra or toolchain work that the current host cannot test quickly

### 3. Check repository etiquette before touching the branch

Before opening or advancing a PR, inspect the repo's issue template, PR template, contributing guide, and bot comments. Explicitly check:
- whether the issue must be assigned to you first
- whether a maintainer or admin must grant assignment
- whether the repo expects a project star before a PR
- whether a PR template, CLA, DCO, or checklist is required

If the repo has a gate you cannot honestly satisfy, stop and follow the documented process.

### 4. Implement the smallest credible fix

- Reproduce enough to be confident.
- Change the smallest surface that solves the reported problem.
- Add focused tests only when they improve confidence without exploding scope.
- Keep unrelated cleanup out of the branch.
- If local dependencies or toolchains are missing, still run the strongest narrow validation available.

### 5. Validate honestly

Only claim what you actually ran.

Good examples:
- `git diff --check`
- targeted unit tests
- compile or typecheck for changed files
- linters against touched paths
- focused manual reproduction steps

Bad pattern:
- checking "tested locally" when you only inspected the diff

### 6. Open or update the PR cleanly

- Use the repo template exactly.
- Link the issue precisely (`Fixes #123`, `Closes #123`) when appropriate.
- Summarize the bug, the fix, and the exact validation run.
- Keep the title concrete and maintainer-readable.
- If the repo enforces template structure, repair the body instead of arguing with the bot.

### 7. Run the follow-up loop

Work this order:
1. unresolved review feedback
2. failing or stale actionable CI
3. PRs closest to merge or blocking other work
4. reviewer follow-up after new fixes land
5. close or defer stale low-value work

Triage rules:
- Ignore non-actionable external gates unless a maintainer specifically asks about them.
- Treat CLA or DCO-only blockers as actionable if you can resolve them.
- Do not open more PRs just to feel productive while existing ones are waiting on easy follow-up.

### 8. Interact like a good collaborator

- Reply briefly and concretely.
- Thank reviewers when they unblock or clarify something.
- Use GitHub emoji reactions to acknowledge comments and keep interactions warm without adding noise.
- Do not be defensive; make the diff better.

## Fast decision heuristics

Ask:
- Is this issue surgically fixable in one branch?
- Can I validate the touched path honestly on this host?
- Is there already a PR or duplicate issue?
- Will this save maintainer time instead of creating review debt?
- Is the repo asking for assignment or a star first?

If several answers are no, defer it.

## References

Read these only when needed:
- `references/pr-checklists.md` for reusable preflight, etiquette, PR, and follow-up checklists
- `references/gh-commands.md` for concrete `gh` commands and review or CI loops
- `references/openclaw-pipeline.md` for the multi-lane OpenClaw automation pattern that inspired this skill

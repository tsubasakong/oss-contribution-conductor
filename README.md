# OSS Contribution Conductor

[![Validate](https://github.com/tsubasakong/oss-contribution-conductor/actions/workflows/validate.yml/badge.svg)](https://github.com/tsubasakong/oss-contribution-conductor/actions/workflows/validate.yml)
[![Skill package](https://img.shields.io/badge/package-.skill-blue)](./oss-contribution-conductor.skill)
[![OpenClaw skill](https://img.shields.io/badge/OpenClaw-skill-7c3aed)](./oss-contribution-conductor/SKILL.md)
[![Changelog](https://img.shields.io/badge/changelog-date--based-orange)](./CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

A reusable OpenClaw skill and helper toolkit for running disciplined, maintainer-friendly open-source contribution workflows on GitHub.

This repo is for agents and humans who want a repeatable way to:
- pick high-probability OSS issues
- avoid duplicate or etiquette-breaking PRs
- open small, honest fixes
- track follow-up work across many open PRs
- keep queue and tracker state in files instead of fragile chat memory

## Why this repo exists

A lot of autonomous OSS contribution attempts fail in boring ways: bad issue selection, dishonest validation, ignored repo templates, duplicated work, or no follow-through once review feedback arrives.

OSS Contribution Conductor packages the workflow that avoids those mistakes:
- a reusable skill with judgment-heavy guidance
- deterministic helper scripts for queue and tracker state
- references for etiquette, CI triage, cron lane design, and error recovery
- sample state files that show the data model concretely
- a distributable `.skill` artifact for easy sharing

## What’s inside

```text
.
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── README.md
├── examples/
│   └── demo-state/
├── oss-contribution-conductor/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/
├── oss-contribution-conductor.skill
├── tests/
│   ├── fixtures/
│   ├── run_all.py
│   └── test_cli_scripts.py
└── tools/
    ├── package_skill.py
    └── validate_repo.py
```

## Repository highlights

### Skill source
- `oss-contribution-conductor/SKILL.md` contains the core workflow and decision rules.
- `oss-contribution-conductor/references/` contains focused supporting docs loaded only when needed.

### Helper scripts
The skill ships with deterministic helpers for the repetitive parts of the workflow:

| Script | Purpose |
| --- | --- |
| `scripts/refill_queue.py` | Add new issue candidates from `gh search` results |
| `scripts/claim_next.py` | Safely claim the next queued item for an opener lane |
| `scripts/update_item_status.py` | Apply queue/tracker state transitions consistently |
| `scripts/sync_tracker.py` | Refresh tracker state from GitHub PR data |
| `scripts/validate_state.py` | Validate queue/tracker schema and cross-file consistency |
| `scripts/render_pr_body.py` | Generate a clean starter PR body |
| `scripts/common.py` | Shared helpers used by the other scripts |

### Example state and smoke tests
Inspired by larger harness repos, this repo now ships a small amount of executable proof instead of only documentation.

- `examples/demo-state/queue.sample.json` and `tracker.sample.json` show the queue/tracker schema with realistic values.
- `tests/test_cli_scripts.py` exercises the helper CLIs against those samples and fixture data.
- `tests/run_all.py` keeps local and CI test runs dependency-free.

### Packaged artifact
- `oss-contribution-conductor.skill` is the distributable archive built from the source skill folder.

### Community and maintenance docs
- `CHANGELOG.md` tracks meaningful repo changes in a lightweight date-based format.
- `CODE_OF_CONDUCT.md` sets the tone for collaboration without turning the repo into policy theater.

## Quick start

### 1. Read the skill
Start with:
- [`oss-contribution-conductor/SKILL.md`](./oss-contribution-conductor/SKILL.md)

Then pull in references as needed:
- `references/pr-checklists.md`
- `references/gh-commands.md`
- `references/state-schema.md`
- `references/error-recovery.md`
- `references/cron-setup.md`
- `references/example-walkthrough.md`
- `references/cli-design.md`
- `references/openclaw-pipeline.md`

### 2. Inspect the sample state
If you want to understand the queue/tracker model before wiring up automation, open:
- [`examples/demo-state/queue.sample.json`](./examples/demo-state/queue.sample.json)
- [`examples/demo-state/tracker.sample.json`](./examples/demo-state/tracker.sample.json)

### 3. Use the source skill or the packaged archive
Depending on how you manage OpenClaw skills, either:
- use the source folder directly from `oss-contribution-conductor/`, or
- share/import the packaged `oss-contribution-conductor.skill` archive

### 4. Validate, test, and refresh the package locally
```bash
make test
make validate
make package
```

## Design principles

This repo is opinionated on purpose.

- **Prefer small surgical fixes.** Broad feature work is usually a poor fit for autonomous opening lanes.
- **Validate honestly.** Never claim testing you did not actually run.
- **Respect repo etiquette.** Assignment rules, PR templates, CLA/DCO gates, and reviewer norms matter.
- **Finish follow-up work.** Unresolved review feedback and actionable CI come before opening more PRs.
- **Keep machine state in files.** Queue and tracker files survive compaction, restarts, and cron-session drift.
- **Use scripts for deterministic work, not judgment.** Scripts keep the bookkeeping consistent; the skill handles decisions.

## Development

### Requirements
- Python 3.10+
- `gh` for GitHub-driven workflows
- `git`

### Useful commands
```bash
make test       # run stdlib Python smoke tests
make validate   # repo checks + compile checks + smoke tests + package parity
make package    # rebuild oss-contribution-conductor.skill from source
```

## GitHub automation

This repo includes a validation workflow that checks:
- the skill frontmatter is sane
- the committed `.skill` archive matches the source folder
- the helper scripts and tests compile cleanly
- the smoke-test suite passes
- the sample queue/tracker state stays valid JSON

That keeps the repo feeling maintained instead of drifting out of sync.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

Short version:
- keep changes focused
- avoid adding fluffy docs inside the skill itself
- preserve the split between judgment-heavy guidance and deterministic helpers
- keep the packaged `.skill` archive in sync with source changes
- run the smoke tests before opening a PR

## Roadmap ideas

Good next-level improvements if the repo grows:
- release automation for tagged `.skill` artifacts
- a thin `oss-pr` wrapper CLI over the helper scripts
- more fixture coverage around tracker sync edge cases
- a public demo walkthrough using a real contribution from issue to merged PR

## License

[MIT](./LICENSE)

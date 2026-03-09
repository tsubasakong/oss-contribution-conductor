# Thin CLI Design

Do not start with a giant product. Start with helper scripts and let a future thin CLI wrap them once the workflow stabilizes.

## Design split

### Keep in the skill

Keep judgment-heavy logic in the skill:
- which issues are worth taking
- how to classify fast-lane vs blocked work
- how to interpret etiquette rules
- how to respond to reviewers and maintainers
- whether a CI failure is actionable or ambient noise

### Move into scripts or a thin CLI

Move repetitive, deterministic work into scripts:
- queue refill
- queue claim
- queue or tracker status updates
- tracker sync
- schema validation
- standard PR body rendering

## Proposed command tree

```text
oss-pr queue refill
oss-pr queue claim
oss-pr queue list
oss-pr queue update-status

oss-pr tracker sync
oss-pr tracker list
oss-pr tracker show

oss-pr repo inspect-etiquette
oss-pr repo find-related-prs

oss-pr pr render-body

oss-pr state validate
oss-pr state summary

oss-pr doctor
```

## MVP commands

If you only build the first useful slice, build these first:
- `queue refill`
- `queue claim`
- `tracker sync`
- `state validate`
- `pr render-body`

These cover the highest-frequency deterministic operations.

## Output philosophy

Prefer machine-readable JSON output by default or via a `--json` flag.

Good CLI output should make it easy for an agent to answer:
- what changed?
- what was skipped?
- what needs attention next?
- did the command mutate state?

## Packaging advice

Phase 1:
- ship standalone Python helper scripts in `scripts/`

Phase 2:
- add a small `oss-pr` wrapper that delegates to those scripts

Phase 3:
- only after the workflow is stable, invest in a fuller CLI package with tests, versioning, and distribution

## Why keep it thin

A heavy CLI hard-codes policy too early. This workflow still depends on judgment, evolving etiquette knowledge, and host-specific validation constraints. Keep the CLI boring and reliable; keep the skill smart and flexible.

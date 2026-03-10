# Contributing

Thanks for improving OSS Contribution Conductor.

## What this repo is optimizing for

This repo is meant to stay compact, reusable, and agent-friendly.

Priorities:
- clear workflow guidance
- deterministic helper scripts
- honest, low-noise automation patterns
- minimal clutter
- public-repo hygiene that makes the project easy to trust

## Community expectations

Be respectful, direct, and collaborative.

If you are participating here, follow the spirit of [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md): improve the work without making the repo more annoying for other people.

## Contribution guidelines

### Keep changes focused
Prefer narrow improvements over broad rewrites.

Good examples:
- improving one reference file
- tightening a helper script
- fixing packaging or validation drift
- making README or contributor guidance clearer
- expanding smoke-test coverage for a real script behavior

### Preserve the design split
Keep this boundary sharp:
- **skill/docs** for judgment-heavy guidance
- **scripts** for repetitive deterministic work

Do not move subjective decision-making into scripts unless it truly benefits from determinism.

### Avoid repo bloat inside the skill folder
The skill itself should stay lean.

Inside `oss-contribution-conductor/`, only add files that directly help the skill do its job:
- `SKILL.md`
- `references/`
- `scripts/`
- other bundled resources only when they are clearly justified

Avoid adding extra “nice to have” docs inside the skill folder.

### Keep examples realistic
If you touch `examples/demo-state/`, keep the sample queue/tracker data valid and representative of real usage.

These files are both documentation and test fixtures.

### Keep the package in sync
If you change anything under `oss-contribution-conductor/`, refresh the packaged artifact before submitting.

```bash
make validate
make package
```

### Validate honestly
If you mention validation in a PR, only list what you actually ran.

## Development commands

```bash
make test
make validate
make package
```

## Pull request checklist

Before opening a PR:
- [ ] I kept the change scoped and relevant to this repo
- [ ] I updated the packaged `.skill` archive if needed
- [ ] I ran `make test`
- [ ] I ran `make validate`
- [ ] I did not add unnecessary files or productized fluff inside the skill folder

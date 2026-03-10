# Changelog

All notable changes to this repository are documented here.

This project is still small and does not use release tags yet, so entries are date-based for now.

## Unreleased

### Added
- Public community docs with a repository-level `CODE_OF_CONDUCT.md`
- Sample queue/tracker state files under `examples/demo-state/`
- A stdlib Python smoke-test suite for the bundled helper scripts
- `tests/run_all.py` so local and CI test execution stays simple and dependency-free

### Changed
- `make validate` now runs the smoke-test suite in addition to packaging and compile checks
- README and contributor docs now document examples, tests, and maintenance expectations more clearly
- Repository validation now checks for key public docs and example-state fixtures

## 2026-03-09

### Added
- Initial public repo polish pass: `CONTRIBUTING.md`, `LICENSE`, `Makefile`, GitHub issue/PR templates, validation workflow, packaging tools, and archive parity checks
- Bundled helper scripts for queue refill, claiming, tracker sync, state validation, and starter PR-body rendering
- Focused references for etiquette, CI triage, cron lane design, error recovery, and state schema

### Changed
- Renamed the project from `openclaw-oss-pr-skill` to `oss-contribution-conductor`
- Repackaged the distributable archive as `oss-contribution-conductor.skill`
- Strengthened the README and GitHub metadata so the repo is easier to understand and share

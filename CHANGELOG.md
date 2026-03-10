# Changelog

All notable changes to this repository are documented here.

This project uses a lightweight SemVer-style release strategy. Before `1.0.0`, tags use the `v0.x.y` series while the skill layout and workflow details continue to harden.

## [Unreleased]

- No unreleased entries yet.

## [0.1.0] - 2026-03-09

### Added
- Initial public repo polish: `CONTRIBUTING.md`, `LICENSE`, `Makefile`, GitHub issue/PR templates, validation workflow, packaging tools, and archive parity checks
- Bundled helper scripts for queue refill, claiming, tracker sync, state validation, and starter PR-body rendering
- Focused references for etiquette, CI triage, cron lane design, error recovery, state schema, and pipeline design
- Public community docs with a repository-level `CODE_OF_CONDUCT.md`
- Sample queue/tracker state files under `examples/demo-state/`
- A stdlib Python smoke-test suite for the bundled helper scripts
- A release workflow that publishes the packaged `.skill` archive and checksum on version tags

### Changed
- Renamed the project from `openclaw-oss-pr-skill` to `oss-contribution-conductor`
- Repackaged the distributable archive as `oss-contribution-conductor.skill`
- Sharpened the README opening section, badges, orientation links, and release/tagging guidance for a better GitHub landing page
- Extended repository validation so public docs, sample-state fixtures, and smoke tests stay in sync with the repo

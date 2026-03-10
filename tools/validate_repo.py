#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "oss-contribution-conductor"
ARCHIVE = ROOT / "oss-contribution-conductor.skill"
README = ROOT / "README.md"
CHANGELOG = ROOT / "CHANGELOG.md"
CODE_OF_CONDUCT = ROOT / "CODE_OF_CONDUCT.md"
SAMPLE_QUEUE = ROOT / "examples" / "demo-state" / "queue.sample.json"
SAMPLE_TRACKER = ROOT / "examples" / "demo-state" / "tracker.sample.json"


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"{path.relative_to(ROOT)} is missing YAML frontmatter")

    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        raise SystemExit(f"{path.relative_to(ROOT)} has malformed YAML frontmatter")

    frontmatter = parts[0].removeprefix("---\n")
    data: dict[str, str] = {}
    for raw_line in frontmatter.splitlines():
        if not raw_line or raw_line.startswith("#") or raw_line.startswith(" "):
            continue
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def read_source_files() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for path in sorted(SKILL_DIR.rglob("*")):
        if path.is_file():
            files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    return files


def read_archive_files() -> dict[str, bytes]:
    if not ARCHIVE.exists():
        raise SystemExit(f"missing packaged artifact: {ARCHIVE.relative_to(ROOT)}")
    files: dict[str, bytes] = {}
    with ZipFile(ARCHIVE) as zf:
        for name in sorted(zf.namelist()):
            files[name] = zf.read(name)
    return files


def require_json_array(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"missing required file: {path.relative_to(ROOT)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path.relative_to(ROOT)} is not valid JSON: {exc}") from exc
    if not isinstance(payload, list):
        raise SystemExit(f"{path.relative_to(ROOT)} must contain a JSON array")


def main() -> int:
    for path in (README, CHANGELOG, CODE_OF_CONDUCT):
        if not path.exists():
            raise SystemExit(f"missing required file: {path.relative_to(ROOT)}")
    if not SKILL_DIR.exists():
        raise SystemExit("missing skill source directory")

    require_json_array(SAMPLE_QUEUE)
    require_json_array(SAMPLE_TRACKER)

    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        raise SystemExit("missing oss-contribution-conductor/SKILL.md")

    fm = parse_frontmatter(skill_md)
    if fm.get("name") != SKILL_DIR.name:
        raise SystemExit(f"skill name mismatch: expected {SKILL_DIR.name!r}, got {fm.get('name')!r}")
    if not fm.get("description"):
        raise SystemExit("skill description must not be empty")

    source_files = read_source_files()
    archive_files = read_archive_files()

    missing_from_archive = sorted(set(source_files) - set(archive_files))
    extra_in_archive = sorted(set(archive_files) - set(source_files))
    changed_files = sorted(name for name in source_files if name in archive_files and source_files[name] != archive_files[name])

    if missing_from_archive or extra_in_archive or changed_files:
        problems = {
            "missing_from_archive": missing_from_archive,
            "extra_in_archive": extra_in_archive,
            "changed_files": changed_files,
        }
        raise SystemExit(json.dumps(problems, indent=2))

    summary = {
        "ok": True,
        "skill": SKILL_DIR.name,
        "source_file_count": len(source_files),
        "archive_file_count": len(archive_files),
        "examples_checked": [SAMPLE_QUEUE.relative_to(ROOT).as_posix(), SAMPLE_TRACKER.relative_to(ROOT).as_posix()],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

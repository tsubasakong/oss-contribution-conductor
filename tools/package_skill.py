#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "oss-contribution-conductor"
ARCHIVE = ROOT / "oss-contribution-conductor.skill"
FIXED_TIMESTAMP = (2026, 1, 1, 0, 0, 0)


def iter_skill_files() -> list[Path]:
    return sorted(path for path in SKILL_DIR.rglob("*") if path.is_file())


def build_archive() -> None:
    if not SKILL_DIR.exists():
        raise SystemExit(f"missing skill directory: {SKILL_DIR}")

    tmp_archive = ARCHIVE.with_suffix(".skill.tmp")
    with ZipFile(tmp_archive, "w", compression=ZIP_DEFLATED) as zf:
        for path in iter_skill_files():
            rel_path = path.relative_to(ROOT).as_posix()
            info = ZipInfo(rel_path)
            info.date_time = FIXED_TIMESTAMP
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (path.stat().st_mode & 0o777) << 16
            zf.writestr(info, path.read_bytes())

    tmp_archive.replace(ARCHIVE)
    print(f"wrote {ARCHIVE.relative_to(ROOT)}")


if __name__ == "__main__":
    build_archive()

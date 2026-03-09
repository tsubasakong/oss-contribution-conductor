#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

QUEUE_STATUSES = {"queued", "claimed", "blocked", "deferred", "opened", "merged", "closed"}
TRACKER_STATUSES = {"open", "draft", "blocked", "deferred", "merged", "closed"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_repo(repo: str) -> str:
    repo = (repo or "").strip()
    if repo.count("/") != 1:
        raise ValueError(f"repo must look like owner/repo, got: {repo!r}")
    owner, name = repo.split("/", 1)
    if not owner or not name:
        raise ValueError(f"repo must look like owner/repo, got: {repo!r}")
    return f"{owner}/{name}"


def issue_key(repo: str, issue: int) -> str:
    return f"{normalize_repo(repo)}#{int(issue)}"


def pr_key(repo: str, pr: int) -> str:
    return f"{normalize_repo(repo)}!{int(pr)}"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return default
    return json.loads(text)


def save_json(path: Path, data: Any) -> None:
    ensure_parent(path)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    os.replace(tmp_path, path)


def print_json(data: Any) -> None:
    json.dump(data, sys.stdout, indent=2, sort_keys=False)
    sys.stdout.write("\n")


def gh_json(args: list[str]) -> Any:
    cmd = ["gh", *args]
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        stdout = completed.stdout.strip()
        details = stderr or stdout or f"exit code {completed.returncode}"
        raise RuntimeError(f"gh command failed: {' '.join(cmd)}\n{details}")
    raw = completed.stdout.strip()
    if not raw:
        return None
    return json.loads(raw)


def item_repo(item: dict[str, Any]) -> str | None:
    repo = item.get("repo")
    if isinstance(repo, str) and repo.count("/") == 1:
        return repo
    return None


def summarize_status_rollup(rollup: list[dict[str, Any]] | None) -> dict[str, int]:
    summary = {
        "success": 0,
        "failure": 0,
        "pending": 0,
        "cancelled": 0,
        "neutral": 0,
        "total": 0,
    }
    for item in rollup or []:
        state = str(
            item.get("conclusion")
            or item.get("state")
            or item.get("status")
            or ""
        ).strip().lower()
        if state in {"success", "successful", "passed"}:
            summary["success"] += 1
        elif state in {"failure", "failed", "timed_out", "action_required", "startup_failure"}:
            summary["failure"] += 1
        elif state in {"pending", "queued", "in_progress", "requested", "waiting", "expected"}:
            summary["pending"] += 1
        elif state in {"cancelled", "canceled", "skipped", "stale"}:
            summary["cancelled"] += 1
        else:
            summary["neutral"] += 1
    summary["total"] = sum(summary[k] for k in ("success", "failure", "pending", "cancelled", "neutral"))
    return summary


@contextmanager
def file_lock(
    lock_path: Path,
    *,
    stale_seconds: int = 1800,
    wait_seconds: float = 30.0,
    poll_seconds: float = 0.2,
) -> Iterator[None]:
    ensure_parent(lock_path)
    start = time.time()
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(json.dumps({"pid": os.getpid(), "created_at": utc_now_iso()}) + "\n")
            break
        except FileExistsError:
            try:
                age = time.time() - lock_path.stat().st_mtime
            except FileNotFoundError:
                continue
            if age > stale_seconds:
                try:
                    lock_path.unlink()
                    continue
                except FileNotFoundError:
                    continue
            if time.time() - start > wait_seconds:
                raise TimeoutError(f"timed out waiting for lock: {lock_path}")
            time.sleep(poll_seconds)
    try:
        yield
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass

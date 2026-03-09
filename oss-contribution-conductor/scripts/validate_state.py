#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import QUEUE_STATUSES, TRACKER_STATUSES, issue_key, load_json, normalize_repo, pr_key, print_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate OSS PR queue/tracker state files.")
    parser.add_argument("--queue", help="Path to queue JSON file")
    parser.add_argument("--tracker", help="Path to tracker JSON file")
    return parser.parse_args()


def is_positive_int(value: Any) -> bool:
    return isinstance(value, int) and value > 0


def validate_queue(queue: list[Any], errors: list[str], warnings: list[str]) -> dict[str, int]:
    seen = set()
    counts = {status: 0 for status in QUEUE_STATUSES}
    for index, item in enumerate(queue):
        prefix = f"queue[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} is not an object")
            continue
        repo = item.get("repo")
        issue = item.get("issue")
        status = item.get("status")
        try:
            normalize_repo(repo)
        except Exception:
            errors.append(f"{prefix}.repo is invalid: {repo!r}")
        if not is_positive_int(issue):
            errors.append(f"{prefix}.issue must be a positive integer")
        if status not in QUEUE_STATUSES:
            errors.append(f"{prefix}.status is invalid: {status!r}")
        else:
            counts[status] += 1
        if is_positive_int(issue) and isinstance(repo, str):
            try:
                key = issue_key(repo, issue)
                if key in seen:
                    errors.append(f"duplicate queue issue entry: {key}")
                seen.add(key)
            except Exception:
                pass
        if status == "claimed":
            if not item.get("claimed_by"):
                errors.append(f"{prefix} is claimed but missing claimed_by")
            if not item.get("claimed_at"):
                warnings.append(f"{prefix} is claimed but missing claimed_at")
        if status in {"opened", "merged", "closed"} and item.get("claimed_by"):
            warnings.append(f"{prefix} still has claim metadata after terminal/opened status")
    return counts


def validate_tracker(tracker: list[Any], errors: list[str], warnings: list[str]) -> dict[str, int]:
    seen = set()
    counts = {status: 0 for status in TRACKER_STATUSES}
    for index, item in enumerate(tracker):
        prefix = f"tracker[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} is not an object")
            continue
        repo = item.get("repo")
        pr = item.get("pr")
        issue = item.get("issue")
        status = item.get("status")
        try:
            normalize_repo(repo)
        except Exception:
            errors.append(f"{prefix}.repo is invalid: {repo!r}")
        if not is_positive_int(pr):
            errors.append(f"{prefix}.pr must be a positive integer")
        if issue is not None and not is_positive_int(issue):
            errors.append(f"{prefix}.issue must be a positive integer when present")
        if status not in TRACKER_STATUSES:
            errors.append(f"{prefix}.status is invalid: {status!r}")
        else:
            counts[status] += 1
        if is_positive_int(pr) and isinstance(repo, str):
            try:
                key = pr_key(repo, pr)
                if key in seen:
                    errors.append(f"duplicate tracker PR entry: {key}")
                seen.add(key)
            except Exception:
                pass
        if status in {"open", "draft", "blocked"} and not item.get("last_checked_at"):
            warnings.append(f"{prefix} is active but missing last_checked_at")
    return counts


def cross_validate(queue: list[Any], tracker: list[Any], warnings: list[str]) -> None:
    queue_by_issue = {}
    tracker_by_issue = {}
    for item in queue:
        if isinstance(item, dict) and isinstance(item.get("repo"), str) and is_positive_int(item.get("issue")):
            try:
                queue_by_issue[issue_key(item["repo"], item["issue"])] = item
            except Exception:
                pass
    for item in tracker:
        if isinstance(item, dict) and isinstance(item.get("repo"), str) and is_positive_int(item.get("issue")):
            try:
                tracker_by_issue[issue_key(item["repo"], item["issue"])] = item
            except Exception:
                pass

    for key, queue_item in queue_by_issue.items():
        tracker_item = tracker_by_issue.get(key)
        if queue_item.get("status") == "opened" and tracker_item is None:
            warnings.append(f"queue item {key} is opened but missing tracker entry")
        if queue_item.get("status") == "queued" and tracker_item and tracker_item.get("status") in {"open", "draft", "merged", "closed"}:
            warnings.append(f"queue item {key} is still queued while tracker already exists")


def main() -> int:
    args = parse_args()
    if not args.queue and not args.tracker:
        raise SystemExit("at least one of --queue or --tracker is required")

    errors: list[str] = []
    warnings: list[str] = []
    queue: list[Any] = []
    tracker: list[Any] = []
    queue_counts: dict[str, int] = {}
    tracker_counts: dict[str, int] = {}

    if args.queue:
        queue = load_json(Path(args.queue), default=[])
        if not isinstance(queue, list):
            raise SystemExit("queue file must contain a JSON array")
        queue_counts = validate_queue(queue, errors, warnings)

    if args.tracker:
        tracker = load_json(Path(args.tracker), default=[])
        if not isinstance(tracker, list):
            raise SystemExit("tracker file must contain a JSON array")
        tracker_counts = validate_tracker(tracker, errors, warnings)

    if queue and tracker:
        cross_validate(queue, tracker, warnings)

    print_json(
        {
            "ok": not errors,
            "errors": errors,
            "warnings": warnings,
            "queue_counts": queue_counts,
            "tracker_counts": tracker_counts,
        }
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

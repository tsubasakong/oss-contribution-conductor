#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import TRACKER_STATUSES, file_lock, load_json, normalize_repo, print_json, save_json, utc_now_iso


QUEUE_ALLOWED = {"queued", "claimed", "blocked", "deferred", "opened", "merged", "closed"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update queue and/or tracker item status.")
    parser.add_argument("--queue", help="Path to queue JSON file")
    parser.add_argument("--tracker", help="Path to tracker JSON file")
    parser.add_argument("--lock", help="Optional lock file for queue/tracker mutation")
    parser.add_argument("--repo", required=True, help="Repo in owner/repo form")
    parser.add_argument("--issue", type=int, help="Issue number")
    parser.add_argument("--pr", type=int, help="PR number")
    parser.add_argument("--status", required=True, help="New status")
    parser.add_argument("--reason", help="Short status reason")
    parser.add_argument("--lane", help="Lane responsible for the item")
    parser.add_argument("--author", help="GitHub author for tracker creation")
    parser.add_argument("--title", help="Optional title override")
    parser.add_argument("--url", help="Optional URL override")
    parser.add_argument("--clear-claim", action="store_true", help="Clear claim metadata on queue items")
    parser.add_argument("--create-tracker-if-missing", action="store_true", help="Create tracker item when status is opened/open/draft and a PR number is supplied")
    return parser.parse_args()


def tracker_status_from_input(status: str) -> str:
    if status == "opened":
        return "open"
    return status


def update_queue_item(item: dict[str, Any], args: argparse.Namespace) -> None:
    item["status"] = args.status
    item["updated_at"] = utc_now_iso()
    if args.reason:
        item["status_reason"] = args.reason
        if args.status == "blocked":
            item["blocked_reason"] = args.reason
    if args.pr:
        item["opened_pr"] = args.pr
    if args.clear_claim or args.status != "claimed":
        item["claimed_by"] = None
        item["claimed_at"] = None


def update_tracker_item(item: dict[str, Any], args: argparse.Namespace) -> None:
    item["status"] = tracker_status_from_input(args.status)
    item["last_checked_at"] = utc_now_iso()
    if args.reason:
        item["status_reason"] = args.reason
    if args.lane:
        item["lane"] = args.lane
    if args.title:
        item["title"] = args.title
    if args.url:
        item["url"] = args.url


def maybe_create_tracker(args: argparse.Namespace) -> dict[str, Any] | None:
    tracker_status = tracker_status_from_input(args.status)
    if tracker_status not in TRACKER_STATUSES:
        return None
    if not args.pr:
        return None
    if tracker_status not in {"open", "draft", "blocked", "deferred"} and not args.create_tracker_if_missing:
        return None
    now = utc_now_iso()
    return {
        "repo": normalize_repo(args.repo),
        "issue": args.issue,
        "pr": args.pr,
        "status": tracker_status,
        "author": args.author,
        "lane": args.lane,
        "title": args.title,
        "url": args.url,
        "created_at": now,
        "last_checked_at": now,
        "status_reason": args.reason,
    }


def main() -> int:
    args = parse_args()
    repo = normalize_repo(args.repo)
    if not args.queue and not args.tracker:
        raise SystemExit("at least one of --queue or --tracker is required")
    if args.status not in QUEUE_ALLOWED and tracker_status_from_input(args.status) not in TRACKER_STATUSES:
        raise SystemExit(f"unsupported status: {args.status}")
    if args.issue is None and args.pr is None:
        raise SystemExit("at least one of --issue or --pr is required")

    lock_path = Path(args.lock) if args.lock else None

    class NullContext:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc, tb):
            return False

    context = file_lock(lock_path) if lock_path else NullContext()

    with context:
        updated_queue = []
        updated_tracker = []

        if args.queue:
            queue_path = Path(args.queue)
            queue = load_json(queue_path, default=[])
            if not isinstance(queue, list):
                raise SystemExit("queue file must contain a JSON array")
            for item in queue:
                if not isinstance(item, dict):
                    continue
                if item.get("repo") != repo or args.issue is None or item.get("issue") != args.issue:
                    continue
                update_queue_item(item, args)
                updated_queue.append(item)
            save_json(queue_path, queue)

        if args.tracker:
            tracker_path = Path(args.tracker)
            tracker = load_json(tracker_path, default=[])
            if not isinstance(tracker, list):
                raise SystemExit("tracker file must contain a JSON array")
            for item in tracker:
                if not isinstance(item, dict):
                    continue
                if item.get("repo") != repo:
                    continue
                if args.pr is not None and item.get("pr") == args.pr:
                    update_tracker_item(item, args)
                    updated_tracker.append(item)
                elif args.pr is None and args.issue is not None and item.get("issue") == args.issue:
                    update_tracker_item(item, args)
                    updated_tracker.append(item)
            if not updated_tracker:
                created = maybe_create_tracker(args)
                if created and args.create_tracker_if_missing:
                    tracker.append(created)
                    updated_tracker.append(created)
            save_json(tracker_path, tracker)

    print_json(
        {
            "ok": True,
            "repo": repo,
            "issue": args.issue,
            "pr": args.pr,
            "status": args.status,
            "updated_queue_count": len(updated_queue),
            "updated_tracker_count": len(updated_tracker),
            "updated_queue": updated_queue,
            "updated_tracker": updated_tracker,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

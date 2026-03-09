#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import gh_json, issue_key, load_json, normalize_repo, print_json, save_json, utc_now_iso


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refill an OSS PR issue queue from gh search results.")
    parser.add_argument("--queue", required=True, help="Path to queue JSON file")
    parser.add_argument("--tracker", required=True, help="Path to tracker JSON file")
    parser.add_argument("--label", action="append", default=[], help="GitHub issue label to require")
    parser.add_argument("--language", action="append", default=[], help="Language filter for gh search")
    parser.add_argument("--repo", action="append", default=[], help="Restrict search to one or more repos")
    parser.add_argument("--query", default="", help="Raw search query text")
    parser.add_argument("--limit", type=int, default=20, help="Maximum search results to inspect")
    parser.add_argument("--sort", default="updated", help="gh search sort key")
    parser.add_argument("--source-file", help="Optional JSON file containing pre-fetched gh search issue results")
    parser.add_argument("--dry-run", action="store_true", help="Do not write queue changes")
    return parser.parse_args()


def build_search_results(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.source_file:
        return load_json(Path(args.source_file), default=[])

    cmd = [
        "search",
        "issues",
        args.query,
        "--state",
        "open",
        "--limit",
        str(args.limit),
        "--sort",
        args.sort,
        "--json",
        "number,title,url,updatedAt,repository,labels,assignees",
    ]
    for label in args.label:
        cmd.extend(["--label", label])
    for language in args.language:
        cmd.extend(["--language", language])
    for repo in args.repo:
        cmd.extend(["--repo", repo])
    return gh_json(cmd) or []


def repo_from_result(result: dict[str, Any]) -> str:
    repository = result.get("repository") or {}
    name_with_owner = repository.get("nameWithOwner")
    if isinstance(name_with_owner, str) and name_with_owner.count("/") == 1:
        return normalize_repo(name_with_owner)
    owner = repository.get("owner") or {}
    owner_login = owner.get("login")
    name = repository.get("name")
    return normalize_repo(f"{owner_login}/{name}")


def main() -> int:
    args = parse_args()
    queue_path = Path(args.queue)
    tracker_path = Path(args.tracker)

    queue = load_json(queue_path, default=[])
    tracker = load_json(tracker_path, default=[])
    if not isinstance(queue, list):
        raise SystemExit("queue file must contain a JSON array")
    if not isinstance(tracker, list):
        raise SystemExit("tracker file must contain a JSON array")

    seen_issue_keys = set()
    for item in queue:
        if isinstance(item, dict) and item.get("repo") and item.get("issue"):
            try:
                seen_issue_keys.add(issue_key(item["repo"], int(item["issue"])))
            except Exception:
                pass
    for item in tracker:
        if isinstance(item, dict) and item.get("repo") and item.get("issue"):
            try:
                seen_issue_keys.add(issue_key(item["repo"], int(item["issue"])))
            except Exception:
                pass

    results = build_search_results(args)
    added: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    now = utc_now_iso()

    for result in results:
        repo = repo_from_result(result)
        issue_number = int(result["number"])
        key = issue_key(repo, issue_number)
        if key in seen_issue_keys:
            skipped.append({"repo": repo, "issue": issue_number, "reason": "already in queue_or_tracker"})
            continue

        candidate = {
            "repo": repo,
            "issue": issue_number,
            "title": result.get("title"),
            "url": result.get("url"),
            "status": "queued",
            "priority": "normal",
            "claimed_by": None,
            "claimed_at": None,
            "source": "gh-search",
            "created_at": now,
            "updated_at": result.get("updatedAt"),
            "labels": [label.get("name") for label in (result.get("labels") or []) if isinstance(label, dict) and label.get("name")],
            "discovery": {
                "query": args.query,
                "labels": args.label,
                "languages": args.language,
                "repos": args.repo,
                "sort": args.sort,
            },
        }
        queue.append(candidate)
        added.append({"repo": repo, "issue": issue_number, "title": result.get("title")})
        seen_issue_keys.add(key)

    if not args.dry_run:
        save_json(queue_path, queue)

    print_json(
        {
            "ok": True,
            "dry_run": args.dry_run,
            "queue_path": str(queue_path),
            "added_count": len(added),
            "skipped_count": len(skipped),
            "added": added,
            "skipped": skipped,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

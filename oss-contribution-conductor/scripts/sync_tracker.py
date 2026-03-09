#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import TRACKER_STATUSES, gh_json, load_json, normalize_repo, print_json, save_json, summarize_status_rollup, utc_now_iso


ACTIVE_STATUSES = {"open", "draft", "blocked"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync tracker entries against live GitHub PR state.")
    parser.add_argument("--tracker", required=True, help="Path to tracker JSON file")
    parser.add_argument("--repo", action="append", default=[], help="Restrict sync to one or more repos")
    parser.add_argument("--include-closed", action="store_true", help="Also refresh merged/closed entries")
    parser.add_argument("--dry-run", action="store_true", help="Do not write tracker changes")
    return parser.parse_args()


def map_tracker_status(view: dict[str, Any]) -> str:
    state = str(view.get("state") or "").upper()
    is_draft = bool(view.get("isDraft"))
    if state == "MERGED":
        return "merged"
    if state == "CLOSED":
        return "closed"
    if is_draft:
        return "draft"
    return "open"


def build_attention(status: str, review_decision: str | None, ci_summary: dict[str, int]) -> list[str]:
    attention: list[str] = []
    if status in {"open", "draft", "blocked"} and review_decision == "CHANGES_REQUESTED":
        attention.append("unresolved_review_feedback")
    if status in {"open", "draft", "blocked"} and ci_summary.get("failure", 0) > 0:
        attention.append("failing_ci")
    if status in {"open", "draft", "blocked"} and ci_summary.get("pending", 0) > 0:
        attention.append("pending_ci")
    return attention


def main() -> int:
    args = parse_args()
    tracker_path = Path(args.tracker)
    tracker = load_json(tracker_path, default=[])
    if not isinstance(tracker, list):
        raise SystemExit("tracker file must contain a JSON array")

    repo_filter = {normalize_repo(repo) for repo in args.repo}
    changed: list[dict[str, Any]] = []
    checked_count = 0

    for item in tracker:
        if not isinstance(item, dict):
            continue
        repo = item.get("repo")
        pr = item.get("pr")
        status = item.get("status")
        if not isinstance(repo, str) or not isinstance(pr, int):
            continue
        if repo_filter and repo not in repo_filter:
            continue
        if status not in TRACKER_STATUSES:
            continue
        if not args.include_closed and status not in ACTIVE_STATUSES:
            continue

        view = gh_json(
            [
                "pr",
                "view",
                str(pr),
                "--repo",
                repo,
                "--json",
                "number,title,state,isDraft,reviewDecision,mergeStateStatus,statusCheckRollup,url,updatedAt",
            ]
        )
        checked_count += 1

        ci_summary = summarize_status_rollup(view.get("statusCheckRollup"))
        new_status = map_tracker_status(view)
        review_decision = view.get("reviewDecision")
        attention = build_attention(new_status, review_decision, ci_summary)
        before = {
            "status": item.get("status"),
            "review_decision": item.get("review_decision"),
            "ci": item.get("ci"),
            "attention": item.get("attention"),
        }

        item["title"] = view.get("title") or item.get("title")
        item["url"] = view.get("url") or item.get("url")
        item["status"] = new_status
        item["review_decision"] = review_decision
        item["merge_state_status"] = view.get("mergeStateStatus")
        item["github_updated_at"] = view.get("updatedAt")
        item["last_checked_at"] = utc_now_iso()
        item["ci"] = ci_summary
        item["attention"] = attention

        after = {
            "status": item.get("status"),
            "review_decision": item.get("review_decision"),
            "ci": item.get("ci"),
            "attention": item.get("attention"),
        }
        if before != after:
            changed.append({"repo": repo, "pr": pr, "before": before, "after": after})

    if not args.dry_run:
        save_json(tracker_path, tracker)

    print_json(
        {
            "ok": True,
            "dry_run": args.dry_run,
            "tracker_path": str(tracker_path),
            "checked_count": checked_count,
            "changed_count": len(changed),
            "changed": changed,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import file_lock, load_json, print_json, save_json, utc_now_iso


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Claim the next queued OSS issue safely.")
    parser.add_argument("--queue", required=True, help="Path to queue JSON file")
    parser.add_argument("--lane", required=True, help="Lane name claiming work, e.g. opener-a")
    parser.add_argument("--lock", required=True, help="Path to lock file")
    parser.add_argument("--stale-seconds", type=int, default=1800, help="Treat older lock files as stale")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    queue_path = Path(args.queue)
    lock_path = Path(args.lock)

    with file_lock(lock_path, stale_seconds=args.stale_seconds):
        queue = load_json(queue_path, default=[])
        if not isinstance(queue, list):
            raise SystemExit("queue file must contain a JSON array")

        claimed = None
        for item in queue:
            if not isinstance(item, dict):
                continue
            if item.get("status") != "queued":
                continue
            if item.get("claimed_by"):
                continue
            item["status"] = "claimed"
            item["claimed_by"] = args.lane
            item["claimed_at"] = utc_now_iso()
            claimed = item
            break

        if claimed is not None:
            save_json(queue_path, queue)
            print_json({"ok": True, "claimed": True, "item": claimed})
            return 0

    print_json({"ok": True, "claimed": False, "item": None})
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = shutil.which("python3") or sys.executable
SCRIPTS_DIR = ROOT / "oss-contribution-conductor" / "scripts"
EXAMPLES_DIR = ROOT / "examples" / "demo-state"
FIXTURES_DIR = ROOT / "tests" / "fixtures"


def run_python(script: Path, *args: object, expected_returncode: int = 0) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [PYTHON, str(script), *[str(arg) for arg in args]],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if completed.returncode != expected_returncode:
        raise AssertionError(
            f"expected exit {expected_returncode}, got {completed.returncode}\n"
            f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return completed


class ScriptCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def copy_example_state(self) -> tuple[Path, Path]:
        queue_path = self.tmp / "queue.json"
        tracker_path = self.tmp / "tracker.json"
        shutil.copy2(EXAMPLES_DIR / "queue.sample.json", queue_path)
        shutil.copy2(EXAMPLES_DIR / "tracker.sample.json", tracker_path)
        return queue_path, tracker_path

    def load_json(self, path: Path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_example_state_validates_cleanly(self) -> None:
        completed = run_python(
            SCRIPTS_DIR / "validate_state.py",
            "--queue",
            EXAMPLES_DIR / "queue.sample.json",
            "--tracker",
            EXAMPLES_DIR / "tracker.sample.json",
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["errors"], [])

    def test_claim_next_claims_first_queued_item(self) -> None:
        queue_path, _ = self.copy_example_state()
        lock_path = self.tmp / "claim.lock"

        completed = run_python(
            SCRIPTS_DIR / "claim_next.py",
            "--queue",
            queue_path,
            "--lane",
            "opener-a",
            "--lock",
            lock_path,
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["claimed"])
        self.assertEqual(payload["item"]["issue"], 42)
        self.assertEqual(payload["item"]["claimed_by"], "opener-a")

        queue = self.load_json(queue_path)
        self.assertEqual(queue[0]["status"], "claimed")
        self.assertEqual(queue[0]["claimed_by"], "opener-a")
        self.assertEqual(queue[1]["status"], "opened")

    def test_refill_queue_uses_source_file_and_dedupes_existing_entries(self) -> None:
        queue_path, tracker_path = self.copy_example_state()

        completed = run_python(
            SCRIPTS_DIR / "refill_queue.py",
            "--queue",
            queue_path,
            "--tracker",
            tracker_path,
            "--source-file",
            FIXTURES_DIR / "gh-search.sample.json",
            "--query",
            "label:documentation",
            "--limit",
            "10",
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["added_count"], 1)
        self.assertEqual(payload["skipped_count"], 2)
        self.assertEqual(payload["added"][0]["issue"], 99)

        queue = self.load_json(queue_path)
        self.assertEqual([item["issue"] for item in queue], [42, 77, 99])
        self.assertEqual(queue[-1]["status"], "queued")
        self.assertEqual(queue[-1]["repo"], "example/project")

    def test_update_item_status_can_open_issue_and_create_tracker(self) -> None:
        queue_path, tracker_path = self.copy_example_state()
        lock_path = self.tmp / "update.lock"

        completed = run_python(
            SCRIPTS_DIR / "update_item_status.py",
            "--queue",
            queue_path,
            "--tracker",
            tracker_path,
            "--lock",
            lock_path,
            "--repo",
            "example/project",
            "--issue",
            "42",
            "--pr",
            "88",
            "--status",
            "opened",
            "--lane",
            "opener-b",
            "--author",
            "octocat",
            "--title",
            "Fix sidebar stale active state",
            "--url",
            "https://github.com/example/project/pull/88",
            "--reason",
            "opened clean follow-up PR",
            "--create-tracker-if-missing",
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["updated_queue_count"], 1)
        self.assertEqual(payload["updated_tracker_count"], 1)

        queue = self.load_json(queue_path)
        updated_queue_item = next(item for item in queue if item["issue"] == 42)
        self.assertEqual(updated_queue_item["status"], "opened")
        self.assertEqual(updated_queue_item["opened_pr"], 88)
        self.assertIsNone(updated_queue_item["claimed_by"])

        tracker = self.load_json(tracker_path)
        created_tracker_item = next(item for item in tracker if item["pr"] == 88)
        self.assertEqual(created_tracker_item["status"], "open")
        self.assertEqual(created_tracker_item["issue"], 42)
        self.assertEqual(created_tracker_item["lane"], "opener-b")

    def test_render_pr_body_includes_exact_validation_commands(self) -> None:
        completed = run_python(
            SCRIPTS_DIR / "render_pr_body.py",
            "--issue",
            "123",
            "--problem",
            "The docs still mention an old flag name.",
            "--fix",
            "Update the docs to use the current flag and examples.",
            "--validation",
            "git diff --check",
            "--validation",
            "python3 -m py_compile docs/build_docs.py",
        )
        body = completed.stdout
        self.assertIn("Closes #123", body)
        self.assertIn("- `git diff --check`", body)
        self.assertIn("- `python3 -m py_compile docs/build_docs.py`", body)
        self.assertIn("Do not tick or claim any validation you did not actually run.", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)

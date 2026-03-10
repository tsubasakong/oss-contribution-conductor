#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = Path(__file__).resolve().parent
BOX_W = 60


def box_line(text: str) -> str:
    return f"║{text.ljust(BOX_W)}║"


def main() -> int:
    print("╔" + "═" * BOX_W + "╗")
    print(box_line("        OSS Contribution Conductor - Smoke Test Suite"))
    print("╚" + "═" * BOX_W + "╝")
    print()

    loader = unittest.defaultTestLoader
    suite = loader.discover(str(TESTS_DIR), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    total = result.testsRun
    failed = len(result.failures) + len(result.errors)
    passed = total - failed

    print()
    print("╔" + "═" * BOX_W + "╗")
    print(box_line("                        Final Results"))
    print("╠" + "═" * BOX_W + "╣")
    print(box_line(f"  Total Tests: {total:>4}"))
    print(box_line(f"  Passed:      {passed:>4}  ✓"))
    print(box_line(f"  Failed:      {failed:>4}  {'✗' if failed else ' '}"))
    print("╚" + "═" * BOX_W + "╝")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a maintainer-friendly starter PR body.")
    parser.add_argument("--issue", type=int, help="Issue number to link")
    parser.add_argument("--link-keyword", default="Closes", help="Keyword to link the issue, e.g. Closes or Fixes")
    parser.add_argument("--problem", required=True, help="Short problem summary")
    parser.add_argument("--fix", required=True, help="Short fix summary")
    parser.add_argument("--validation", action="append", default=[], help="Exact validation command or note; repeatable")
    parser.add_argument("--output", help="Optional output file path")
    return parser.parse_args()


def render_body(args: argparse.Namespace) -> str:
    lines: list[str] = []
    if args.issue:
        lines.append(f"{args.link_keyword} #{args.issue}")
        lines.append("")

    lines.extend(
        [
            "## Summary",
            f"- {args.problem}",
            f"- {args.fix}",
            "",
            "## Validation",
        ]
    )

    if args.validation:
        for check in args.validation:
            lines.append(f"- `{check}`")
    else:
        lines.append("- Not run yet — replace this with the exact validation you actually performed before opening the PR.")

    lines.extend(
        [
            "",
            "## Notes",
            "- Adapt this starter body to the repository's exact PR template before submitting.",
            "- Do not tick or claim any validation you did not actually run.",
            "",
            "## Checklist",
            "- [x] I kept the change scoped to the reported issue.",
            "- [ ] I have tested my changes locally.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    body = render_body(args)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(body, encoding="utf-8")
    else:
        print(body, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Validate commit messages against the 50/72 rule.

- Subject (first line of the message Git will keep): at most 50 characters.
- Every following line: at most 72 characters.

Lines that Git treats as comments (optional leading whitespace, then '#') are
ignored, matching what Git strips from the final message.

Usage (Git commit-msg hook):
    5072.py "$1"

Usage (pre-commit framework, .pre-commit-config.yaml):
    entry: python 5072.py
    language: system
    stages: [commit-msg]
    always_run: true
"""

from __future__ import annotations

import sys
from pathlib import Path


SUBJECT_MAX = 50
BODY_LINE_MAX = 72


def _strip_comment_lines(text: str) -> str:
    """Remove lines Git would drop as comments (leading ws + '#')."""
    kept: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        kept.append(line)
    return "\n".join(kept).strip("\n")


def validate_commit_message(text: str) -> list[str]:
    """
    Return a list of human-readable errors; empty means valid.
    """
    errors: list[str] = []
    cleaned = _strip_comment_lines(text).rstrip("\n")

    if not cleaned.strip():
        return errors

    lines = cleaned.split("\n")
    subject = lines[0]

    if len(subject) > SUBJECT_MAX:
        errors.append(
            f"Subject line is {len(subject)} characters; maximum is {SUBJECT_MAX}.\n"
            f"  {subject}"
        )

    for i, line in enumerate(lines[1:], start=2):
        if len(line) > BODY_LINE_MAX:
            errors.append(
                f"Line {i} is {len(line)} characters; maximum is {BODY_LINE_MAX}.\n"
                f"  {line}"
            )

    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "commit-msg hook: pass the path to the commit message file as argv[1].",
            file=sys.stderr,
        )
        return 1

    path = Path(sys.argv[1])
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Cannot read commit message file {path}: {exc}", file=sys.stderr)
        return 1

    errors = validate_commit_message(raw)
    if errors:
        print("Commit message does not follow the 50/72 rule:\n", file=sys.stderr)
        for msg in errors:
            print(msg, file=sys.stderr)
            print(file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

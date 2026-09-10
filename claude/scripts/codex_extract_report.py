#!/usr/bin/env python3
"""Extract the final answer from a `codex review` stream log.

`codex review` has no output flag, so the wrapper tees the stream and keeps
everything after the last marker line the CLI prints before its final message.
Two things make that fragile, and both have bitten us:

1. The CLI started colouring that marker line on 2026-09-10
   (``\x1b[35m\x1b[3mcodex\x1b[0m\x1b[0m``). A bare ``^codex$`` match stopped
   matching, so twelve review reports in a row were written empty while the
   wrapper still reported "saved" -- the report only survived in the raw
   stream log.
2. The CLI prints that final message twice (once streamed, once as the
   result), so an exactly doubled half has to be collapsed.

Kept out of the shell script so it can be tested; see
scripts/test_codex_extract_report.py.
"""
import re
import sys

# Any SGR escape (colour, italics, reset). The stream log keeps them; the
# report should not.
ANSI = re.compile(r"\x1b\[[0-9;]*m")

MARKER = "codex"


def strip_ansi(text: str) -> str:
    return ANSI.sub("", text)


def collapse_doubled(lines: list[str]) -> list[str]:
    """Drop the second copy when the block is printed twice in a row."""
    for i, line in enumerate(lines):
        if i and line == lines[0]:
            return lines[:i]
    return lines


def extract(stream: str) -> str:
    """Return the text after the LAST marker line, doubling collapsed."""
    kept: list[str] = []
    seen_marker = False
    for line in strip_ansi(stream).split("\n"):
        if line.rstrip() == MARKER:
            kept = []
            seen_marker = True
            continue
        if seen_marker:
            kept.append(line)
    while kept and not kept[-1].strip():
        kept.pop()
    if not kept:
        return ""
    return "\n".join(collapse_doubled(kept)).rstrip("\n")


def main() -> int:
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8", errors="replace") as handle:
            stream = handle.read()
    else:
        stream = sys.stdin.read()
    report = extract(stream)
    if not report:
        return 1
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())

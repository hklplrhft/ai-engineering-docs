#!/usr/bin/env python3
"""Tests for the Codex report extractor.

Regression: on 2026-09-10 the Codex CLI started colouring the marker line, the
shell one-liner that cut the report stopped matching, and twelve review reports
were written empty while the wrapper still said "saved".

Run: python3 scripts/test_codex_extract_report.py
  or: python3 -m unittest scripts.test_codex_extract_report
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from codex_extract_report import extract, strip_ansi  # noqa: E402

# The exact shape the CLI writes since 2026-09-10 (magenta + italic + two
# resets), copied from logs/codex/20260910-191646-57220-review.stream.log.
COLOURED_MARKER = "\x1b[35m\x1b[3mcodex\x1b[0m\x1b[0m"


class ExtractTests(unittest.TestCase):
    def test_plain_marker(self):
        stream = "thinking out loud\ncodex\nNo findings above P3.\n"
        self.assertEqual(extract(stream), "No findings above P3.")

    def test_coloured_marker(self):
        stream = f"diff context\n{COLOURED_MARKER}\nP2 in main_screen.dart:41\n"
        self.assertEqual(extract(stream), "P2 in main_screen.dart:41")

    def test_doubled_final_message_is_collapsed(self):
        answer = "No findings above P3."
        stream = f"noise\n{COLOURED_MARKER}\n{answer}\n{answer}\n"
        self.assertEqual(extract(stream), answer)

    def test_doubled_multiline_block_is_collapsed(self):
        block = "P1 file.dart:10\nreason\n"
        stream = f"{COLOURED_MARKER}\n{block}{block}"
        self.assertEqual(extract(stream), "P1 file.dart:10\nreason")

    def test_last_marker_wins(self):
        stream = f"{COLOURED_MARKER}\nfirst pass\n{COLOURED_MARKER}\nfinal answer\n"
        self.assertEqual(extract(stream), "final answer")

    def test_no_marker_gives_empty(self):
        # The wrapper turns this into a hard failure instead of a 1-byte file.
        self.assertEqual(extract("only progress lines\n"), "")

    def test_marker_only_gives_empty(self):
        self.assertEqual(extract(f"{COLOURED_MARKER}\n\n"), "")

    def test_indented_codex_line_is_not_a_marker(self):
        # A quoted diff line may say 'codex'; only a line of its own counts.
        stream = f"{COLOURED_MARKER}\nsee    codex here\nand more\n"
        self.assertEqual(extract(stream), "see    codex here\nand more")

    def test_strip_ansi_leaves_text(self):
        self.assertEqual(strip_ansi("\x1b[31mred\x1b[0m text"), "red text")


if __name__ == "__main__":
    unittest.main()

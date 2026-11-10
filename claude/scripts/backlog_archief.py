#!/usr/bin/env python3
"""Move ticked items from Hans' topic files in ~/Development/_backlogs to an archive per topic.

Plan: docs/plans/2026-11-10-backlog-archief.md. Rule (Hans, 10 Nov 2026): ticked items in the topic files
(`~/Development/_backlogs/<repo>/<onderwerp>.md`) may move to `<repo>/archief/<onderwerp>.md`, only with this script.

  python3 -I claude/scripts/backlog_archief.py dryrun OUTDIR FILE...   compute, write copies into OUTDIR only
  python3 -I claude/scripts/backlog_archief.py write FILE...           append to the archive, rewrite the topic file

What moves: a top-level item `- [x] ...` with its continuation lines (indented lines up to a blank line, the next
`- ` item or a heading). What stays: open items, ticked sub-items under an open item, a ticked item that still has an
open sub-item, and all other text (WAAR, STAND, headings, intros). A file with a line the script cannot place (text
at column 0 directly under a ticked item) is skipped as a whole.

Safety: the archive is only appended to (created exclusively). The topic file is replaced only when the archived
items read back exactly once from the archive and the topic file has not changed since it was read; otherwise the
file is left alone and a rerun finishes the job (an item already in the archive is not appended again, checked per
item). After each write the script checks that every open item (any list marker) is still there, in the same order,
and that every removed line is in the archive. A lock stops two runs of this script at once.
"""
import datetime
import fcntl
import os
import re
import sys
import tempfile

BACKLOGS = os.path.realpath(os.environ.get("BACKLOGS_DIR", os.path.expanduser("~/Development/_backlogs")))
TICKED = re.compile(r"^- \[[xX]\] ")
OPEN = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\[ \]")  # any list marker (Codex, 10 Nov 2026)
HEADING = re.compile(r"^#{1,6} ")
NO_HEADING = "(zonder kop, onder OPEN PUNTEN)"


class Skip(Exception):
    """The file cannot be handled safely; nothing is written for it."""


def split(text):
    """(new_text, items, kept) where items is a list of (heading, lines) to archive and kept the first lines of
    ticked items that stay because they have an open sub-item."""
    lines = text.split("\n")
    drop, items, kept = set(), [], []
    heading = NO_HEADING
    i = 0
    while i < len(lines):
        line = lines[i]
        if HEADING.match(line):
            heading = line
        if not TICKED.match(line):
            i += 1
            continue
        j = i + 1
        while True:
            while j < len(lines) and lines[j].strip() and not lines[j].startswith("- ") and not HEADING.match(lines[j]):
                if not lines[j][0].isspace():
                    raise Skip(f"line {j + 1} is text at column 0 directly under a ticked item")
                j += 1
            k = j
            while k < len(lines) and not lines[k].strip():
                k += 1
            if j < k < len(lines) and lines[k][0].isspace():
                j = k  # an indented line after blank lines still belongs to the item (Codex, 10 Nov 2026)
                continue
            break
        block = lines[i:j]
        if any(OPEN.match(l) for l in block[1:]):
            kept.append(line)
        else:
            items.append((heading, block))
            drop.update(range(i, j))
            # One blank line goes with the item when it stood between blank lines, so the list keeps one blank line
            # between items and paragraphs never merge. `k` is the nearest line before it that stays.
            k = i - 1
            while k >= 0 and k in drop:
                k -= 1
            before_blank = k < 0 or not lines[k].strip()
            at_end = all(not l.strip() for l in lines[j:])
            if before_blank and at_end and k >= 0:
                drop.add(k)  # last item of the file: drop the blank line above it, keep the final newline
            elif before_blank and j < len(lines) - 1 and not lines[j].strip():
                drop.add(j)
                j += 1
        i = j
    new = "\n".join(l for k, l in enumerate(lines) if k not in drop)
    return new, items, kept


def render(items):
    """Archive text for the items, grouped under the heading they stood under; deterministic for rerun detection."""
    out, last = [], None
    for heading, block in items:
        if heading != last:
            out.append(heading)
            out.append("")
            last = heading
        out.extend(block)
        out.append("")
    return "\n".join(out)


def archive_path(path):
    d, name = os.path.split(path)
    return os.path.join(d, "archief", name)


def check_path(path):
    real = os.path.realpath(path)
    rel = os.path.relpath(real, BACKLOGS)
    parts = rel.split(os.sep)
    if rel.startswith("..") or len(parts) != 2 or not parts[1].endswith(".md") or parts[0] == "archief":
        raise Skip(f"not a topic file <repo>/<onderwerp>.md under {BACKLOGS}")
    return real


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def open_lines(text):
    return [l for l in text.split("\n") if OPEN.match(l)]


def atomic_write(path, text):
    tmp = os.path.join(os.path.dirname(path), "." + os.path.basename(path) + ".tmp-archief")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.chmod(tmp, os.stat(path).st_mode & 0o777)
    os.replace(tmp, path)


def replace_if_unchanged(path, old, new):
    """Replace the topic file with `new` only while it still holds `old`. A hard link pins the file that is replaced,
    so a writer that changes it in place between the check and the replace is noticed afterwards and its version is
    put back (Codex, 10 Nov 2026). A writer that swaps in a new file by rename in that same instant is not seen; the
    window is a few microseconds."""
    d, base = os.path.split(path)
    pin, tmp = os.path.join(d, "." + base + ".pin-archief"), os.path.join(d, "." + base + ".tmp-archief")
    for leftover in (pin, tmp):
        if os.path.exists(leftover):
            os.unlink(leftover)
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(new)
    os.chmod(tmp, os.stat(path).st_mode & 0o777)
    os.link(path, pin)
    try:
        if read(pin) != old:
            raise Skip("topic file changed during the run; left alone (the items are in the archive, run again)")
        os.replace(tmp, path)
        late = read(pin)
    finally:
        for leftover in (pin, tmp):
            if os.path.exists(leftover):
                os.unlink(leftover)
    if late != old:
        if read(path) == new:
            atomic_write(path, late)
        raise Skip("topic file changed just before the replace; its latest version is back in place, run again")


def header(path, today):
    repo, name = os.path.relpath(path, BACKLOGS).split(os.sep)
    return (f"Archief van {repo}/{name}: afgevinkte punten, verplaatst met "
            f"ai-engineering-docs/claude/scripts/backlog_archief.py (regel Hans {today}). Alleen aanvullen.\n")


def present(archive, block):
    """True when the item (all its lines, as a whole) is already in the archive text."""
    return ("\n" + "\n".join(block) + "\n") in ("\n" + archive + "\n")


def write_one(path, today):
    old = read(path)
    new, items, kept = split(old)
    if not items:
        return f"nothing to archive ({len(kept)} kept)"
    arch = archive_path(path)
    os.makedirs(os.path.dirname(arch), exist_ok=True)
    if not os.path.exists(arch):
        try:
            with open(arch, "x", encoding="utf-8") as f:
                f.write(header(path, today))
        except FileExistsError:
            pass
    current = read(arch)
    # per item, so a rerun after a crash never archives an item twice, also when more items were ticked meanwhile
    fresh = [(h, b) for h, b in items if not present(current, b)]
    if fresh:
        with open(arch, "a", encoding="utf-8") as f:  # append only
            f.write(("\n" if current.endswith("\n") else "\n\n") + f"Gearchiveerd op {today} ({len(fresh)} punten):\n\n"
                    + render(fresh))
    stored = read(arch)
    if not all(present(stored, b) for _, b in items):
        raise Skip(f"archive {arch} does not hold every item; topic file left alone, check by hand")
    replace_if_unchanged(path, old, new)
    after = read(path)
    if open_lines(after) != open_lines(old):
        raise Skip("CHECK FAILED: open items differ after the write; compare with the archive and git")
    gone = [l for l in old.split("\n") if l.strip() and l not in after.split("\n")]
    missing = [l for l in gone if l not in read(arch).split("\n")]
    if missing:
        raise Skip(f"CHECK FAILED: {len(missing)} removed line(s) not in the archive")
    return f"archived {len(items)} ({len(old.splitlines())} -> {len(after.splitlines())} lines, {len(kept)} kept)"


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("dryrun", "write"):
        sys.exit(__doc__)
    mode = sys.argv[1]
    outdir = sys.argv[2] if mode == "dryrun" else None
    if outdir:
        out = os.path.realpath(outdir)
        if out == BACKLOGS or out.startswith(BACKLOGS + os.sep) or BACKLOGS.startswith(out + os.sep):
            sys.exit("STOP: OUTDIR overlaps the backlogs folder; a dry run writes only outside it")
    files = sys.argv[3:] if mode == "dryrun" else sys.argv[2:]
    lock = open(os.path.join(tempfile.gettempdir(), "backlog-archief.lock"), "a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.exit("STOP: another run is busy; nothing written")
    today = datetime.date.today().isoformat()
    failed = 0
    for f in files:
        try:
            path = check_path(f)
            rel = os.path.relpath(path, BACKLOGS)
            if mode == "dryrun":
                old = read(path)
                new, items, kept = split(old)
                dest = os.path.join(outdir, rel)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, "w", encoding="utf-8") as fh:
                    fh.write(new)
                if items:
                    adest = os.path.join(outdir, os.path.dirname(rel), "archief", os.path.basename(rel))
                    os.makedirs(os.path.dirname(adest), exist_ok=True)
                    with open(adest, "w", encoding="utf-8") as fh:
                        fh.write(header(path, today) + f"\nGearchiveerd op {today} ({len(items)} punten):\n\n" + render(items))
                assert open_lines(new) == open_lines(old)
                print(f"{rel:40s} {len(items):3d} to archive, {len(kept)} kept, "
                      f"{len(old.splitlines())} -> {len(new.splitlines())} lines, open {len(open_lines(old))}")
            else:
                print(f"{rel:40s} {write_one(path, today)}")
        except Skip as e:
            failed += 1
            print(f"{f}: SKIPPED: {e}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

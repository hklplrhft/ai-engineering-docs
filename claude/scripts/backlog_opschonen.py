#!/usr/bin/env python3
"""Remove ticked items from Hans' topic files in ~/Development/_backlogs (team repos), the way the team does in TODO.md.

Plan: docs/plans/2026-11-10-backlog-archief.md (v3). Rule (Hans, 10 Nov 2026): a finished item in a topic file
`~/Development/_backlogs/<repo>/<onderwerp>.md` first gets a clear line in the CHANGELOG of the team repo (what, when,
evidence; no customer data); then the ticked item may go, only with this script. The full text stays in the git
history of ~/Development/_backlogs (hourly snapshot), so the script only touches a file whose current content is
already committed there.

  python3 -I claude/scripts/backlog_opschonen.py dryrun OUTDIR FILE...   compute, write copies into OUTDIR only
  python3 -I claude/scripts/backlog_opschonen.py write FILE...           remove the ticked items

What goes: a top-level item `- [x] ...` with its continuation lines (indented lines, also after a blank line, up to
the next `- ` item, a heading or text at column 0). What stays: open items, ticked sub-items under an open item, a
ticked item that still has an open sub-item (any list marker), and all other text (WAAR, STAND, headings, intros).
A file with text at column 0 directly under a ticked item is skipped as a whole.

Safety: the file must be tracked and unchanged in the _backlogs git (else: wait for the next snapshot). It is replaced
only while it still holds what was read; a hard link pins the replaced file for a few seconds, so a writer that
changes it in place around the replace is noticed, its version saved outside _backlogs and, when safe, put back. Afterwards the script checks that every open item is still
there, in the same order, and that every removed line is in the committed version. A lock stops two runs at once.
"""
import fcntl
import os
import re
import subprocess
import sys
import tempfile
import time

BACKLOGS = os.path.realpath(os.environ.get("BACKLOGS_DIR", os.path.expanduser("~/Development/_backlogs")))
TICKED = re.compile(r"^- \[[xX]\] ")
OPEN = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+\[ \]")  # any list marker (Codex, 10 Nov 2026)
HEADING = re.compile(r"^#{1,6} ")
GRACE = float(os.environ.get("OPSCHONEN_GRACE", "2"))  # seconds the replaced file stays watched (Codex, 10 Nov 2026)
RESCUE = os.path.join(tempfile.gettempdir(), "backlog-opschonen-herstel")
pause = time.sleep  # the test replaces this to act as a writer during the grace period


class Skip(Exception):
    """The file cannot be handled safely; nothing is written for it."""


def split(text):
    """(new_text, items, kept): items are the removed blocks (lists of lines), kept the first lines of ticked items
    that stay because they still have an open sub-item."""
    lines = text.split("\n")
    drop, items, kept = set(), [], []
    i = 0
    while i < len(lines):
        line = lines[i]
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
        while block and not block[-1].strip():
            block.pop()
        if any(OPEN.match(l) for l in block[1:]):
            kept.append(line)
        else:
            items.append(block)
            drop.update(range(i, i + len(block)))
            j = i + len(block)
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


def check_path(path):
    real = os.path.realpath(path)
    rel = os.path.relpath(real, BACKLOGS)
    parts = rel.split(os.sep)
    if rel.startswith("..") or len(parts) != 2 or not parts[1].endswith(".md"):
        raise Skip(f"not a topic file <repo>/<onderwerp>.md under {BACKLOGS}")
    return real, rel


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def git(*args):
    return subprocess.run(["git", "-C", BACKLOGS, *args], check=True, capture_output=True, text=True).stdout


def committed(rel):
    """(commit, text) of the file as committed in the _backlogs git, or Skip when it is not committed as it is now.
    The commit that is reported is the one whose text is compared (Codex, 10 Nov 2026)."""
    if git("status", "--porcelain", "--", rel).strip():
        raise Skip("not yet in the _backlogs git as it is now; wait for the next hourly snapshot")
    commit = git("log", "-1", "--format=%H", "--", rel).strip()
    if not commit:
        raise Skip("not tracked in the _backlogs git")
    return commit[:8], git("show", f"{commit}:{rel}")


def open_lines(text):
    return [l for l in text.split("\n") if OPEN.match(l)]


def atomic_write(path, text):
    tmp = os.path.join(os.path.dirname(path), "." + os.path.basename(path) + ".tmp-opschonen")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.chmod(tmp, os.stat(path).st_mode & 0o777)
    os.replace(tmp, path)


def rescue(path, text):
    """Keep a copy outside _backlogs of a version that another writer made during the run."""
    os.makedirs(RESCUE, exist_ok=True)
    rel = os.path.relpath(path, BACKLOGS).replace(os.sep, "_")
    dest = os.path.join(RESCUE, f"{time.strftime('%Y%m%d-%H%M%S')}-{rel}")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(text)
    return dest


def replace_if_unchanged(path, old, new):
    """Replace the file with `new` only while it still holds `old`. A hard link pins the file that is replaced and
    stays for GRACE seconds, so a writer that changes it in place around the replace (also one that opened it before
    and writes just after) is noticed. Its version is then saved outside _backlogs and, if nobody wrote to the new
    file yet, put back (Codex, 10 Nov 2026). Not seen: a writer that swaps in a whole new file by rename in the same
    microseconds as the replace."""
    d, base = os.path.split(path)
    pin, tmp = os.path.join(d, "." + base + ".pin-opschonen"), os.path.join(d, "." + base + ".tmp-opschonen")
    for leftover in (pin, tmp):
        if os.path.exists(leftover):
            os.unlink(leftover)
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(new)
    os.chmod(tmp, os.stat(path).st_mode & 0o777)
    os.link(path, pin)
    try:
        if read(pin) != old:
            raise Skip("file changed during the run; left alone, run again")
        os.replace(tmp, path)
        pause(GRACE)
        late = read(pin)
    finally:
        for leftover in (pin, tmp):
            if os.path.exists(leftover):
                os.unlink(leftover)
    if late != old:
        saved = rescue(path, late)
        if read(path) == new:
            atomic_write(path, late)
            raise Skip(f"another writer changed the file during the replace; its version is back in place (copy: {saved}); run again")
        raise Skip(f"CHECK: two writers during the replace; the other version is saved at {saved}; merge by hand")


def write_one(path, rel):
    old = read(path)
    commit, in_git = committed(rel)
    if in_git != old:
        raise Skip("differs from the committed version; wait for the next hourly snapshot")
    new, items, kept = split(old)
    if not items:
        return f"nothing to remove ({len(kept)} kept)"
    replace_if_unchanged(path, old, new)
    after = read(path)
    if open_lines(after) != open_lines(old):
        raise Skip("CHECK FAILED: open items differ after the write; compare with git")
    saved = set(in_git.split("\n"))
    if any(l not in saved for b in items for l in b):
        raise Skip("CHECK FAILED: a removed line is not in the committed version")
    return (f"removed {len(items)} ({len(old.splitlines())} -> {len(after.splitlines())} lines, {len(kept)} kept); "
            f"full text: git -C {BACKLOGS} show {commit}:{rel}")


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
    lock = open(os.path.join(tempfile.gettempdir(), "backlog-opschonen.lock"), "a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        sys.exit("STOP: another run is busy; nothing written")
    failed = 0
    for f in files:
        try:
            path, rel = check_path(f)
            if mode == "dryrun":
                old = read(path)
                new, items, kept = split(old)
                try:
                    commit, _ = committed(rel)
                    state = f"in git ({commit})"
                except Skip as e:
                    state = f"NOT READY: {e}"
                dest = os.path.join(outdir, rel)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                real_dest = os.path.realpath(dest)
                if real_dest == BACKLOGS or real_dest.startswith(BACKLOGS + os.sep):
                    raise Skip("dry-run destination leads into the backlogs folder (symlink); nothing written")
                with open(dest, "w", encoding="utf-8") as fh:
                    fh.write(new)
                assert open_lines(new) == open_lines(old)
                print(f"{rel:36s} {len(items):3d} to remove, {len(kept)} kept, "
                      f"{len(old.splitlines())} -> {len(new.splitlines())} lines, open {len(open_lines(old))}; {state}")
            else:
                print(f"{rel:36s} {write_one(path, rel)}")
        except Skip as e:
            failed += 1
            print(f"{f}: SKIPPED: {e}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

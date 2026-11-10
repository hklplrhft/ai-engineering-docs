#!/bin/bash
# Tests for project-check.sh (SessionStart hook). Run: bash claude/hooks/test_project_check.sh
set -u
HOOK="$(cd "$(dirname "$0")" && pwd)/project-check.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
fail=0
check() { # check <description> <output> <expected substring>
  if printf '%s' "$2" | grep -qF -- "$3"; then echo "ok   $1"; else echo "FOUT $1: verwacht '$3' in: $2"; fail=1; fi
}
absent() { # absent <description> <output> <substring that must not be there>
  if printf '%s' "$2" | grep -qF -- "$3"; then echo "FOUT $1: '$3' hoort er niet in: $2"; fail=1; else echo "ok   $1"; fi
}
valid_json() {
  if [ -z "$2" ] || printf '%s' "$2" | python3 -I -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null; then echo "ok   $1"; else echo "FOUT $1: geen geldige JSON: $2"; fail=1; fi
}
run() { (cd "$1" && CLAUDE_NOTES_DIR="$TMP/notes" sh "$HOOK"); }

G="git -c user.name=t -c user.email=t@example.com -c commit.gpgsign=false"
mkdir -p "$TMP/Proj/docs/refs" "$TMP/Proj/docs/onderwerpen" "$TMP/notes" "$TMP/los"
cd "$TMP/Proj" || exit 1
$G init -q -b main
touch CLAUDE.md .gitignore TODO.md CHANGELOG.md docs/decisions.md docs/refs/.keep
printf 'Afspraken\n' > docs/onderwerpen/README.md
printf 'WAAR: x\nHERZIEN OP: 2000-01-01\nOPEN PUNTEN\n' > docs/onderwerpen/alfa.md
printf 'WAAR: y\nHERZIEN OP: 2999-01-01\n' > docs/onderwerpen/beta.md
$G add -A && $G commit -qm een
first=$(git rev-parse HEAD)
$G worktree add -q "$TMP/Proj-alfa" -b hans/alfa "$first"
$G worktree add -q "$TMP/Proj-gamma" -b hans/gamma "$first"
printf 'WAAR: z\n' > docs/onderwerpen/gamma.md
$G add -A && $G commit -qm twee
git update-ref refs/remotes/origin/main HEAD
touch "$TMP/notes/proj alfa.txt"

out=$(run "$TMP/Proj")
valid_json "hoofdmap: geldige JSON" "$out"
absent "hoofdmap: TODO.md telt als backlog" "$out" "BACKLOG.md ontbreekt"
absent "hoofdmap: git herkend" "$out" "Geen git repo"
check "hoofdmap: lijst van onderwerpen zonder README" "$out" "alfa, beta, gamma."
check "hoofdmap: over de HERZIEN OP-datum" "$out" "alfa (2000-01-01)"
absent "hoofdmap: datum in de toekomst niet gemeld" "$out" "beta (2999"
check "hoofdmap: onderwerpen zonder item in Notch" "$out" "melden aan Hans: beta, gamma."

out=$(run "$TMP/Proj-alfa")
valid_json "worktree: geldige JSON" "$out"
absent "worktree: git herkend (.git is daar een bestand)" "$out" "Geen git repo"
check "worktree: wijst het onderwerpbestand aan" "$out" "Onderwerp alfa: lees eerst docs/onderwerpen/alfa.md"
absent "worktree: geen lijst van de hoofdmap" "$out" "Onderwerpen in"

out=$(run "$TMP/Proj-gamma")
check "worktree achter op main: eerst mergen" "$out" "staat op origin/main maar nog niet in deze worktree; doe eerst git merge origin/main"

out=$(run "$TMP/los")
check "geen git: gemeld" "$out" "Geen git repo"
valid_json "geen git: geldige JSON" "$out"

rm -rf "$TMP/notes"
out=$(run "$TMP/Proj")
absent "zonder notitiemap: geen melding over Notch" "$out" "Notch"

if [ "$fail" = 0 ]; then echo "alle tests groen"; else echo "TESTS GEFAALD"; exit 1; fi

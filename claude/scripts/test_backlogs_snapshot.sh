#!/bin/bash
# Tests for backlogs-snapshot.sh. Run: bash claude/scripts/test_backlogs_snapshot.sh
# Uses a temporary folder with a local bare remote; never touches ~/Development/_backlogs or GitHub.
set -u
SCRIPT="$(cd "$(dirname "$0")" && pwd)/backlogs-snapshot.sh"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
fail=0
ok() { echo "ok   $1"; }
bad() { echo "FOUT $1"; fail=1; }

setup() { # fresh backlogs folder with a bare remote
  rm -rf "$TMP/remote.git" "$TMP/_backlogs"
  git init -q --bare "$TMP/remote.git"
  mkdir -p "$TMP/_backlogs/notities"
  cd "$TMP/_backlogs" || exit 1
  git init -q -b main
  git config user.name test; git config user.email test@example.com; git config commit.gpgsign false
  echo begin > notities/begin.txt
  git add -A && git commit -qm begin
  git remote add origin "$TMP/remote.git"
  git push -q -u origin main
}

# A git that, on its first push, writes a note into the folder: a change made while the job runs.
cat > "$TMP/git-wrapper" <<EOF
#!/bin/bash
if [ "\$1" = "push" ] && [ ! -f "$TMP/marker" ]; then
  touch "$TMP/marker"
  echo "tijdens de push" > "$TMP/_backlogs/notities/tijdens-push.txt"
fi
exec /usr/bin/git "\$@"
EOF
chmod +x "$TMP/git-wrapper"

run() { HOME="$TMP" BACKLOGS_DIR="$TMP/_backlogs" SNAPSHOT_QUIET=1 bash "$SCRIPT"; }

# 1. A change during the push is committed and pushed in a second round.
setup
echo nieuw > notities/nieuw.txt
out=$(SNAPSHOT_GIT="$TMP/git-wrapper" SNAPSHOT_GITLEAKS=/usr/bin/true run)
[ -z "$(git status --porcelain)" ] && ok "map is schoon na de run" || bad "map niet schoon: $(git status --porcelain)"
printf '%s' "$out" | grep -q "nog een ronde" && ok "tweede ronde gelogd" || bad "geen tweede ronde: $out"
files=$(git --git-dir="$TMP/remote.git" ls-tree -r --name-only main)
printf '%s\n' "$files" | grep -qx "notities/nieuw.txt" && ok "eerste wijziging op de remote" || bad "nieuw.txt ontbreekt op de remote"
printf '%s\n' "$files" | grep -qx "notities/tijdens-push.txt" && ok "wijziging tijdens de push op de remote" || bad "tijdens-push.txt ontbreekt op de remote"

# 2. Nothing changed: no commit, nothing logged as pushed.
before=$(git rev-parse HEAD)
out=$(SNAPSHOT_GITLEAKS=/usr/bin/true run)
[ "$(git rev-parse HEAD)" = "$before" ] && ok "geen wijziging, geen commit" || bad "onnodige commit"

# 3. gitleaks finds something: nothing committed, exit code 1.
echo "verdacht" > notities/verdacht.txt
SNAPSHOT_GITLEAKS=/usr/bin/false run >/dev/null; code=$?
[ "$code" = 1 ] && ok "gitleaks-vondst stopt met code 1" || bad "verwacht code 1, kreeg $code"
[ "$(git rev-parse HEAD)" = "$before" ] && ok "gitleaks-vondst: niets gecommit" || bad "toch gecommit na gitleaks-vondst"
[ -n "$(git status --porcelain)" ] && [ -z "$(git diff --cached --name-only)" ] && ok "gitleaks-vondst: niets gestaged" || bad "staging niet teruggezet"

if [ "$fail" = 0 ]; then echo "alle tests groen"; else echo "TESTS GEFAALD"; exit 1; fi

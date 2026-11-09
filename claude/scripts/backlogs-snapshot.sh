#!/bin/bash
# backlogs-snapshot.sh -- hourly snapshot of the private backlog folder (~/Development/_backlogs) to a private
# GitHub repo. Sessions never commit there themselves; this job is the only committer, so parallel sessions cannot
# mix up the git index. gitleaks checks the staged changes first: on a finding nothing is committed or pushed and
# macOS shows a notification.
#
# Installed as ~/scripts/achtergrondtaken/Backlogs-snapshot (readable name in macOS login items), started by launchd
# job nl.hanskluppel.backlogs-snapshot every hour. Plan: docs/plans/2026-11-09-backlogs-per-project.md.
set -u

DIR="${BACKLOGS_DIR:-$HOME/Development/_backlogs}"
GIT=/usr/bin/git
GITLEAKS=/opt/homebrew/bin/gitleaks

log() { printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"; }
notify() { /usr/bin/osascript -e "display notification \"$1\" with title \"Backlogs-snapshot\"" >/dev/null 2>&1; }

cd "$DIR" || { log "STOP: map $DIR bestaat niet"; exit 1; }

# Files elsewhere that have no other backup (e.g. a private backlog excluded from its repo) are listed in
# backup-bronnen.txt, one path per line relative to ~/Development, and copied to backup/ (with / as __) first.
# Notch only reads files directly in this folder, so backup/ does not show up there.
if [ -f backup-bronnen.txt ]; then
  mkdir -p backup
  while IFS= read -r rel || [ -n "$rel" ]; do
    case "$rel" in ''|'#'*) continue ;; esac
    src="$HOME/Development/$rel"
    if [ -f "$src" ]; then cp -p "$src" "backup/$(printf '%s' "$rel" | sed 's#/#__#g')"; else log "back-upbron ontbreekt: $rel"; fi
  done < backup-bronnen.txt
fi

if [ -n "$($GIT status --porcelain)" ]; then
  $GIT add -A
  if ! "$GITLEAKS" git --pre-commit --staged --no-banner --redact . >/dev/null 2>&1; then
    $GIT reset -q
    log "STOP: gitleaks vond een mogelijk geheim; niets gecommit of gepusht"
    notify "Mogelijk een sleutel in een backlog. Niets opgeslagen naar GitHub. Draai gitleaks in $DIR."
    exit 1
  fi
  $GIT commit -q -m "snapshot $(date '+%Y-%m-%d %H:%M')" && log "commit gemaakt"
fi

# Push whatever is not on the remote yet (also earlier commits whose push failed).
if $GIT remote get-url origin >/dev/null 2>&1; then
  if [ -n "$($GIT log --oneline '@{upstream}..HEAD' 2>/dev/null)" ] || ! $GIT rev-parse '@{upstream}' >/dev/null 2>&1; then
    if $GIT push -q -u origin HEAD 2>&1; then log "gepusht"; else log "push mislukt"; notify "Push naar GitHub mislukt; zie ~/Library/Logs/backlogs-snapshot.log"; fi
  fi
else
  log "geen remote ingesteld; alleen lokaal gecommit"
fi

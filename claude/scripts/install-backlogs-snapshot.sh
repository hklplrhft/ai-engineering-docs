#!/bin/bash
# install-backlogs-snapshot.sh -- installs the hourly backlog snapshot (launchd nl.hanskluppel.backlogs-snapshot).
# Copies backlogs-snapshot.sh to ~/scripts/achtergrondtaken/Backlogs-snapshot and the plist to ~/Library/LaunchAgents,
# then (re)loads the job. Undo: launchctl bootout gui/$(id -u)/nl.hanskluppel.backlogs-snapshot and remove both files.
set -eu
SRC="$(cd "$(dirname "$0")/.." && pwd)"
LABEL=nl.hanskluppel.backlogs-snapshot
TARGET="$HOME/scripts/achtergrondtaken/Backlogs-snapshot"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

mkdir -p "$HOME/scripts/achtergrondtaken" "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
install -m 755 "$SRC/scripts/backlogs-snapshot.sh" "$TARGET"
sed "s#HOME_DIR#$HOME#g" "$SRC/launchd/$LABEL.plist" > "$PLIST"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "geinstalleerd: $TARGET, $PLIST (elk uur, log ~/Library/Logs/backlogs-snapshot.log)"

#!/bin/sh
# Stop hook: Claude may not end its turn while there is uncommitted work.
# Blocks once per turn (stop_hook_active prevents a loop) with the list of dirty files,
# so the work gets committed or explicitly reported. Unmerged branches are shown as a
# non-blocking message. Bron: https://github.com/hklplrhft/ai-engineering-docs (claude/hooks/)

input=$(cat)
if printf '%s' "$input" | grep -q '"stop_hook_active": *true'; then
  exit 0
fi

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

dirty=$(git status --porcelain 2>/dev/null)
default=main
git show-ref --verify --quiet refs/heads/main || { git show-ref --verify --quiet refs/heads/master && default=master; }
unmerged=$(git branch --no-merged "$default" 2>/dev/null | sed 's/^[* ]*//' | grep -v "^$default$" | tr '\n' ' ')
current=$(git branch --show-current 2>/dev/null)

json_escape() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g' | awk '{printf "%s\\n", $0}'; }

if [ -n "$dirty" ]; then
  count=$(printf '%s\n' "$dirty" | wc -l | tr -d ' ')
  list=$(printf '%s\n' "$dirty" | head -15)
  reason="Ongecommit werk in $(basename "$PWD") (branch $current, $count bestand(en)):\\n$(json_escape "$list")"
  [ "$count" -gt 15 ] && reason="${reason}... "
  reason="${reason}\\nCommit wat bij deze taak hoort (selectief, geen git add .), of meld de gebruiker expliciet wat je bewust niet commit en waarom."
  [ -n "$unmerged" ] && reason="${reason}\\nNiet-gemergde branches: ${unmerged}"
  printf '{"decision":"block","reason":"%s"}\n' "$reason"
  exit 0
fi

if [ -n "$unmerged" ] && [ "$current" != "$default" ]; then
  printf '{"systemMessage":"Werkboom schoon. Niet-gemergde branches: %s"}\n' "$(json_escape "$unmerged")"
fi
exit 0

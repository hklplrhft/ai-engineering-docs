#!/bin/sh
# PreToolUse hook (Bash): blocks commands that publish, deploy or destroy without the user
# doing it themselves. Claude gets the reason and asks the user to run `! <command>`.
# Bron: https://github.com/hklplrhft/ai-engineering-docs (claude/hooks/)

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)
[ -z "$cmd" ] && cmd="$CLAUDE_BASH_COMMAND"
[ -z "$cmd" ] && exit 0

block() {
  printf 'BLOCKED by ~/.claude/hooks/pretool-guard.sh: %s\nVraag de gebruiker dit zelf te draaien met:  ! %s\n' "$1" "$cmd" >&2
  exit 2
}

# Publishing and deploying: always by the user.
printf '%s' "$cmd" | grep -qE '(^|[;&|] *)git +push\b' && block "git push wordt nooit door Claude gedaan (afspraak: nooit pushen zonder expliciete bevestiging)"
printf '%s' "$cmd" | grep -qE '\bwrangler +(deploy|publish)\b|\bvercel +(--prod|deploy)\b|\bfirebase +deploy\b|\bnpm +publish\b|\bgh +release +create\b|\bfastlane\b|\bflutter +build +(ipa|appbundle|aab)\b.*upload|\bxcrun +altool\b' && block "deploy/publiceer-commando"

# Destructive git.
printf '%s' "$cmd" | grep -qE '\bgit +reset +--hard\b|\bgit +clean +-[a-zA-Z]*f|\bgit +checkout +-- +\.|\bgit +restore +(\.|--worktree +\.)|\bgit +branch +-D\b|\bgit +push +.*(--force|-f\b|\+[a-zA-Z])|\bgit +stash +drop\b|\bgit +reflog +expire\b' && block "destructief git-commando (werk of historie gaat verloren)"

# Destructive shell: rm -r/-f outside scratch and build folders.
if printf '%s' "$cmd" | grep -qE '(^|[;&|] *)(sudo +)?rm +(-[a-zA-Z]*[rR][a-zA-Z]* +|-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]* +)'; then
  targets=$(printf '%s' "$cmd" | sed -E 's/.*rm +(-[a-zA-Z]+ +)+//; s/[;&|].*//')
  safe=1
  for t in $targets; do
    case "$t" in
      /tmp/*|/private/tmp/*|"$TMPDIR"*|*/scratchpad/*|*/node_modules|*/node_modules/*|node_modules|node_modules/*|dist|dist/*|build|build/*|.wrangler|.wrangler/*|.dart_tool|.dart_tool/*|*/dist|*/build|coverage|coverage/*) ;;
      *) safe=0 ;;
    esac
  done
  [ "$safe" -eq 1 ] || block "rm -r/-f buiten tmp/scratchpad/build-mappen"
fi

# Database destruction.
printf '%s' "$cmd" | grep -qiE '\bdrop +(table|database|schema)\b|\btruncate +table\b' && block "DROP/TRUNCATE"

exit 0

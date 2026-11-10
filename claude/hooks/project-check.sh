#!/bin/sh
# SessionStart hook: check project-inrichting, and point the session at its topic.
# Ref: ~/.claude/docs/project-setup.md
# Bron: https://github.com/hklplrhft/ai-engineering-docs (claude/hooks/)
#
# Topics (plan notch docs/plans/2026-11-10-notities-en-onderwerpen.md): a topic lives in its own worktree
# <Repo>-<onderwerp> with docs/onderwerpen/<onderwerp>.md. In such a worktree the session is told to read that file;
# in the main folder of a repo with docs/onderwerpen/ it gets the list of topics, the ones past their HERZIEN OP date,
# and (when the notes folder exists) the ones without an item in Notch.
# Test: sh claude/hooks/test_project_check.sh
missing=""
info=""
notes="${CLAUDE_NOTES_DIR:-$HOME/Development/_backlogs/notities}"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  top=$(git rev-parse --show-toplevel)
  # The common dir is <main worktree>/.git, also when we are in a linked worktree (where .git is a file).
  common=$(cd "$(git rev-parse --git-common-dir)" && pwd -P)
  main=$(dirname "$common")
  top=$(cd "$top" && pwd -P)
  repo=$(basename "$main")
else
  top=""
  missing="${missing}Geen git repo -- voer git init uit. "
fi

[ -f "CLAUDE.md" ] || missing="${missing}CLAUDE.md ontbreekt -- voer /init uit. "
[ -f ".gitignore" ] || missing="${missing}.gitignore ontbreekt -- maak aan met .env en secrets. "
[ -d "docs/refs" ] || missing="${missing}docs/refs/ ontbreekt (littekens). "
# BACKLOG.md en CHANGELOG.md mogen in de root of in docs/ staan (sommige projecten, zoals aurora_monitor, houden ze
# sinds jaar en dag in docs/). TODO.md telt ook: AIvoorRED noemt zijn backlog zo.
[ -f "BACKLOG.md" ] || [ -f "docs/BACKLOG.md" ] || [ -f "TODO.md" ] || missing="${missing}BACKLOG.md ontbreekt (open punten). "
[ -f "CHANGELOG.md" ] || [ -f "docs/CHANGELOG.md" ] || missing="${missing}CHANGELOG.md ontbreekt. "
[ -f "docs/decisions.md" ] || missing="${missing}docs/decisions.md ontbreekt (besluitenlog). "
if [ -f ".env" ] && [ ! -f ".env.example" ]; then
  missing="${missing}.env.example ontbreekt (welke keys zijn nodig?). "
fi
if [ -f "CLAUDE.md" ] && grep -qiE "^## *TODO|^- \[ \]" CLAUDE.md 2>/dev/null; then
  missing="${missing}CLAUDE.md bevat een TODO-lijst -- verhuis naar BACKLOG.md. "
fi

if [ -n "$top" ] && [ "$top" != "$main" ]; then
  # A linked worktree named <Repo>-<onderwerp>: its topic file.
  base=$(basename "$top")
  topic=""
  case "$base" in
    "$repo"-*) topic=${base#"$repo"-} ;;
  esac
  if [ -n "$topic" ]; then
    file="docs/onderwerpen/$topic.md"
    if [ -f "$top/$file" ]; then
      info="${info}Onderwerp ${topic}: lees eerst ${file} (WAAR, STAND, VOLGENDE STAP, OPEN PUNTEN) en werk dat bestand bij aan het eind van elk werkmoment. "
    else
      ref=$(git symbolic-ref -q --short refs/remotes/origin/HEAD 2>/dev/null || echo origin/main)
      if git cat-file -e "$ref:$file" 2>/dev/null; then
        info="${info}Onderwerp ${topic}: ${file} staat op ${ref} maar nog niet in deze worktree; doe eerst git merge ${ref}. "
      fi
    fi
  fi
elif [ -n "$top" ] && [ -d "$top/docs/onderwerpen" ]; then
  # The main folder: which topics exist, which are due for review, which have no item in Notch.
  today=$(date +%Y-%m-%d)
  lrepo=$(printf '%s' "$repo" | tr '[:upper:]' '[:lower:]')
  names=""; due=""; noitem=""
  for f in "$top"/docs/onderwerpen/*.md; do
    [ -f "$f" ] || continue
    n=$(basename "$f" .md)
    [ "$n" = "README" ] && continue
    names="${names}${names:+, }$n"
    d=$(sed -n 's/^HERZIEN OP:* *\([0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]\).*/\1/p' "$f" | head -n 1)
    if [ -n "$d" ] && [ "$(printf '%s\n%s\n' "$d" "$today" | sort | head -n 1)" = "$d" ]; then
      due="${due}${due:+, }$n ($d)"
    fi
    if [ -d "$notes" ] && [ ! -f "$notes/$lrepo $n.txt" ]; then
      noitem="${noitem}${noitem:+, }$n"
    fi
  done
  if [ -n "$names" ]; then
    info="${info}Onderwerpen in ${repo} (docs/onderwerpen/, elk met een eigen worktree ${repo}-<onderwerp>): ${names}. "
    [ -n "$due" ] && info="${info}Over hun HERZIEN OP-datum, voorleggen aan Hans: ${due}. "
    [ -n "$noitem" ] && info="${info}Zonder item in Notch (${notes}/${lrepo} <onderwerp>.txt), melden aan Hans: ${noitem}. "
  fi
fi

if [ -n "$missing" ] || [ -n "$info" ]; then
  esc() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }
  out="{"
  if [ -n "$missing" ]; then
    out="${out}\"systemMessage\": \"Project-inrichting check: $(esc "$missing")Zie ~/.claude/docs/project-setup.md.\""
  fi
  if [ -n "$info" ]; then
    [ -n "$missing" ] && out="${out}, "
    out="${out}\"hookSpecificOutput\": {\"hookEventName\": \"SessionStart\", \"additionalContext\": \"$(esc "$info")\"}"
  fi
  echo "${out}}"
fi

#!/bin/sh
# SessionStart hook: check project-inrichting.
# Ref: ~/.claude/docs/project-setup.md
# Bron: https://github.com/hklplrhft/ai-engineering-docs (claude/hooks/)
missing=""

[ -d ".git" ] || missing="${missing}Geen git repo -- voer git init uit. "
[ -f "CLAUDE.md" ] || missing="${missing}CLAUDE.md ontbreekt -- voer /init uit. "
[ -f ".gitignore" ] || missing="${missing}.gitignore ontbreekt -- maak aan met .env en secrets. "
[ -d "docs/refs" ] || missing="${missing}docs/refs/ ontbreekt (littekens). "
[ -f "BACKLOG.md" ] || missing="${missing}BACKLOG.md ontbreekt (open punten). "
[ -f "CHANGELOG.md" ] || missing="${missing}CHANGELOG.md ontbreekt. "
[ -f "docs/decisions.md" ] || missing="${missing}docs/decisions.md ontbreekt (besluitenlog). "
if [ -f ".env" ] && [ ! -f ".env.example" ]; then
  missing="${missing}.env.example ontbreekt (welke keys zijn nodig?). "
fi
if [ -f "CLAUDE.md" ] && grep -qiE "^## *TODO|^- \[ \]" CLAUDE.md 2>/dev/null; then
  missing="${missing}CLAUDE.md bevat een TODO-lijst -- verhuis naar BACKLOG.md. "
fi

if [ -n "$missing" ]; then
  # Escape double quotes for JSON.
  msg=$(printf '%s' "$missing" | sed 's/"/\\"/g')
  echo "{\"systemMessage\": \"Project-inrichting check: ${msg}Zie ~/.claude/docs/project-setup.md.\"}"
fi

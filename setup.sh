#!/bin/bash
# AI Engineering Setup -- configuratie voor Claude Code
# Bron: https://hklplrhft.github.io/ai-engineering-docs/deel-22.html
#
# Installeert de werkwijze uit de AI Engineering Gids in ~/.claude/:
#   CLAUDE.md, docs/project-setup.md, hooks/*.sh en de hook-configuratie in settings.json.
#
# De bron van alle bestanden is de map claude/ in de repo
# https://github.com/hklplrhft/ai-engineering-docs. Twee manieren:
#   - Vanuit een lokale clone (bash setup.sh): ~/.claude verwijst met symlinks naar de repo,
#     zodat `git pull` in de repo meteen op deze machine geldt en er nooit twee versies zijn.
#   - Via curl (curl -fsSL .../setup.sh | bash): de bestanden worden gedownload en gekopieerd.
#     Draai het script opnieuw om bij te werken.
# Bestaande bestanden worden eerst gebackupt naar ~/.claude/backups/setup-<datum>/.
# settings.json wordt nooit vervangen: alleen de hooks worden erin samengevoegd (jq).

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

REPO_RAW="https://raw.githubusercontent.com/hklplrhft/ai-engineering-docs/main/claude"
FILES="CLAUDE.md docs/project-setup.md hooks/project-check.sh hooks/stop-git-check.sh hooks/pretool-guard.sh hooks.json"

echo ""
echo "AI Engineering Setup"
echo "===================="
echo ""

if command -v claude &> /dev/null; then
  echo -e "${GREEN}[OK]${NC} Claude Code is geinstalleerd"
else
  echo -e "${YELLOW}[!]${NC} Claude Code niet gevonden. Installeer eerst:"
  echo "    npm install -g @anthropic-ai/claude-code"
  echo ""
fi

if ! command -v jq &> /dev/null; then
  echo -e "${RED}[X]${NC} jq ontbreekt (nodig voor de hooks en settings.json). Installeer: brew install jq"
  exit 1
fi

mkdir -p ~/.claude/docs ~/.claude/hooks ~/.claude/backups

# --- Bron bepalen: lokale clone (symlink) of download (kopie) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/claude/CLAUDE.md" ]; then
  MODE=link
  SRC="$SCRIPT_DIR/claude"
  echo -e "${GREEN}[OK]${NC} Lokale clone gevonden: symlinks naar $SRC"
else
  MODE=copy
  SRC="$(mktemp -d)"
  echo -e "${GREEN}[OK]${NC} Bestanden downloaden van $REPO_RAW"
  for f in $FILES; do
    mkdir -p "$SRC/$(dirname "$f")"
    curl -fsSL "$REPO_RAW/$f" -o "$SRC/$f"
  done
fi

BACKUP=~/.claude/backups/setup-$(date +%Y%m%d-%H%M%S)
backup_existing() {
  local target="$1"
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    mkdir -p "$BACKUP/$(dirname "${target#$HOME/.claude/}")"
    cp "$target" "$BACKUP/${target#$HOME/.claude/}"
    echo -e "${YELLOW}[BACKUP]${NC} $target -> $BACKUP/"
  fi
}

install_file() {
  local f="$1" target=~/.claude/"$1"
  backup_existing "$target"
  rm -f "$target"
  if [ "$MODE" = link ]; then
    ln -s "$SRC/$f" "$target"
    echo -e "${GREEN}[LINK]${NC} ~/.claude/$f -> $SRC/$f"
  else
    cp "$SRC/$f" "$target"
    echo -e "${GREEN}[OK]${NC} ~/.claude/$f"
  fi
}

for f in CLAUDE.md docs/project-setup.md hooks/project-check.sh hooks/stop-git-check.sh hooks/pretool-guard.sh; do
  install_file "$f"
done
chmod +x "$SRC"/hooks/*.sh

# --- settings.json: hooks samenvoegen, rest ongemoeid laten ---
SETTINGS=~/.claude/settings.json
if [ ! -f "$SETTINGS" ]; then
  cp "$SRC/hooks.json" "$SETTINGS"
  echo -e "${GREEN}[OK]${NC} ~/.claude/settings.json aangemaakt"
else
  backup_existing "$SETTINGS"
  # Per event: bestaande entries houden, entries uit hooks.json toevoegen als hun commando ontbreekt.
  jq --slurpfile new "$SRC/hooks.json" '
    def cmds(entries): [entries[]?.hooks[]?.command];
    .hooks = ((.hooks // {}) as $cur
      | reduce ($new[0].hooks | to_entries[]) as $e ($cur;
          .[$e.key] = ((.[$e.key] // []) as $existing
            | $existing + [ $e.value[] | select((.hooks[0].command) as $c | (cmds($existing) | index($c)) == null) ])))
  ' "$SETTINGS" > "$SETTINGS.tmp" && mv "$SETTINGS.tmp" "$SETTINGS"
  echo -e "${GREEN}[OK]${NC} hooks samengevoegd in ~/.claude/settings.json"
fi

[ "$MODE" = copy ] && rm -rf "$SRC"

echo ""
echo "Klaar. Geinstalleerd:"
echo "  ~/.claude/CLAUDE.md                globale werkwijze"
echo "  ~/.claude/docs/project-setup.md    checklist per project"
echo "  ~/.claude/hooks/project-check.sh   SessionStart: meldt wat in het project ontbreekt"
echo "  ~/.claude/hooks/stop-git-check.sh  Stop: geen beurt eindigen met ongecommit werk"
echo "  ~/.claude/hooks/pretool-guard.sh   PreToolUse: blokkeert push/deploy/destructieve commando's"
if [ "$MODE" = link ]; then
  echo ""
  echo "Symlink-modus: 'git pull' in $SCRIPT_DIR werkt deze machine bij."
else
  echo ""
  echo "Kopie-modus: draai dit script opnieuw om bij te werken."
fi
echo ""

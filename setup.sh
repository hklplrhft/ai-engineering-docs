#!/bin/bash
# AI Engineering Setup -- eenmalige configuratie voor Claude Code
# Bron: https://hklplrhft.github.io/ai-engineering-docs/deel-22.html
#
# Dit script maakt 4 bestanden aan in ~/.claude/ die de werkwijze
# uit de AI Engineering Gids automatisch afdwingen bij elk project.
# Bestaande bestanden worden NIET overschreven.

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "AI Engineering Setup"
echo "===================="
echo ""

# Check: Claude Code geinstalleerd?
if command -v claude &> /dev/null; then
  echo -e "${GREEN}[OK]${NC} Claude Code is geinstalleerd"
else
  echo -e "${YELLOW}[!]${NC} Claude Code niet gevonden. Installeer eerst:"
  echo "    npm install -g @anthropic-ai/claude-code"
  echo ""
fi

# Directories aanmaken
mkdir -p ~/.claude/docs
mkdir -p ~/.claude/hooks

CREATED=0
SKIPPED=0

# --- Bestand 1: ~/.claude/CLAUDE.md ---
if [ -f ~/.claude/CLAUDE.md ]; then
  echo -e "${YELLOW}[SKIP]${NC} ~/.claude/CLAUDE.md bestaat al"
  SKIPPED=$((SKIPPED + 1))
else
  cat > ~/.claude/CLAUDE.md << 'CLAUDEMD'
# Globale instructies

## Taal
# Pas aan naar je eigen taal:
- Communiceer in het Nederlands
- Code, commits en comments in het Engels

## Werkwijze -- plan, verifieer, commit

### Altijd plannen voor doen
- /plan bij taken die meer dan 1 bestand raken of langer dan 5 minuten duren
- Geef verificatiecriteria mee: welke tests moeten slagen, welke output wordt verwacht
- Wacht op goedkeuring voordat je begint met implementeren

### Context schoon houden
- Stel /clear voor bij taakwissel (andere feature, ander onderwerp)
- Stel /compact voor na 30+ minuten of wanneer context vol raakt
- Bij sessie-overdracht: maak een HANDOFF.md (doel, status, wat geprobeerd, volgende stappen)

### Git-discipline
- Werk op branches, niet direct op main
- Commit na elke voltooide wijziging -- herinner als er nog niet gecommit is
- Selectief committen: specifieke bestanden, niet git add .
- Nooit pushen, deployen of berichten sturen zonder expliciete bevestiging

### Verificatie
- Waarschuw bij hallucinaties (onbekende packages, API's, functies) -- verifieer eerst
- Stel git diff voor bij grotere wijzigingen zodat de gebruiker kan reviewen
- Commit nooit code die de gebruiker niet begrijpt -- bied uitleg aan

## Code kwaliteit

### Test-first bij bugs
- Bij bugfixes: schrijf eerst een falende regressietest, dan pas de fix
- Test na elke wijziging -- herinner aan testen/lint/analyze na code changes
- Zonder test is een fix alleen voor vandaag

### Feedback loop -- van fout naar regel
- Fout gevonden -> fix + regressietest
- Terugkerend probleem -> regel toevoegen aan docs/refs/ of CLAUDE.md
- Kritieke fout -> stel een hook voor die het afdwingt
- Doel: elke fout kan maar een keer voorkomen

### Kwaliteitscontroles
- Geen secrets hardcoden -- gebruik environment variables of .env + .gitignore
- Review gegenereerde code op OWASP top 10 (SQL injection, XSS, command injection)
- Stel linters/typecheck voor als die ontbreken in het project

## Project-inrichting check
Bij het begin van een taak in een nieuw project, doorloop de volledige setup:
- Lees ~/.claude/docs/project-setup.md en doorloop alle stappen
- Stel elke stap voor aan de gebruiker voordat je begint met de eigenlijke taak

Minimale check bij bestaande projecten:
- CLAUDE.md van het actieve project (zo niet: stel /init voor)
- Hooks voor lint/typecheck (zo niet: stel voor om in te richten)
- docs/refs/ map voor littekens-documenten (zo niet: vermeld het bij terugkerende fouten)
- .gitignore met .env en secrets (zo niet: waarschuw)

## Signalen -- wanneer ingrijpen
- Na 2 mislukte pogingen voor dezelfde taak: stel voor om te stoppen, /clear, en een
  betere prompt te formuleren
- Bij herhaling van eerder gemaakte fouten: stel voor om een regel/hook toe te voegen
- Bij vage opdrachten: vraag om specifieke bestanden, error output, of verwacht gedrag
- Bij grote wijzigingen zonder tests: weiger door te gaan totdat er verificatiecriteria zijn

## Signalen -- wanneer uitbreiden (5-lagen systeem)
Stel de volgende uitbreidingen voor wanneer het moment er is. Niet vooraf, maar zodra
de situatie zich voordoet:
- Bug gefixt zonder test? -> "Zal ik een test-framework opzetten?"
- Zelfde fout 2x? -> "Zal ik een hook instellen?"
- Valkuil ontdekt? -> "Zal ik dit in docs/refs/ vastleggen?"
- Handeling 3x herhaald? -> "Zal ik hier een skill van maken?"
- Parallelle controle nodig? -> "Zal ik een custom agent maken?"
- Sessie-einde met onafgemaakt werk? -> "Zal ik een HANDOFF.md maken?"

## Veiligheid
- Review shell commando's kritisch, vooral: rm -rf, git push --force, drop table
- Geen gevoelige data (API keys, wachtwoorden) in prompts of CLAUDE.md
- Stel nooit voor om hooks te skippen (--no-verify) of checks uit te schakelen

## Stijl
- Geen em-dashes of en-dashes in code of tekst, gebruik --
- Wees beknopt in uitleg, gedetailleerd in code
CLAUDEMD
  echo -e "${GREEN}[OK]${NC} ~/.claude/CLAUDE.md aangemaakt"
  CREATED=$((CREATED + 1))
fi

# --- Bestand 2: ~/.claude/docs/project-setup.md ---
if [ -f ~/.claude/docs/project-setup.md ]; then
  echo -e "${YELLOW}[SKIP]${NC} ~/.claude/docs/project-setup.md bestaat al"
  SKIPPED=$((SKIPPED + 1))
else
  cat > ~/.claude/docs/project-setup.md << 'SETUPMD'
# Project Setup Checklist

Doorloop deze stappen bij het begin van een nieuw project of wanneer
een project geen CLAUDE.md heeft.

## Stap 1: Project CLAUDE.md aanmaken

Stel `/init` voor als er geen CLAUDE.md in de projectroot staat.

De CLAUDE.md moet bevatten (compact, max ~100-150 regels):
- **Project** -- wat doet het project, voor wie
- **Tech stack** -- framework, taal, database, hosting
- **Commando's** -- build, dev, test, lint (exact zoals ze gedraaid worden)
- **Architectuur** -- mappenstructuur, belangrijke patronen, routing
- **Kritieke regels** -- dingen die NOOIT mogen (bijv. "verwijder geen content")
- **Referenties** -- verwijzingen naar docs/refs/ bestanden voor details

Wat er NIET in hoort:
- Code style (dat doet de linter)
- Code voorbeelden (verouderen)
- Info die uit de code afgeleid kan worden

## Stap 2: .gitignore controleren

Check of .gitignore aanwezig is met minimaal:
- .env en .env.* (secrets)
- node_modules/ of equivalent (dependencies)
- Build output (dist/, .astro/, .next/, build/)
- OS bestanden (.DS_Store)
- IDE bestanden (.vscode/settings.json, .idea/)

Waarschuw als .gitignore ontbreekt of .env niet erin staat.

## Stap 3: Git initialiseren

Als er nog geen .git/ is:
- `git init`
- Maak een feature branch: `git checkout -b feature/<beschrijvend>`
- Werk NOOIT direct op main

## Stap 4: docs/refs/ aanmaken

Maak `docs/refs/` directory aan (leeg is OK bij start).

Dit is de plek voor "littekens" -- lessen uit fouten:
- Fout gevonden -> fix + regressietest + regel in docs/refs/
- Terugkerend probleem -> regel toevoegen
- Kritieke fout -> hook voorstellen die het afdwingt

Typische bestanden die hier later in komen:
- `docs/refs/api-regels.md` -- API conventies en valkuilen
- `docs/refs/deploy.md` -- deployment procedures
- `docs/refs/routing.md` -- hoe routing werkt
- `docs/refs/data-structuur.md` -- data model uitleg

## Stap 5: Hooks instellen

Detecteer de tech stack en stel de juiste hook voor:

| Stack          | Pre-commit hook commando                                  |
|----------------|-----------------------------------------------------------|
| Astro          | `npx astro build`                                         |
| Next.js/React  | `npm run lint && npx tsc --noEmit`                        |
| Python         | `ruff check . && mypy .`                                  |
| Go             | `go vet ./... && staticcheck ./...`                       |
| Flutter        | `flutter analyze && dart format --set-exit-if-changed .`  |
| Generiek       | `npm run build` of `npm test`                             |

## Stap 6: Eerste commit

Na het inrichten:
- Selectief stagen (specifieke bestanden, niet `git add .`)
- Duidelijk commit bericht
- Verifieer dat de pre-commit hook werkt

## Verificatie

Na het doorlopen van alle stappen, controleer:
- [ ] CLAUDE.md aanwezig en compact
- [ ] .gitignore met .env en secrets
- [ ] Git repo met feature branch (niet main)
- [ ] docs/refs/ directory aanwezig
- [ ] Pre-commit hook geinstalleerd en werkend
- [ ] Eerste commit geslaagd
SETUPMD
  echo -e "${GREEN}[OK]${NC} ~/.claude/docs/project-setup.md aangemaakt"
  CREATED=$((CREATED + 1))
fi

# --- Bestand 3: ~/.claude/hooks/project-check.sh ---
if [ -f ~/.claude/hooks/project-check.sh ]; then
  echo -e "${YELLOW}[SKIP]${NC} ~/.claude/hooks/project-check.sh bestaat al"
  SKIPPED=$((SKIPPED + 1))
else
  cat > ~/.claude/hooks/project-check.sh << 'HOOKSH'
#!/bin/bash
# SessionStart hook: controleert of een project is ingericht
warnings=""

[ ! -d ".git" ] && warnings="${warnings}\n- Geen git repo. Overweeg: git init"
[ ! -f "CLAUDE.md" ] && warnings="${warnings}\n- Geen CLAUDE.md. Stel voor: /init"
[ ! -d "docs/refs" ] && warnings="${warnings}\n- Geen docs/refs/ map"
if [ -f ".gitignore" ]; then
  grep -q "^\.env" .gitignore 2>/dev/null || \
    warnings="${warnings}\n- .env staat niet in .gitignore!"
else
  warnings="${warnings}\n- Geen .gitignore gevonden"
fi

if [ -n "$warnings" ]; then
  echo "PROJECT-CHECK: Ontbrekende onderdelen:"
  echo -e "$warnings"
  echo ""
  echo "Bied aan om ontbrekende onderdelen op te zetten."
fi
HOOKSH
  chmod +x ~/.claude/hooks/project-check.sh
  echo -e "${GREEN}[OK]${NC} ~/.claude/hooks/project-check.sh aangemaakt"
  CREATED=$((CREATED + 1))
fi

# --- Bestand 4: ~/.claude/settings.json ---
if [ -f ~/.claude/settings.json ]; then
  # Check of SessionStart hook al geconfigureerd is
  if grep -q "SessionStart" ~/.claude/settings.json 2>/dev/null; then
    echo -e "${YELLOW}[SKIP]${NC} ~/.claude/settings.json bevat al een SessionStart hook"
  else
    echo -e "${YELLOW}[!]${NC} ~/.claude/settings.json bestaat maar heeft geen SessionStart hook"
    echo "    Voeg handmatig toe aan je settings.json:"
    echo '    "SessionStart": [{"hooks": [{"type": "command", "command": "bash ~/.claude/hooks/project-check.sh"}]}]'
  fi
  SKIPPED=$((SKIPPED + 1))
else
  cat > ~/.claude/settings.json << 'SETTINGSJSON'
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/project-check.sh"
          }
        ]
      }
    ]
  }
}
SETTINGSJSON
  echo -e "${GREEN}[OK]${NC} ~/.claude/settings.json aangemaakt"
  CREATED=$((CREATED + 1))
fi

# Samenvatting
echo ""
echo "===================="
if [ $CREATED -gt 0 ]; then
  echo -e "${GREEN}${CREATED} bestand(en) aangemaakt.${NC}"
fi
if [ $SKIPPED -gt 0 ]; then
  echo -e "${YELLOW}${SKIPPED} bestand(en) overgeslagen (bestonden al).${NC}"
fi
echo ""
echo "Volgende stap: open een project en start claude."
echo "De SessionStart hook detecteert automatisch wat ontbreekt."
echo ""
echo "Pas ~/.claude/CLAUDE.md aan naar je eigen taal en voorkeuren."
echo "Gids: https://hklplrhft.github.io/ai-engineering-docs/deel-22.html"
echo ""

# Project Setup Checklist

Doorloop deze stappen bij het begin van een nieuw project of wanneer een project geen CLAUDE.md heeft.
Gebaseerd op: https://hklplrhft.github.io/ai-engineering-docs/index.html
Bron van dit bestand: https://github.com/hklplrhft/ai-engineering-docs (map `claude/docs/`).

## Stap 1: Project CLAUDE.md aanmaken

Stel `/init` voor als er geen CLAUDE.md in de projectroot staat.

De CLAUDE.md moet bevatten (compact, max ~100-150 regels):
- **Project** -- wat doet het project, voor wie
- **Tech stack** -- framework, taal, database, hosting
- **Commando's** -- build, dev, test, lint (exact zoals ze gedraaid worden)
- **Architectuur** -- mappenstructuur, belangrijke patronen, routing
- **Kritieke regels** -- dingen die NOOIT mogen (bijv. "verwijder geen content", "geen secrets in code")
- **Referenties** -- verwijzingen naar docs/refs/ bestanden voor details
- **Feiten met datum en bron** -- IDs, accounts, URLs: "gecontroleerd op <datum> via <bron>"

Wat er NIET in hoort:
- Code style (dat doet de linter)
- Code voorbeelden (verouderen)
- Info die uit de code afgeleid kan worden
- TODO-lijsten (die horen in BACKLOG.md; bij herschrijven van CLAUDE.md vallen ze weg)

## Stap 2: .gitignore en .env.example

Check of .gitignore aanwezig is met minimaal:
- .env en .env.* (secrets)
- node_modules/ of equivalent (dependencies)
- Build output (dist/, .astro/, .next/, build/)
- OS bestanden (.DS_Store)
- IDE bestanden (.vscode/settings.json, .idea/)

Maak een `.env.example` met alle benodigde keys zonder waarden, en leg in docs/refs/ vast waar
de echte waarden staan (wachtwoordmanager, ander project, dashboard). Zo kan een placeholder-token
nooit stilzwijgend voor een echte doorgaan.

Waarschuw als .gitignore ontbreekt of .env niet erin staat.

## Stap 3: Git initialiseren

Als er nog geen .git/ is:
- `git init`
- Maak een feature branch: `git checkout -b feature/<beschrijvend>`
- Werk NOOIT direct op main
- Stel voor de repo een remote te geven (GitHub) en CI in te richten zodra er tests zijn

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

## Stap 4b: BACKLOG.md, CHANGELOG.md, docs/decisions.md, docs/plans/

Vijf plekken, elk met een eigen regel. Zo kan een afspraak, besluit of open punt alleen
verdwijnen door het bewust af te vinken, nooit door herschrijven.

| Bestand | Inhoud | Regel |
|---|---|---|
| `BACKLOG.md` | Alle open punten, vragen en bevindingen, geprioriteerd in secties | Alleen aanvullen of afvinken, nooit herschrijven |
| `CHANGELOG.md` | Per datum wat er veranderd is (features, fixes, besluiten, externe wijzigingen) | Alleen aanvullen, nieuwste bovenaan |
| `docs/decisions.md` | Besluitenlog: datum, besluit, waarom, verworpen alternatieven, wie | Alleen aanvullen; elke beantwoorde ontwerpvraag krijgt een regel |
| `docs/plans/` | Goedgekeurde plannen (`YYYY-MM-DD-<naam>.md`) | Niet wijzigen na goedkeuring; afwijkingen in CHANGELOG.md |
| `HANDOFF.md` | Momentopname: status, waar gebleven, eerstvolgende stap, hoe lokaal te testen | Mag herschreven worden; geen open punten hierin |

Templates:
```markdown
# Backlog

Open punten, geprioriteerd. Afgeronde punten verhuizen naar CHANGELOG.md.

## 1. <hoogste prioriteit, bijv. naar productie>
- [ ] ...

## 2. <volgende thema>
- [ ] ...

## Vragen
- [ ] ...

## Later / nice to have
- [ ] ...
```

```markdown
# Changelog

Alleen aanvullen, nooit herschrijven. Nieuwste bovenaan. Open punten staan in BACKLOG.md.

## YYYY-MM-DD -- <korte titel>
- ...
```

```markdown
# Besluiten

Alleen aanvullen. Nieuwste bovenaan. Een besluit terugdraaien = nieuw besluit met verwijzing.

## YYYY-MM-DD <titel>
- **Besluit**: ...
- **Waarom**: ...
- **Alternatieven**: ... (verworpen omdat ...)
- **Wie**: <naam> via <gesprek/plan>
```

Werkritme: na elke afgeronde wijziging, vóór de commit: CHANGELOG.md aanvullen, het punt in
BACKLOG.md afvinken, besluiten in docs/decisions.md zetten. Nieuwe vragen of bevindingen direct
in BACKLOG.md. Wijzigingen in externe systemen (CRM, cloud, stores): CHANGELOG.md + script in `scripts/`.

## Stap 5: Hooks instellen

Globaal (voor alle projecten, via setup.sh in ~/.claude/settings.json):
- SessionStart: `project-check.sh` meldt wat er in de projectinrichting ontbreekt
- Stop: `stop-git-check.sh` blokkeert het einde van een beurt zolang er ongecommit werk staat
- PreToolUse (Bash): `pretool-guard.sh` blokkeert `git push`, deploys en destructieve commando's;
  de gebruiker draait die zelf met `! <commando>`

Per project: stel een pre-commit check voor die de build/lint/tests draait.

### Detecteer de tech stack en stel de juiste hook voor:

| Stack | Pre-commit hook commando |
|-------|--------------------------|
| Astro | `npx astro build` |
| Next.js/React | `npm run lint && npx tsc --noEmit` |
| Python | `ruff check . && mypy .` |
| Go | `go vet ./... && staticcheck ./...` |
| Flutter | `flutter analyze && flutter test` |
| Cloudflare Worker / TypeScript | `npx tsc --noEmit && npx vitest run` |
| Generiek | `npm run build` of `npm test` |

Als Claude Code PreToolUse-hook in `.claude/settings.json` van het project (draait bij `git commit`):
```bash
mkdir -p .claude/hooks
cat > .claude/hooks/pre-commit-check.sh << 'HOOK'
#!/bin/bash
[[ "$CLAUDE_BASH_COMMAND" != *"git commit"* ]] && exit 0
cd "$(git rev-parse --show-toplevel)" || exit 1
<COMMANDO HIER> || { echo "BLOCKED: fix the errors before committing."; exit 1; }
HOOK
chmod +x .claude/hooks/pre-commit-check.sh
```
En in `.claude/settings.json`: `{"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":"bash .claude/hooks/pre-commit-check.sh"}]}]}}`

## Stap 6: Eerste commit

Na het inrichten:
- Selectief stagen (specifieke bestanden, niet `git add .`)
- Duidelijk commit bericht
- Verifieer dat de pre-commit hook werkt

## Verificatie

Na het doorlopen van alle stappen, controleer:
- [ ] CLAUDE.md aanwezig en compact, zonder TODO-lijst
- [ ] .gitignore met .env en secrets; .env.example aanwezig
- [ ] Git repo met feature branch (niet main)
- [ ] docs/refs/ directory aanwezig
- [ ] BACKLOG.md, CHANGELOG.md, docs/decisions.md aanwezig
- [ ] Pre-commit hook geinstalleerd en werkend
- [ ] Eerste commit geslaagd

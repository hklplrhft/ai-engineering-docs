# CLAUDE.md -- ai-engineering-docs

Bron van de AI Engineering Gids (https://hklplrhft.github.io/ai-engineering-docs/) en van de Claude-configuratie
die `setup.sh` installeert. Statische HTML, geen build-stap.

## Opbouw

- `index.html`, `deel-NN.html`, `referentie-*.html`: de hoofdstukken van de gids. Elke pagina heeft dezelfde opbouw:
  head (fonts en `styles.css`), hamburger, zijnav (`<nav class="nav">`), `<main>` met een `<section>`, de pager
  (`<nav class="page-nav">` met vorige, `n / totaal`, volgende) en het script onderaan.
- `plannen/`: losse plannen met een eigen menu en teller; die horen niet bij de reeks van de gids.
- `claude/`: de bron van wat `setup.sh` in `~/.claude/` zet (globale `CLAUDE.md`, `docs/project-setup.md`, hooks,
  `hooks.json`, scripts, `AGENTS.md.template`). Dit is de enige versie: hoofdstukken verwijzen ernaar en kopieren
  hem niet.
- `ai-engineering-starter-kit.zip`: losse starter kit met eigen minimale sjablonen.

## Regels

- Een nieuw of verplaatst hoofdstuk: de zijnav in alle gidspagina's bijwerken, en de pager (vorige, volgende,
  `n / totaal`) in alle gidspagina's. Controleer daarna dat alle interne links en ankers bestaan.
- Geen gedachtestreepjes (em of en dash); gebruik `--`, komma's of punten.
- Algemene hoofdstukken bevatten geen namen van eigen projecten, klanten of interne tools: de gids is bedoeld om aan
  anderen mee te geven.
- `claude/CLAUDE.md` blijft compact (onder ~200 regels): per regel een zin, de uitleg staat in de gids.

## Vastleggen

Open punten in `BACKLOG.md`, wat er veranderde in `CHANGELOG.md` (nieuwste bovenaan), besluiten in
`docs/decisions.md`, goedgekeurde plannen in `docs/plans/`. Codex-toets: `claude/scripts/codex_second_opinion.sh`
(uitvoer in `logs/codex/`, niet in git).

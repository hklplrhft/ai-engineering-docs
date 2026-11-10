# Plan: afgevinkte punten uit de onderwerpbestanden naar een archief

Status: v2 (na Codex-toets), goedgekeurd door Hans op 10 nov 2026. Antwoorden: A ja (klantzaken: rij en onderwerpbestand
weg, archief blijft), B nee (BACKLOG.md van eigen projecten niet archiveren). Branch `hans/backlog-archief` (worktree
`~/Development/ai-engineering-docs/ai-engineering-docs-archief`, vanaf main 336a362).

## Aanleiding

Hans (10 nov): "waarom zou ik alle afgevinkte punten bewaren?" De onderwerpbestanden in `~/Development/_backlogs/`
groeien door afgevinkte punten: samen 129 afgevinkte hoofdpunten in 15 bestanden van AIvoorRED (bijvoorbeeld
copernica-mailings 11 open en 11 afgevinkt in 317 regels). De regel "alleen aanvullen of afvinken, nooit herschrijven"
bestaat om te voorkomen dat een open punt stil verdwijnt; elke afvinking staat al in CHANGELOG en alles staat in git
(uurtaak). Keuze Hans uit drie (archief, gewoon weghalen, laten staan): archief.

## Wat er verandert

1. Nieuw script `claude/scripts/backlog_archief.py` (naast `backlogs-snapshot.sh`), met test
   `claude/scripts/test_backlog_archief.py`:
   - Werkt alleen op onderwerpbestanden `~/Development/_backlogs/<repo>/<onderwerp>.md`; weigert de korte rijen en
     kladblokken (`_backlog_*.txt`), bestanden in `archief/` en alles daarbuiten.
   - Verplaatst een afgevinkt hoofdpunt (`- [x] ...` op kolom 0) met zijn vervolgregels naar
     `<repo>/archief/<onderwerp>.md`. Vervolgregels zijn ingesprongen regels, ook na een witregel (een tweede alinea
     of een subpunt onder het punt); het punt eindigt bij het volgende `- `-punt, een kop of tekst die niet
     ingesprongen is.
   - Blijft staan: open punten, afgevinkte subpunten onder een open punt, een afgevinkt punt dat nog een open
     subpunt heeft (met elk lijstteken: `-`, `*`, `+` of `1.`), en alle andere tekst (WAAR, STAND, VOLGENDE STAP, koppen, intro's van secties).
   - Een witregel gaat mee als het punt tussen witregels stond, zodat er één witregel tussen de punten blijft en
     alinea's niet aan elkaar plakken. Staat er tekst op kolom 0 direct onder een afgevinkt punt (niet in te
     delen), dan slaat het script dat hele bestand over.
   - Het archief krijgt per run een blok "Gearchiveerd op <datum> (<n> punten):", met de punten onder de kop waar
     ze stonden; het archief wordt alleen aangevuld.
   - Veiligheid: het onderwerpbestand wordt pas vervangen als elk punt in het archief staat en het bestand sinds het
     inlezen niet veranderd is (een terminal kan er tegelijk in schrijven); anders blijft het staan en maakt een
     tweede run het af. Of een punt al in het archief staat, kijkt het script per punt, dus niets komt er dubbel in,
     ook niet als er intussen meer is afgevinkt. Schrijft een terminal precies tussen die controle en het vervangen
     in het bestand, dan merkt het script dat achteraf (een harde link houdt het oude bestand vast) en zet het de
     versie van de terminal terug. Alleen een terminal die in diezelfde paar microseconden een heel nieuw bestand
     neerzet, ziet het niet; dat restrisico accepteer ik. Na het schrijven controleert het dat alle open punten (ook
     subpunten, elk lijstteken) er nog zijn, in dezelfde volgorde, en dat elke weggehaalde regel in het archief
     staat. Een slot voorkomt twee runs van het script tegelijk. Een proefrun schrijft alleen in een map buiten
     `_backlogs` (een map erin of eromheen weigert hij).
2. Eenmalige run nu op alle 15 onderwerpbestanden van AIvoorRED (zoom-academy-gateway/branches.md is intussen weg,
   akkoord Hans; het open punt staat nu in checkout-app.md). Proefrun 10 nov, na de Codex-aanpassingen:

   | Bestand | Naar archief | Blijft (afgevinkt met open subpunt) | Regels | Open |
   |---|---|---|---|---|
   | a-bounces | 5 | 0 | 99 -> 89 | 25 |
   | aivoorred-app | 14 | 0 | 452 -> 282 | 28 |
   | artikelen-zoom01 | 1 | 0 | 44 -> 39 | 11 |
   | backlog-ordening | 16 | 0 | 47 -> 15 | 4 |
   | checkout-app | 7 | 0 | 184 -> 56 | 8 |
   | copernica-mailings | 11 | 0 | 317 -> 116 | 11 |
   | klantzaken | 10 | 0 | 73 -> 18 | 0 |
   | leden-betalingen | 11 | 0 | 332 -> 119 | 11 |
   | mobiel | 1 | 0 | 26 -> 25 | 2 |
   | prijswissel | 12 | 0 | 167 -> 58 | 15 |
   | pro-communicatie | 8 | 1 | 165 -> 111 | 11 |
   | sleutels | 2 | 0 | 143 -> 138 | 13 |
   | terugwinactie | 14 | 0 | 331 -> 167 | 8 |
   | wintergids | 17 | 0 | 302 -> 222 | 40 |
   | zapier | 0 | 0 | 22 -> 22 | 7 |

   Samen 129 punten naar het archief, 2.704 naar 1.477 regels. "Open" telt ook open subpunten; dat aantal is
   voor en na gelijk. In de proefversies komt nergens een regel bij, geen drie witregels op rij, elk bestand eindigt
   met een regeleinde.
3. Regel in de globale CLAUDE.md (`claude/CLAUDE.md`, bij "In `~/Development/_backlogs/` schrijft een sessie ..."):
   "Afgevinkte punten in een onderwerpbestand mogen naar `<repo>/archief/<onderwerp>.md`, alleen met
   `claude/scripts/backlog_archief.py`, nooit met de hand. Een sessie mag dat voor haar eigen onderwerp doen; alle
   onderwerpen tegelijk alleen op verzoek van Hans. Staat iets niet (meer) in het onderwerpbestand, kijk dan in het
   archief." De regel voor `BACKLOG.md` van eigen projecten (alleen aanvullen of afvinken) blijft (zie vraag B).
4. Vastleggen in ai-engineering-docs: CHANGELOG.md (ook de nog ontbrekende regel voor 99ca2b2 van vandaag) en
   docs/decisions.md. In `_backlogs`: STAND en VOLGENDE STAP van backlog-ordening.

## Volgorde

1. Na akkoord: dit plan committen op `hans/backlog-archief`.
2. Script en test committen (test groen).
3. Proefrun opnieuw (bestanden veranderen door de terminals), dan `write` op de 16 bestanden, uitvoer bewaren.
4. Regel, CHANGELOG en decisions; commit; lokaal mergen in main van ai-engineering-docs (niet pushen: de repo is
   openbaar, besluit Hans 9 nov). Worktree en branch daarna weg.

## Tests

- `python3 claude/scripts/test_backlog_archief.py`: 19 gevallen groen (14 eerst, 5 na Codex): alleen afgevinkte hoofdpunten gaan; open
  punten en subpunten blijven in volgorde; afgevinkt met open subpunt blijft; vervolgregels (ingesprongen, vet,
  notities) gaan mee; witregels kloppen (geen dubbele, lijst zonder witregels blijft dicht, laatste punt weg met
  regeleinde); koppen en tekst blijven; archief met kop per groep; tekst op kolom 0 stopt; alinea's plakken niet
  aan elkaar; schrijven en tweede run (niets dubbel); herstart na een crash vóór het vervangen; een terminal die
  tijdens de run een punt toevoegt (bestand blijft staan, tweede run maakt het af, het nieuwe punt blijft); alleen
  onderwerpbestanden; proefrun schrijft alleen in de proefmap. Na Codex: open subpunt met `*` of `1.` blijft;
  vervolg en open subpunt na een witregel horen bij het punt; terminal schrijft vlak vóór het vervangen (versie
  van de terminal komt terug, geen hulpbestanden achter); herstart met intussen een extra afgevinkt punt (niets
  dubbel); proefrun in de backlogmap stopt.

## Verificatie

- Uitvoer van `write`: per bestand "archived n", geen SKIPPED; het script controleert zelf open punten en
  weggehaalde regels.
- Daarna los: aantal open punten per bestand gelijk aan de proefrun; in elk archief de afgevinkte punten precies één
  keer; `git -C ~/Development/_backlogs status --short` toont de nieuwe archiefbestanden (nog niet in git) en
  `git diff --stat` alleen weggehaalde regels in de onderwerpbestanden (vóór de volgende uursnapshot).
- "Nog te doen" van de prijswissel blijft dezelfde 10 punten: getest met `nogTeDoen` uit
  `git show origin/main:scripts/prijswissel-4995/regels.mjs` op het nieuwe prijswissel.md (de hoofdmap van AIvoorRED
  staat nog op een oude branch waar stand.mjs TODO.md leest, dus niet die versie gebruiken).
- Notch toont de map `archief/` niet (scant alleen `_backlog_*.txt` in de hoofdmap, `BacklogParser.scan`).

## Impact

- Terminals die een onderwerpbestand in hun context hebben: hun volgende Edit faalt één keer (bestand veranderd) en
  ze lezen het opnieuw. Wie een afgevinkt punt zoekt, vindt het in het archief.
- De verify van de scripts voor stap 3c en 3d (AIvoorRED) slaagt daarna niet meer (de verhuisde blokken staan niet
  meer letterlijk in de bestanden); verwacht, beide stappen zijn af.
- Persoonsgegevens: het archief bevat dezelfde tekst als nu, in dezelfde privémap; geen nieuwe plek.
- Let op bij prijswissel: het afgevinkte punt "Op of na 7 nov: kijken of het lid ... de maandbundel houdt; idem na
  3 dec en 6 dec" is afgevinkt omdat het ochtendbericht het deed, en dat staat sinds 9 nov uit. Het open punt
  "Besluit Hans: bewaking nu het ochtendbericht uit staat" dekt dat; na het archiveren staat de uitleg in het archief.

## Losse vragen aan Hans

A. Klantzaken heeft na het archiveren 0 open punten. Volgens de regel van vandaag ("klaar is weg"): de rij
   `_backlog_aivoorred klantzaken.txt` en het onderwerpbestand weghalen (het archief blijft)?
B. Ook `BACKLOG.md` van eigen projecten (bijvoorbeeld Zoom Alerts, 2.873 regels) zo archiveren? Voorstel: nu niet,
   eerst zien hoe het bij de onderwerpbestanden bevalt.

## Codex-toets

Ronde 1 (gpt-6-astra, xhigh, 10 nov 14:46), zeven bevindingen, alle zeven in de code nagelopen en overgenomen:

1. P1, een terminal die precies tussen de laatste controle en het vervangen schrijft, verliest zijn punt. Klopt.
   Overgenomen: een harde link houdt het vervangen bestand vast; schreef iemand erin, dan komt zijn versie terug en
   stopt het script voor dat bestand (test). Restrisico (iemand zet in diezelfde microseconden een heel nieuw bestand
   neer) staat hierboven.
2. P2, de herstart herkende het archief per run in plaats van per punt, zodat een punt na een herstart met een extra
   afgevinkt punt dubbel kon komen. Klopt. Overgenomen: per punt (test).
3. P2, een vervolg of open subpunt na een witregel raakte los van zijn punt. Klopt in het script; in de echte
   bestanden komt het nu niet voor (nagekeken). Overgenomen (test).
4. P2, open subpunten met `*`, `+` of `1.` werden niet als open herkend en gingen mee. Klopt. Overgenomen (test).
5. P2, een proefrun met de backlogmap als uitvoermap overschreef de bestanden. Klopt. Overgenomen: weigert (test).
6. P2, de controle met stand.mjs zou in de hoofdmap van AIvoorRED de oude versie gebruiken die TODO.md leest.
   Klopt. Overgenomen: controle met de versie van origin/main (zie Verificatie).
7. P3, `git diff` toont nieuwe (nog niet vastgelegde) archiefbestanden niet. Klopt. Overgenomen: `git status`.

Geen tweede ronde: alles is overgenomen en raakt het script en de controle, niet de aanpak.

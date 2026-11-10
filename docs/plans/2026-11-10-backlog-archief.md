# Plan: afgevinkte punten uit de onderwerpbestanden halen, zoals het team doet

Status: v3 (na twee Codex-rondes), goedgekeurd door Hans op 10 nov 2026 ("akkoord"); eigen projecten: de regel geldt
vanaf nu, bestaande afgevinkte punten verhuist een sessie in dat project op verzoek van Hans. Branch `hans/backlog-archief` (worktree
`~/Development/ai-engineering-docs/ai-engineering-docs-archief`). v2 (archief per onderwerp) was goedgekeurd; Hans
koos daarna (10 nov) voor de werkwijze van Theske en Maarten zonder archiefbestand, dus v3 vervangt v2.

## Aanleiding

Hans (10 nov): "waarom zou ik alle afgevinkte punten bewaren?" De onderwerpbestanden in `~/Development/_backlogs/`
groeien door afgevinkte punten: 129 afgevinkte hoofdpunten in de bestanden van AIvoorRED. Theske en Maarten halen
afgeronde punten weg uit TODO.md; bovenaan TODO.md staat "Afgeronde punten staan in CHANGELOG.md; hier alleen wat
nog moet gebeuren" (nu 7 afgevinkt tegen 29 open). Besluit Hans: dezelfde werkwijze voor zijn punten, geen
archiefbestand; wat in CHANGELOG komt moet duidelijk zijn. Eigen projecten: afgevinkte punten verhuizen naar de eigen
CHANGELOG.

## Wat er verandert

1. Script `claude/scripts/backlog_opschonen.py` (vervangt `backlog_archief.py` op deze branch), met test
   `claude/scripts/test_backlog_opschonen.py`:
   - Werkt alleen op onderwerpbestanden `~/Development/_backlogs/<repo>/<onderwerp>.md`; weigert korte rijen en
     kladblokken (`_backlog_*.txt`) en alles daarbuiten.
   - Haalt een afgevinkt hoofdpunt (`- [x] ...` op kolom 0) weg met zijn vervolgregels: ingesprongen regels, ook na
     een witregel; het punt eindigt bij het volgende `- `-punt, een kop of tekst op kolom 0.
   - Blijft staan: open punten, afgevinkte subpunten onder een open punt, een afgevinkt punt met nog een open
     subpunt (elk lijstteken: `-`, `*`, `+`, `1.`), en alle andere tekst (WAAR, STAND, koppen, intro's).
   - Een witregel gaat mee als het punt tussen witregels stond; alinea's plakken nooit aan elkaar. Tekst op kolom 0
     direct onder een afgevinkt punt: het hele bestand wordt overgeslagen.
   - Vangnet: het script raakt alleen een bestand aan dat precies zo al in de git van `_backlogs` staat (uurtaak).
     Anders: "wacht op de volgende snapshot". Zo staat de volledige tekst van elk weggehaald punt altijd in git; het
     script meldt per bestand de commit (`git -C ~/Development/_backlogs show <commit>:<repo>/<onderwerp>.md`).
   - Veiligheid: vervangen alleen als het bestand nog is wat er gelezen werd. Een harde link houdt het vervangen
     bestand nog 2 seconden vast; schrijft een terminal er rond het vervangen in (ook een die het al open had), dan
     bewaart het script die versie buiten `_backlogs` (`$TMPDIR/backlog-opschonen-herstel/`) en zet hem terug als
     niemand intussen in het nieuwe bestand schreef; schreven er twee, dan blijven beide versies bewaard en meldt het
     "samenvoegen met de hand". Restrisico: een terminal die in dezelfde microseconden een heel nieuw bestand neerzet.
     De gemelde commit is dezelfde als waarmee de tekst vergeleken is.
     Daarna controleert het dat alle open punten er nog zijn, in dezelfde volgorde, en dat elke weggehaalde regel in
     de vastgelegde versie staat. Een slot voorkomt twee runs tegelijk; een proefrun schrijft alleen buiten
     `_backlogs`.
2. Eenmalige run op de onderwerpbestanden van AIvoorRED. Proefrun 10 nov (alle bestanden staan al in git):

   | Bestand | Weg | Blijft (afgevinkt met open subpunt) | Regels | Open |
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
   | zapier, sendgrid-bewaking (nieuw, andere terminal) | 0 | 0 | gelijk | 7, 3 |

   Samen 129 weg, 2.704 naar 1.477 regels; het aantal open punten (ook subpunten) blijft per bestand gelijk.
3. Klantzaken (vraag A, ja): na de run 0 open punten; de rij `_backlog_aivoorred klantzaken.txt` en het
   onderwerpbestand gaan weg, maar alleen als `git status` direct ervoor laat zien dat beide precies zo in git staan
   (anders wachten op de uursnapshot).
4. AIvoorRED (worktree, commit, Hans pusht):
   - CHANGELOG.md: één duidelijke regel per onderwerp (keuze Hans: "ja eens"): hoeveel afgevinkte punten eruit
     gingen, dat ze afgerond waren (veel hebben een eigen CHANGELOG-regel van toen), en waar de volledige tekst staat
     (`git -C ~/Development/_backlogs show <commit>:aivoorred/<onderwerp>.md`, privé). Geen klantgegevens.
   - CLAUDE.md r. 79: één zin dat Hans' afgeronde punten net als in TODO.md een regel in CHANGELOG krijgen en daarna
     uit het onderwerpbestand gaan (met het script).
   - HANDOFF.md: de rij klantzaken eruit.
5. Regels in de globale CLAUDE.md (`claude/CLAUDE.md`):
   - Tabel, rij BACKLOG.md (eigen projecten): "Alleen aanvullen, nooit herschrijven. Een afgerond punt verhuist naar
     CHANGELOG.md (onder de datum: wat er gedaan is en het bewijs) en gaat dan uit BACKLOG.md." In plaats van "alleen
     aanvullen of afvinken; afgevinkt punt krijgt een regel in CHANGELOG.md".
   - Bij `~/Development/_backlogs/` (teamrepo): "Een afgerond punt in een onderwerpbestand krijgt een duidelijke
     regel in de CHANGELOG van de teamrepo (wat, wanneer, bewijs; geen klantgegevens) en gaat daarna uit het
     onderwerpbestand, alleen met `claude/scripts/backlog_opschonen.py` (de tekst blijft in git van `_backlogs`);
     zoals Theske en Maarten het in TODO.md doen."
   - Dezelfde regel op de andere plekken die nog "afvinken" voorschrijven: de inleiding van "Vastleggen" ("alleen
     verdwijnen door het bewust af te vinken"), `claude/CLAUDE.md` r. 163 ("punt afvinken in BACKLOG.md"),
     `claude/docs/project-setup.md` r. 71 en 118, en de uitleg op de site `deel-03.html` r. 229 en 233.
   - Bestaande afgevinkte punten in eigen projecten (bijvoorbeeld Zoom Alerts: 322 afgevinkt, 78 open) verhuist een
     sessie in dat project naar de eigen CHANGELOG, op verzoek van Hans; niet vanuit deze terminal (elk project heeft
     een eigen repo en CHANGELOG-opmaak). Open punt in backlog-ordening.
6. Vastleggen in ai-engineering-docs: CHANGELOG.md (ook de ontbrekende regel voor 99ca2b2 van vandaag) en
   docs/decisions.md. In `_backlogs`: STAND en VOLGENDE STAP van backlog-ordening.

## Volgorde

1. Na akkoord: plan v3, script en test committen op `hans/backlog-archief`.
2. Proefrun opnieuw; die geeft per bestand de commit waarin de volledige tekst staat.
3. Eerst de CHANGELOG (Codex: de regel komt vóór het weghalen): AIvoorRED-worktree, CHANGELOG met die commits,
   CLAUDE.md en HANDOFF; commit en build (nog niet gepusht).
4. Dan `write`; slaat het script een bestand over, dan de CHANGELOG-regel daarvan aanpassen vóór de push.
5. Controle (zie Verificatie); klantzaken weghalen; Hans pusht AIvoorRED.
6. ai-engineering-docs: regels, CHANGELOG, decisions; commit; lokaal mergen in main (niet pushen, besluit 9 nov).
7. Worktrees en branches weg (Hans).

## Tests

- `python3 claude/scripts/test_backlog_opschonen.py`: 21 gevallen groen (3 na ronde 2: een schrijver die het oude
  bestand open had en na het vervangen schrijft; twee schrijvers tegelijk, beide versies blijven; proefrun via een
  symlink naar de backlogmap stopt), met een eigen wegwerp-git zoals de
  uurtaak: alleen afgevinkte hoofdpunten gaan; open punten en subpunten blijven in volgorde; afgevinkt met open
  subpunt blijft (ook `*` en `1.`); vervolgregels gaan mee, ook na een witregel; witregels kloppen; koppen en tekst
  blijven; tekst op kolom 0 stopt; alinea's plakken niet aan elkaar; schrijven en tweede run, met de volledige tekst
  in git; een bestand dat nog niet in git staat of erna veranderde wacht; een terminal die vóór de controle of vlak
  vóór het vervangen schrijft (zijn punt blijft, geen hulpbestanden achter); alleen onderwerpbestanden; proefrun
  alleen in de proefmap, niet in de backlogmap.

## Verificatie

- Uitvoer van `write`: per bestand "removed n" met de commit, geen SKIPPED.
- Daarna: open punten per bestand gelijk aan de proefrun; `git -C ~/Development/_backlogs diff --stat` toont alleen
  weggehaalde regels; voor elk bestand staat elk weggehaald punt in `git show <commit>:<bestand>`.
- "Nog te doen" van de prijswissel blijft dezelfde 10 punten: getest met `nogTeDoen` uit
  `git show origin/main:scripts/prijswissel-4995/regels.mjs` op het nieuwe prijswissel.md (niet de oude versie in
  de hoofdmap van AIvoorRED, die TODO.md leest).
- Notch: geen verandering in de rijen behalve klantzaken weg.

## Impact

- De afgevinkte tekst staat daarna alleen nog in de git van `_backlogs` (privé, elk uur gepusht naar
  `han-s-kl/backlogs`); in de CHANGELOG van AIvoorRED staat per onderwerp hoe je hem terugvindt.
- Terminals met een onderwerpbestand in hun context: hun volgende Edit faalt één keer (bestand veranderd) en ze lezen
  opnieuw.
- De verify-scripts van stap 3c en 3d (AIvoorRED) slagen daarna niet meer; verwacht, beide stappen zijn af.
- Prijswissel: het afgevinkte punt over de controles na 3 en 6 dec (door het ochtendbericht, dat uit staat) gaat
  eruit; het open punt "Besluit Hans: bewaking nu het ochtendbericht uit staat" dekt dat.

## Codex-toets

Ronde 1 (op v2, archief per onderwerp; 10 nov 14:46): zeven bevindingen, alle zeven nagelopen en overgenomen: schrijver
op het laatste moment (harde link), herkenning per punt bij een herstart (vervalt in v3, er is geen archief meer),
vervolg na een witregel, andere lijsttekens, proefrun in de backlogmap, stand.mjs-versie bij de controle, `git
status` voor nieuwe bestanden (vervalt in v3).

Ronde 2 (op v3, 10 nov 15:14): zeven bevindingen, alle zeven nagelopen en overgenomen:

1. P1, een schrijver die het oude bestand al open had en pas na de laatste controle schreef, raakte zijn tekst kwijt.
   Klopt (een smal venster). Overgenomen: de harde link blijft 2 seconden staan en wordt dan opnieuw gelezen (test).
2. P1, bij twee schrijvers tegelijk kon het terugzetten één versie overschrijven. Klopt. Overgenomen: de andere
   versie wordt altijd buiten `_backlogs` bewaard, terugzetten alleen als het nieuwe bestand onaangeroerd is, anders
   "samenvoegen met de hand" (test).
3. P2, een proefrun via een symlink in de proefmap kon het echte bestand overschrijven. Klopt. Overgenomen (test).
4. P2, de gemelde commit was niet per se de commit waarmee vergeleken werd. Klopt. Overgenomen: één commit.
5. P2, het weghalen van klantzaken viel buiten het vangnet. Klopt. Overgenomen: `git status` direct ervoor.
6. P2, de punten gingen weg vóór de CHANGELOG-regel. Klopt. Overgenomen: volgorde omgedraaid.
7. P2, vier andere plekken schrijven nog "afvinken" voor. Klopt. Overgenomen (punt 5 van "Wat er verandert").

Geen derde ronde: de bevindingen gingen over randgevallen en volgorde, niet over de aanpak, en zijn alle verwerkt.

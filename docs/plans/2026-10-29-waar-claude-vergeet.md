# Plan: hoofdstuk "Waar Claude vergeet" en regels om vergeten te voorkomen

Datum: 29 oktober 2026. Aanvrager: Hans. Status: goedgekeurd door Hans op 29 okt ("akkoord"), v2 (Codex-plantoets r1 verwerkt, zie onderaan).

## Aanleiding

Uit de praktijk (een lange werksessie met meerdere projecten) bleek waar Claude afspraken, keuzes en werkwijzen
kwijtraakt. Hans wil dit algemeen vastleggen, zonder projectspecifieke voorbeelden, zodat hij het aan anderen kan
meegeven via deze gids. Akkoord op de opzet: Hans, 29 okt ("ja").

Daarnaast spreekt de gids zichzelf tegen: deel 3 (De 5 Lagen) raadt aan "beslissingen, project IDs, procedures" in het
geheugen te zetten (`deel-03.html` r. 60, 63 en 188-194), terwijl `claude/CLAUDE.md` zegt dat memory een cache is en
geen archief.

## Besluiten (Hans, 29 okt)

1. Een eigen hoofdstuk, onder Werkwijze na Veelgemaakte Fouten (niet als uitbreiding van deel 18).
2. Algemeen geformuleerd: geen namen van projecten, klanten of tools van Hans; voorbeelden neutraal ("een bestand in
   een sync-map", "een andere sessie past hetzelfde bestand aan").
3. Deel 3 wordt rechtgezet: memory is een cache, geen archief.
4. Nieuwe regels in `claude/CLAUDE.md` (de globale regels die `setup.sh` installeert).

## Wijzigingen

### 0. Inrichting van deze repo (ontbreekt nu)

De repo heeft geen `.gitignore`, `CHANGELOG.md`, `docs/decisions.md`, `docs/plans/` of `AGENTS.md`, terwijl de eigen
regels die voor elk project vragen. Minimaal voor deze wijziging:
- `.gitignore` met `logs/codex/` (de Codex-toets schrijft daar) en `.DS_Store`.
- `docs/plans/` met dit plan.
- `CHANGELOG.md` (nieuwste bovenaan) en `docs/decisions.md` (tabel met waarom en verworpen), met een eerste regel
  voor deze wijziging.
- Een compacte root-`CLAUDE.md` voor deze repo (wat de gids is, opbouw van een pagina: head, zijnav, section, pager;
  regels: nav en pager in alle pagina's bijwerken, geen gedachtestreepjes, geen projectnamen in algemene hoofdstukken,
  `claude/` is de bron van wat `setup.sh` installeert). Het AGENTS-sjabloon verwijst naar een root-`CLAUDE.md`; die
  bestond hier niet (Codex r1 P2-4).
- `AGENTS.md` uit `claude/AGENTS.md.template`, verwijzend naar die root-`CLAUDE.md`.
- `BACKLOG.md` met de losse punten die uit dit plan komen (zie 6). Geen `HANDOFF.md`.

### 1. Nieuw hoofdstuk `deel-19.html` "Waar Claude vergeet"

Zelfde opmaak als de andere delen (kopie van de structuur van `deel-18.html`: head, nav, `section`, `h2` met
`DEEL 19`, callouts `co ci` / `co cw`, pager). Inhoud:

**Inleiding.** Claude onthoudt niets tussen sessies behalve wat in bestanden staat, en ook binnen een sessie is
onthouden niet hetzelfde als toepassen. Instructies zijn probabilistisch, hooks en tests deterministisch (verwijzing
naar deel 3 en 6).

**De negen zwakke plekken.** Per plek: wat je ziet, waarom het gebeurt, wat helpt.
1. Het gesprek is tijdelijk. `/clear` wist de context helemaal; `/compact` vat hem samen, en welke details daarbij
   wegvallen ligt niet vast (vaak juist het waarom en de voorwaarden; met focus-instructies stuur je wat blijft).
   Helpt: vastleggen op het moment dat het ontstaat (Codex r1 P3-9).
2. Weten is niet toepassen: een regel die bij een specifieke handeling hoort (versturen, publiceren, deployen,
   migreren) wordt gemist als hij in een algemeen document staat. Helpt: de regel in de skill of het script van die
   handeling, of een hook.
3. Verouderde kennis: Claude werkt met wat hij eerder in de sessie las, terwijl het bestand intussen veranderd is
   (een andere sessie, de gebruiker zelf, een sync-map). Helpt: vlak voor schrijven opnieuw lezen en vergelijken; nooit
   een heel bestand uitschrijven vanuit een eerdere lezing.
4. Parallelle sessies weten niets van elkaar. Twee sessies in dezelfde map delen bestanden, index en actieve branch:
   een eigen branch alleen isoleert niets. Helpt: afspraken alleen via bestanden; per sessie een eigen worktree
   (eigen map) met een eigen branch (verwijzing naar deel 14) (Codex r1 P2-2).
5. Een keuze zonder waarom, of een besluit dat niet wordt teruggelezen, komt terug: Claude stelt een eerder verworpen
   optie opnieuw voor. Vastleggen alleen is niet genoeg. Helpt: besluitenlog met waarom en verworpen alternatieven,
   en een vaste terugleesstap: vóór een ontwerpkeuze of voorstel het besluitenlog, de backlog en de relevante docs/refs
   doorzoeken op het onderwerp (Codex r1 P2-3).
6. Terloopse afspraken: een deadline, uitzondering of voorkeur die in een bijzin valt, wordt toegepast maar niet
   vastgelegd. Helpt: regel dat zo'n afspraak meteen naar het bestand gaat waar hij geldt.
7. Standaardgedrag sluipt terug, vooral in lange sessies en bij tegenstrijdige regels (globaal tegenover project).
   Helpt: tegenstrijdigheden een keer laten beslissen; de belangrijkste regels als hook.
8. Subagents en andere modellen kennen het gesprek niet; een second-opinion-model leest vaak een ander
   instructiebestand. Helpt: afspraken expliciet in de opdracht en in `AGENTS.md`.
9. Toezeggingen verdwijnen: "ik kom erop terug" werkt alleen zolang de sessie loopt. Helpt: toezeggingen voor na de
   sessie direct naar de backlog.

**De rangorde van maatregelen** (sterk naar zwak): hook of test; een controle in de tool zelf; de regel op de plek van
de handeling (skill, script, checklist); CLAUDE.md, docs/refs en besluitenlog; memory. Met de kanttekening dat een hook
alleen bewaakt wat hij matcht (welke tool, welke schrijfwijze van een commando) en een test alleen telt als hij
verplicht draait (pre-commit, CI). Test je hook dus met de varianten die je wilt tegenhouden (Codex r1 P2-1).

**Tijdelijke plekken om in de gaten te houden:** het gesprek, memory, HANDOFF.md, plannen in `~/.claude/plans/`, de
scratchpad of tijdelijke map van een sessie, tijdelijke worktrees, en losse instellingen of skills in `~/.claude/` die
niet in git staan. Vuistregel: wat moet blijven, staat nooit alleen op zo'n plek.

**Checklist (tien vragen)** om je eigen inrichting na te lopen, bijvoorbeeld: Staat elke regel voor een specifieke
handeling in de skill of het script van die handeling? Bestaat er een besluitenlog met waarom? Staat
`~/.claude/settings.json` in git (zonder geheimen)? Krijgen subagents de afspraken mee?

Lengte: vergelijkbaar met deel 18 tot deel 14; geen projectvoorbeelden.

### 2. `deel-03.html` rechtzetten (laag 4)

- r. 60: de beschrijving van laag 4 wordt "cache: alleen verwijzingen naar waar iets staat; de inhoud staat in git".
- r. 63, de vuistregel: "Context die niet in code of git staat? → memory" wordt "→ docs/refs of het besluitenlog;
  memory hooguit als verwijzing".
- r. 188-194 (laag 4): de tekst over beslissingen en procedures in memory wordt herschreven in dezelfde lijn, met een
  verwijzing naar deel 19.

### 3. `claude/CLAUDE.md` (globale regels)

In de sectie "Vastleggen" en "Signalen", kort en zonder projectnamen:
- Situatieregels op de plek van handelen: een regel die bij een handeling hoort, staat in de skill of het script van
  die handeling; docs/refs legt uit waarom.
- Vlak voor schrijven opnieuw lezen en vergelijken met wat je eerder las; nooit een heel bestand uitschrijven vanuit een
  eerdere lezing.
- Terloopse afspraken (deadline, uitzondering, voorkeur) zijn afspraken: meteen vastleggen waar ze gelden.
- Toezeggingen voor na de sessie direct naar BACKLOG.md.
- Tegenstrijdige regels (globaal en project) niet zelf beslechten: melden, de gebruiker beslist een keer, het besluit
  in de project-CLAUDE.md.
- Subagents en andere modellen krijgen de relevante afspraken expliciet in de opdracht.
- Terugleesstap: vóór een ontwerpkeuze of voorstel het besluitenlog, BACKLOG.md en de relevante docs/refs doorzoeken
  op het onderwerp (Codex r1 P2-3).
- Aanscherpen van de bestaande memory-regel: memory bevat alleen verwijzingen. De regel over feedback van de gebruiker
  ("direct vastleggen in dit bestand (sectie Stijl) of in memory", r. 51) verliest "of in memory" (Codex r1 P2-7).
CLAUDE.md blijft compact: per regel een zin, de uitleg staat in deel 19.

### 4. Navigatie en pager

- Alle 17 pagina's van de gids met de zijnav: na `deel-18.html` de link `deel-19.html` "Waar Claude vergeet".
  `plannen/zoom-nl-code-readiness.html` heeft een eigen slide-menu en teller (`1 / 12`) en hoort niet bij de reeks: die
  blijft ongewijzigd (Codex r1 P2-5).
- Pager: deel 19 wordt 12; deel 22 t/m de begrippenlijst schuiven een op; overal "/ 17" wordt "/ 18".
  Vorige/volgende: deel 18 volgende → deel 19; deel 19 vorige → deel 18, volgende → deel 22; deel 22 vorige → deel 19.
- Scriptmatig met een controle achteraf (elke pagina een link naar deel 19, tellers 1 t/m 18 uniek en oplopend).

### 4b. Handmatige installatie in `deel-22.html`

Stap 2 van de handmatige installatie bevat een eigen, al verouderde kopie van de globale regels (r. 89-171). Die kopie
gaat eruit; in plaats daarvan een download van `claude/CLAUDE.md` uit de repo (dezelfde bron als `setup.sh`), zodat
beide installatieroutes dezelfde regels opleveren en er geen tweede versie meer is (Codex r1 P2-6).

### 4c. Bestaande kapotte links

- `index.html` r. 104 verwijst naar `zoom-nl-code-readiness.html` in de root; wordt `plannen/zoom-nl-code-readiness.html`.
- `deel-03.html` r. 274 verwijst naar het ontbrekende anker `#feedback-loop`; naar het bestaande kopje laten wijzen of de
  link verwijderen (Codex r1 P2-8).

### 5. Niet in scope

- De starter-kit-zip: die bevat een eigen minimale `global/CLAUDE.md` (maart 2026) en wordt niet door `setup.sh`
  gebruikt; `setup.sh` installeert `claude/CLAUDE.md`. Ongewijzigd laten; eventueel later apart bijwerken.
- `setup.sh` zelf: geen wijziging nodig.

## Verificatie

- Elke HTML-pagina parseert (geen kapotte tags), alle interne links en ankers bestaan (ook `#fragment`), elke
  gidspagina linkt naar deel 19, tellers 1 t/m 18 zonder dubbel of gat (klein Python-script).
- Geen gedachtestreepjes (em/en dash) in nieuwe of gewijzigde tekst; geen projectnamen in deel 19 (zoek op een lijst
  namen).
- Visueel: `deel-19.html` lokaal openen in de browser, desktop en smal (mobiel).
- `claude/CLAUDE.md` blijft onder ~200 regels.
- Hans leest deel 19 en de CLAUDE.md-diff voor de merge.

### 6. Losse punten naar BACKLOG.md

- `claude/hooks/pretool-guard.sh` blokkeert `git push` maar niet `git -C <map> push` (Codex r1, getest met alleen de
  commandotekst). Het hoofdstuk noemt dit soort gaten in het algemeen; de fix van de guard is een eigen wijziging met
  een test per variant.
- De starter-kit-zip (maart 2026) loopt achter op `claude/`.

## Codex-plantoets r1 (29 okt, log `logs/codex/20261029-161824-68146-plan.md`)

Alle negen punten nagelopen in de repo en overgenomen: P2-1 rangorde genuanceerd (hook dekt alleen wat hij matcht,
test alleen als verplicht; guard-gat naar BACKLOG); P2-2 worktree in plaats van branch; P2-3 terugleesstap als regel en
in het hoofdstuk; P2-4 root-`CLAUDE.md` voor deze repo; P2-5 de plannen-pagina blijft buiten de reeks; P2-6 de
ingesloten kopie in deel 22 wordt een verwijzing naar `claude/CLAUDE.md`; P2-7 "of in memory" eruit; P2-8 twee
bestaande kapotte links mee hersteld en ankers in de controle; P3-9 `/clear` en `/compact` onderscheiden.
Stoppunt: geen tweede ronde op het plan; wel een review van de diff voor de merge.


# Globale instructies

Bron: https://github.com/hklplrhft/ai-engineering-docs (map `claude/`). Dit bestand is een symlink of kopie daarvan; wijzig het in de repo, niet hier.

## Taal
- Communiceer in het Nederlands
- Code, commits en comments in het Engels

## Modellen
- Alle projecten (behalve zoom-nl): **Claude op xhigh** als leidend model (standaard Fable 5; Opus of een ander Claude-model verandert hier niets aan), **Codex `gpt-6-astra` op xhigh** als second opinion (de Codex-toets hieronder).
- **De leidende Claude-sessie beslist, welk Claude-model dat ook draait.** Elke Codex-bevinding is een hypothese tot die in de code is geverifieerd, en wordt daarna overgenomen of beargumenteerd verworpen (met de reden in CHANGELOG.md). Codex vindt bijna altijd iets als je opnieuw vraagt -- dat is zijn rol -- dus het aantal rondes en het stoppunt bepaalt Claude, niet Codex. Vuistregel: overnemen als het verandert wat een gebruiker ziet of krijgt, of als er zonder de fix iets onwaars getoond wordt; kleiner dan dat gaat als los punt naar BACKLOG.md.
- zoom-nl is de uitzondering en volgt zijn eigen afspraken.

## Werkwijze -- plan, verifieer, commit

### Altijd plannen voor doen
- `/plan` bij taken die meer dan 1 bestand raken of langer dan 5 minuten duren
- Geef verificatiecriteria mee: welke tests moeten slagen, welke output wordt verwacht
- Toets elk plan vóór de goedkeuring met een Codex-second-opinion: `scripts/codex_second_opinion.sh plan docs/plans/<naam>.md` -- kopieer het script uit `claude/scripts/` in ai-engineering-docs (of uit een project dat het al heeft) als het project het nog mist, en zet `logs/codex/` in .gitignore. Elk project heeft ook een `AGENTS.md` nodig (sjabloon: `claude/AGENTS.md.template`): Codex leest DAT bestand en niet CLAUDE.md, dus zonder die verwijzing toetst hij zonder de projectregels. Verwerk P1/P2-bevindingen in het plan of noteer waarom je ze verwerpt; elke Codex-bevinding is een hypothese tot je hem zelf in de code hebt geverifieerd
- Bij een beslissing met echte ontwerpvrijheid (nieuwe bron, API, laag, of een aanpak die nog niet vastligt) hoort EERST een open ronde: `scripts/codex_second_opinion.sh solve "<probleem, zonder onze oplossing>"`, VOORDAT het plan bestaat. Claude zet die ronde nooit zelf in -- hij stelt hem voor in dezelfde vraag waarin hij toch al om akkoord moet vragen voor die bron/aanpak, en de gebruiker beslist. De opbrengst is het VERSCHIL met onze eigen aanpak, niet de oplossing van Codex; convergentie telt als bevestiging, divergentie wijst de plek aan waar de echte keuze zit. Let op: na een `solve` heeft Codex zelf een aanpak bedacht, dus een latere `plan`-toets op een plan dat daarop leunt is zwakker dan een toets op een plan dat hij niet kent. Voor alles daaronder blijft het plan-toets-pad ongewijzigd.
- Wacht op goedkeuring voordat je begint met implementeren
- Na goedkeuring: kopieer het plan naar `docs/plans/YYYY-MM-DD-<naam>.md` in de repo en commit het. Plannen in `~/.claude/plans/` staan buiten git en gaan verloren.

### Context schoon houden
- Stel `/clear` voor bij taakwissel (andere feature, ander onderwerp)
- Stel `/compact` voor na 30+ minuten of wanneer context vol raakt
- Bij sessie-overdracht: maak een HANDOFF.md (doel, status, wat geprobeerd, eerstvolgende stap)

### Vastleggen -- vijf bestanden, elk met een eigen regel
Zo kan een afspraak, besluit of open punt alleen verdwijnen door het bewust af te vinken, nooit door herschrijven.

**Wat moet blijven, staat nooit ALLEEN op een tijdelijke plek.** Tijdelijk zijn: de sessie zelf (weg bij
`/compact` of `/clear`), memory (een cache, geen archief), `HANDOFF.md` (wordt herschreven), en losse teksten
als een PR-beschrijving, een commitbericht of een chatbericht. Een keuze, afspraak, regel, bevinding of taak
die daar blijft steken, is er over een week zonder dat iemand het merkt -- en niemand mist wat hij niet weet.
Dus: op het moment dat zoiets ONTSTAAT gaat het naar het bestand hieronder dat ervoor bestaat, niet aan het
eind van de sessie en niet 'straks even'. Daarna mag het overal genoemd worden; alleen daar staan mag niet.

| Bestand | Inhoud | Regel |
|---|---|---|
| `BACKLOG.md` | Alle open punten, vragen en bevindingen, geprioriteerd in secties | Alleen aanvullen of afvinken, nooit herschrijven. Afgevinkt punt krijgt een regel in CHANGELOG.md |
| `CHANGELOG.md` | Per datum wat er veranderd is: features, fixes, besluiten, bevindingen, wijzigingen in externe systemen | Alleen aanvullen, nieuwste bovenaan |
| `docs/decisions.md` | Besluitenlog: datum, besluit, waarom, verworpen alternatieven, wie | Alleen aanvullen. Elke ontwerpvraag die de gebruiker beantwoordt (AskUserQuestion, plan-keuze) krijgt een regel |
| `docs/plans/` | Goedgekeurde plannen | Nieuw bestand per plan, niet wijzigen na goedkeuring (afwijkingen in CHANGELOG.md) |
| `HANDOFF.md` | Momentopname voor de volgende sessie: waar sta je nu, wat is de eerstvolgende stap, hoe test je het lokaal | Mag herschreven worden, en WORDT dat ook. Daarom hoort hier niets in dat moet blijven: geen open punten (BACKLOG.md), geen afspraken of werkwijze-regels (dit bestand), geen besluiten (docs/decisions.md), geen lessen of valkuilen (docs/refs/). Zet je zoiets hier toch neer, dan verdwijnt het bij de eerstvolgende herschrijving zonder dat iemand het merkt |

- Geen TODO-lijsten in CLAUDE.md: dat bestand wordt elke sessie geladen en bij herschrijven vallen punten stilletjes weg.
- Feiten in CLAUDE.md en docs/refs/ (IDs, URLs, accounts, veldnamen) altijd met "gecontroleerd op <datum> via <bron>". Twijfel je aan een feit: vraag in BACKLOG.md, niet stilzwijgend aanpassen.
- Wijzigingen in externe systemen (Copernica, Cloudflare, App Store, DNS, databases): altijd een regel in CHANGELOG.md en bij voorkeur een herhaalbaar script in `scripts/`. Wat niet in git staat, bestaat niet.
- Memory (`~/.claude/projects/...`) is een cache, geen archief: alles wat telt staat ook in docs/refs/, BACKLOG.md of docs/decisions.md.
- Feedback van de gebruiker over de manier van werken (toon, lengte, volgorde, taal): direct vastleggen in dit bestand (sectie Stijl) of in memory, niet alleen toepassen.
- Werk BACKLOG.md, CHANGELOG.md en docs/decisions.md bij na elke afgeronde wijziging, vóór de commit.

### Git-discipline
- Werk op branches, niet direct op main
- Commit na elke voltooide wijziging -- herinner als er nog niet gecommit is
- Selectief committen: specifieke bestanden, niet `git add .`
- Nooit pushen, deployen of berichten sturen zonder expliciete bevestiging. Een globale hook blokkeert `git push`, deploy-commando's en destructieve git/shell-commando's; vraag de gebruiker die zelf te draaien met `! <commando>`
- Aan het eind van elke sessie: geen ongecommit werk laten staan (een Stop-hook controleert dit) en niet-gemergde branches benoemen in HANDOFF.md
- Secrets nooit in git; wel een `.env.example` met alle benodigde keys (zonder waarden) en in docs/refs/ waar de echte waarden staan

### Verificatie
- Waarschuw bij hallucinaties (onbekende packages, API's, functies) -- verifieer eerst
- Stel `git diff` voor bij grotere wijzigingen zodat de gebruiker kan reviewen
- Commit nooit code die de gebruiker niet begrijpt -- bied uitleg aan als de logica niet voor zich spreekt
- "Getest" betekent: een test of script in de repo dat iemand anders opnieuw kan draaien. Stel CI voor zodra de repo een remote heeft

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

### Vormgeving
- Bij design/vormgeving/UI aanpassingen: gebruik altijd de frontend-design skill
- Niet handmatig Tailwind/CSS classes bedenken maar de skill laten genereren
- Bij mobile app design (React Native, Flutter, iOS, Android): gebruik de mobile-app-design skill
- Volg platformspecifieke richtlijnen (iOS HIG, Material Design) zoals de skill voorschrijft

### Kwaliteitscontroles
- Geen secrets hardcoden -- gebruik environment variables of .env + .gitignore
- Review gegenereerde code op OWASP top 10 (SQL injection, XSS, command injection)
- Stel linters/typecheck voor als die ontbreken in het project

## Project-inrichting check
Bij het begin van een taak in een nieuw project, doorloop de volledige setup:
- Lees ~/.claude/docs/project-setup.md en doorloop alle stappen
- Stel elke stap voor aan de gebruiker voordat je begint met de eigenlijke taak
- Referentie: https://hklplrhft.github.io/ai-engineering-docs/index.html

Minimale check bij bestaande projecten (de SessionStart-hook meldt wat ontbreekt):
- CLAUDE.md van het actieve project (zo niet: stel `/init` voor)
- BACKLOG.md, CHANGELOG.md, docs/decisions.md (zo niet: stel voor ze aan te maken en TODO's uit CLAUDE.md/HANDOFF.md erheen te verhuizen)
- Hooks voor lint/typecheck (zo niet: stel voor om in te richten)
- docs/refs/ map voor littekens-documenten (zo niet: vermeld het bij terugkerende fouten)
- .gitignore met .env en secrets, en een .env.example (zo niet: waarschuw)

## Signalen -- wanneer ingrijpen
- Na 2 mislukte pogingen voor dezelfde taak: stel voor om te stoppen, `/clear`, en een betere prompt te formuleren
- Bij herhaling van eerder gemaakte fouten: stel voor om een regel/hook toe te voegen
- Bij vage opdrachten: vraag om specifieke bestanden, error output, of verwacht gedrag
- Bij grote wijzigingen zonder tests: weiger door te gaan totdat er verificatiecriteria zijn

## Signalen -- wanneer uitbreiden (5-lagen systeem)
Stel de volgende uitbreidingen voor wanneer het moment er is. Niet vooraf, maar zodra de situatie zich voordoet.
Referentie: https://hklplrhft.github.io/ai-engineering-docs/deel-03.html

### Tests (Laag 5) -- stel voor wanneer:
- Een bug wordt gefixt (regressietest verplicht)
- Er nog geen test-framework is maar er wel logica/functies zijn die kunnen breken
- De build slaagt maar de output niet klopt (golden file test)
- "Stel voor: zal ik een test-framework opzetten en een eerste test schrijven?"

### Hooks (Laag 5) -- stel voor wanneer:
- Dezelfde fout 2x voorkomt die een hook had kunnen voorkomen
- Er geen lint/format bij commit draait en er stijlfouten insluipen
- Secrets per ongeluk in code terechtkomen
- "Stel voor: zal ik een hook instellen die dit automatisch checkt?"

### Littekens/docs/refs (Laag 3) -- stel voor wanneer:
- Een fout wordt opgelost die niet vanzelfsprekend is
- Een API, service of patroon valkuilen heeft die je moet onthouden
- Dezelfde vraag over het project 2x wordt gesteld
- "Stel voor: zal ik dit vastleggen in docs/refs/ zodat dit niet nog een keer gebeurt?"

### Skills (Laag 5) -- stel voor wanneer:
- Een handeling regelmatig wordt herhaald (deploy, audit, release)
- Een complex proces meerdere stappen heeft die altijd hetzelfde zijn
- "Stel voor: zal ik hier een skill van maken zodat je het met een commando kunt uitvoeren?"

### Agents (Laag 5) -- stel voor wanneer:
- Een taak onafhankelijk en parallel kan draaien (bijv. content audit, link checker)
- Er een terugkerende controle is die bij elke wijziging moet draaien
- "Stel voor: zal ik hier een custom agent voor maken?"

### BACKLOG.md / CHANGELOG.md / docs/decisions.md (Laag 4) -- werk bij wanneer:
- Een wijziging is afgerond -> regel in CHANGELOG.md, punt afvinken in BACKLOG.md
- De gebruiker een ontwerpkeuze maakt -> regel in docs/decisions.md
- Een nieuw open punt, vraag of bevinding opduikt -> toevoegen aan BACKLOG.md (niet aan CLAUDE.md of HANDOFF.md)
- Iets buiten git verandert (extern systeem) -> CHANGELOG.md + script in scripts/

### HANDOFF.md (Laag 4) -- stel voor wanneer:
- Een sessie lang duurt en er onafgemaakt werk is
- De context vol raakt en er een `/compact` of `/clear` nodig is
- "Stel voor: zal ik een HANDOFF.md maken zodat de volgende sessie direct kan doorpakken?"

## Veiligheid
- Review shell commando's kritisch, vooral: rm -rf, git push --force, drop table
- Geen gevoelige data (API keys, wachtwoorden) in prompts of CLAUDE.md
- Stel nooit voor om hooks te skippen (--no-verify) of checks uit te schakelen

## Stijl
- Geen em-dashes of en-dashes in code of tekst, gebruik --
- Wees beknopt in uitleg, gedetailleerd in code
- Samenvattingen kort: eerst de conclusie in 3-5 regels, details alleen op verzoek of eronder

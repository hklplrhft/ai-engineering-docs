# Plan v4: privé backlogmap met back-up, per onderwerp in teamrepo's, één BACKLOG.md in eigen projecten (9 nov 2026)

Status: v4, goedgekeurd door Hans op 9 nov 2026 (back-up: privé GitHub-repo han-s-kl/backlogs, elk uur automatisch). Aanvulling 9 nov (Hans): in stap 5 ook `_backlog_zoomnl.txt` naar een Inbox in zoom-nl/BACKLOG-HANS.md; het lege `_backlog_zoom_LOGIN.txt` kan weg. v3 plus een privémap met git en privé-GitHub-back-up (Hans, 9 nov).

## Stap 1: privémap `~/Development/_backlogs/` (nieuw; NIET `_prive`, daar staan geheimen)
- Eigen git-repo; remote `han-s-kl/backlogs` (privé). Hans maakt de GitHub-repo zelf aan (`gh repo create ... --private`).
- Script `backlogs-snapshot.sh` (bron in ai-engineering-docs/claude/scripts/): commit alle wijzigingen; eerst
  gitleaks; bij een vondst niet committen en niet pushen, wel een macOS-melding; daarna push. Launchd-taak elk uur.
  Sessies committen niet zelf (geen botsingen in de git-index).
- Verhuizen van de zes `~/Development/_backlog_*.txt` (zoom alert, zoomnl, digitaal lezen, zoom_LOGIN, schoterpoort,
  overige_projecten), ongewijzigd: rijen in Notch dicht, Notch afsluiten, eerste commit met de huidige inhoud,
  verplaatsen, `backlogDirectory` in config.json naar `~/Development/_backlogs`, Notch starten, controleren dat alle
  rijen er zijn. Terugweg: Notch afsluiten, bestanden terug, config terug, starten.
- Wijziging in een extern systeem (launchd, GitHub): regel in CHANGELOG van ai-engineering-docs.

## Stap 2: regels (zodat nieuwe sessies het weten)
- Globale CLAUDE.md: één onderwerp per terminal; waar de backlog staat per soort project (eigen project: BACKLOG.md
  in de repo met Inbox; teamrepo: `~/Development/_backlogs/_backlog_<repo>-<onderwerp>.txt`; zoom-nl: eigen
  afspraken); opbouw van een onderwerp (WAAR, STAND, VOLGENDE STAP, OPEN PUNTEN, witregel tussen punten); bij de start
  lezen; aan het eind van elk werkmoment STAND en VOLGENDE STAP bijwerken met gerichte bewerkingen; in teamrepo's
  vervangt het onderwerpbestand de HANDOFF voor dat onderwerp (tabelregel HANDOFF en eindesessie-regel aangepast).
- AIvoorRED-CLAUDE.md: uitzondering op "open werk in TODO.md".

## Stap 3: AIvoorRED per onderwerp
3a. Claude maakt `_backlog_aivoorred-<onderwerp>.txt` voor a-bounces, sleutels, prijswissel, terugwinactie,
    wintergids, zapier, winback, artikelen-zoom01 en backlog-ordening; vult sleutels en backlog-ordening zelf.
3b. Elke terminal vult zijn eigen bestand en verhuist alleen de punten die zijn branch nieuw toevoegde (vaste
    opdracht om te plakken). Daarna kan Hans die terminal sluiten. Tot stap 4 klaar is: rij in Notch dicht houden als
    een terminal schrijft.
3c. Na het mergen van de vier branches (en een besluit over hans/landen-periode): Claude verhuist de oude gedeelde
    punten één keer vanuit main (lijst vooraf, Codex-toets van de concrete run, behoudscontrole).
3d. De sectie `### 49,95-groep Pro` gaat met kop naar het prijswissel-bestand; `stand.mjs` leest dat pad (stash B,
    aangepast, test).
3e. TODO.md houdt punten van anderen en gedeelde punten, met een verwijsregel.

## Stap 4: Notch veilig maken (repo notch, eigen branch, tests, Codex-review)
a. Vóór opslaan opnieuw lezen en op inhoud vergelijken; bij verschil niet schrijven (klein venster blijft).
b. Bij een conflict: concept blijft én gaat naar het klembord, met melding.
c. Volgorde op het volle pad; geen crash bij twee BACKLOG.md's.
d. Projectbacklog mag een bestandspad zijn (`docs/BACKLOG.md`), map erboven wordt bewaakt.
e. Bij een BACKLOG.md ook het aantal regels in de Inbox tonen.

## Stap 5: eigen projecten (na stap 4, want dan pas toont Notch meerdere BACKLOG.md's veilig)
- Per project (Zoom Alerts, digitaal-lezen, schoterpoort), na akkoord Hans: kladblok ongewijzigd naar
  `## Inbox (Hans)` onderaan BACKLOG.md; Notch toont die BACKLOG.md; regel in de project-CLAUDE.md over de Inbox.

## Stap 6: LOPEND opruimen
Pas als elke regel een gevulde bestemming heeft (ook single sign-on en wachtwoordreset in zoom-nl/BACKLOG-HANS.md).

## Verificatie
1. Stap 1: eerste commit bevat de zes bestanden ongewijzigd (hash per bestand); Notch toont alle rijen; de taak draait
   (log na een uur); een testbestand met een nep-sleutel wordt door gitleaks tegengehouden.
2. Stap 3: na 3b geen nieuwe punten van Hans in de TODO.md van de branches; na 3c behoudscontrole en `stand.mjs`.
3. Stap 4: `swift test` groen; handmatig conflict, slepen, directe update.
4. Stap 5: Inbox regel voor regel gelijk aan het kladblok.
5. Proef: nieuwe sessie leest `_backlog_aivoorred-sleutels.txt` en noemt de juiste volgende stap.

## Risico's
- Push naar GitHub elk uur: alleen privé, gitleaks vooraf; Hans geeft eenmalig toestemming voor deze taak.
- Tot stap 4 kan Notch een gelijktijdige wijziging overschrijven: rij dicht houden.
- Tot 3c staan oude punten nog in TODO.md.

## Codex
v2: zeven bevindingen, verwerkt (stap 4 a-e, 3b/3c, stap 6). v1: gedeelde git-index (sessies committen niet zelf),
migratie zonder terugweg (vaste volgorde met terugweg). Geen nieuwe planronde; Notch-code en de run van 3c krijgen
een eigen Codex-toets.

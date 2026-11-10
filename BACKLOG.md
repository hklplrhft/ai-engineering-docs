# BACKLOG

Open punten. Alleen aanvullen of afvinken; een afgevinkt punt krijgt een regel in CHANGELOG.md.

## Actiebaar

- [ ] **Verwijsregels in `~/Development/_backlogs/aivoorred/` weghalen** (10-11-2026, plan notch `2026-11-10-notities-en-onderwerpen`, fase 3) zodra alle AIvoorRED-terminals opnieuw gestart zijn (dan lezen ze de nieuwe regels en de starthook). Ook `checkout-app.md` daar, na de push van `hans/backlog` naar master van zoom-academy-gateway. De volledige teksten staan in de git van `_backlogs` (snapshot `eb0cb74`).
- [ ] **Hoofdmap `~/Development/AIvoorRED` terug op main** (uit `_backlogs/aivoorred/backlog-ordening.md`, 9 nov; fase 3 van plan notch `2026-11-10-notities-en-onderwerpen`). Staat op `hans/terugwinactie-za`, die inmiddels helemaal in main zit. Pas als Hans de terminals daar heeft gesloten: `git switch main`, `git merge --ff-only origin/main`, daarna de branch lokaal weg met akkoord.
- [ ] **Stop-hook laat `_backlogs` overslaan** (uit `backlog-ordening.md`, 9 nov): sessies committen daar niet zelf. Voorstel: repo's met een `.autocommit`-bestand overslaan in `claude/hooks/stop-git-check.sh`, plus een leeg `.autocommit` in `_backlogs`. Claude mocht de eigen hook niet aanpassen (9 nov); Hans doet het zelf of geeft toestemming.
- [ ] **Eigen projecten: afgevinkte punten van BACKLOG.md naar CHANGELOG.md** (uit `backlog-ordening.md`, regel 10 nov), per project door een sessie in dat project, op verzoek van Hans; grootste: Zoom Alerts (`aurora_monitor/docs/BACKLOG.md`: 322 afgevinkt, 78 open, 2.888 regels).
- [ ] **Persoonlijke regels uit de openbare `claude/CLAUDE.md` halen voor het pushen** (9-11-2026, besluit Hans: voorlopig niet pushen). Main staat lokaal 11+ commits voor op GitHub met de regels van 9 nov (backlogs per project, kladblokken, Notch, `~/Development/_backlogs`, projectnamen, de privé-repo `han-s-kl/backlogs`, en in `docs/decisions.md` dat `~/Development/_prive` geheimen bevat). De repo is openbaar. Voorstel: algemene regels openbaar houden, het persoonlijke deel naar een privébestand dat `claude/CLAUDE.md` inlaadt; de lokale commits herschrijven voordat ze online gaan. Tot dan: niet pushen.
- [ ] **`claude/hooks/pretool-guard.sh` blokkeert `git -C <map> push` niet** (29-10-2026, Codex-plantoets r1 bij het
  plan `docs/plans/2026-10-29-waar-claude-vergeet.md`, getest met alleen de commandotekst). `git push` wordt wel
  geblokkeerd. Fix met een test per variant (`git -C`, `git --git-dir`, push via een alias of script).
- [ ] **Starter-kit-zip bijwerken** (29-10-2026): `ai-engineering-starter-kit.zip` is van maart 2026 en loopt achter op
  `claude/` (onder meer de vastlegregels en deel 19).
- [ ] **Deel 22 stap 3 bevat een verouderde kopie van `claude/docs/project-setup.md`** (29-10-2026, bij de bouw van deel
  19 gezien: 84 tegen 172 regels). Net als stap 2 vervangen door een download uit `claude/`. Eventueel ook de hooks in
  latere stappen nalopen op ingesloten kopieen.
- [ ] **`codex_second_opinion.sh review` schrijft geen rapport als `scripts/codex_extract_report.py` ontbreekt**
  (29-10-2026). Het script zoekt de helper in `$REPO_ROOT/scripts/`; in deze repo staat hij in `claude/scripts/`, en
  projecten die alleen het `.sh`-bestand kopieerden, missen hem helemaal ("FAILED ... no answer written", het antwoord
  staat wel in het `.stream.log`). Oplossen: de helper naast het script zoeken (`$(dirname "$0")`) en in de
  installatie-instructie beide bestanden noemen.

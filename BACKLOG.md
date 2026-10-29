# BACKLOG

Open punten. Alleen aanvullen of afvinken; een afgevinkt punt krijgt een regel in CHANGELOG.md.

## Actiebaar

- [ ] **`claude/hooks/pretool-guard.sh` blokkeert `git -C <map> push` niet** (29-10-2026, Codex-plantoets r1 bij het
  plan `docs/plans/2026-10-29-waar-claude-vergeet.md`, getest met alleen de commandotekst). `git push` wordt wel
  geblokkeerd. Fix met een test per variant (`git -C`, `git --git-dir`, push via een alias of script).
- [ ] **Starter-kit-zip bijwerken** (29-10-2026): `ai-engineering-starter-kit.zip` is van maart 2026 en loopt achter op
  `claude/` (onder meer de vastlegregels en deel 19).
- [ ] **Deel 22 stap 3 bevat een verouderde kopie van `claude/docs/project-setup.md`** (29-10-2026, bij de bouw van deel
  19 gezien: 84 tegen 172 regels). Net als stap 2 vervangen door een download uit `claude/`. Eventueel ook de hooks in
  latere stappen nalopen op ingesloten kopieen.

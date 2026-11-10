#!/usr/bin/env python3
"""Tests for backlog_opschonen.py (plan docs/plans/2026-11-10-backlog-archief.md, v3).

Run: python3 claude/scripts/test_backlog_opschonen.py
"""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import backlog_opschonen as bo  # noqa: E402

TOPIC = """WAAR: test

STAND: test

OPEN PUNTEN

- [ ] open een
  vervolg van open een

- [x] klaar twee
  vervolg van twee
      (10 nov 2026, notitie)

- [ ] open drie
  - [x] afgevinkt subpunt blijft bij open drie

- [x] klaar vier, met open subpunt
  - [ ] nog open onder vier

### Uit TODO.md onder "Iets"

Intro van de sectie.

- [ ] open vijf
- [x] klaar zes
  **Gedaan:** vet en ingesprongen
- [x] klaar zeven
- [ ] open acht

- [x] laatste, klaar negen
"""


class Split(unittest.TestCase):
    def setUp(self):
        self.new, self.items, self.kept = bo.split(TOPIC)

    def test_alleen_afgevinkte_hoofdpunten_gaan(self):
        self.assertEqual([b[0] for b in self.items],
                         ["- [x] klaar twee", "- [x] klaar zes", "- [x] klaar zeven", "- [x] laatste, klaar negen"])

    def test_open_punten_en_subpunten_blijven_in_volgorde(self):
        self.assertEqual(bo.open_lines(self.new), bo.open_lines(TOPIC))
        self.assertIn("  - [x] afgevinkt subpunt blijft bij open drie", self.new)

    def test_afgevinkt_met_open_subpunt_blijft(self):
        self.assertEqual(self.kept, ["- [x] klaar vier, met open subpunt"])
        self.assertIn("- [x] klaar vier, met open subpunt\n  - [ ] nog open onder vier", self.new)

    def test_vervolgregels_gaan_mee(self):
        blocks = {b[0]: b for b in self.items}
        self.assertEqual(blocks["- [x] klaar twee"][1:], ["  vervolg van twee", "      (10 nov 2026, notitie)"])
        self.assertEqual(blocks["- [x] klaar zes"][1:], ["  **Gedaan:** vet en ingesprongen"])
        self.assertNotIn("vervolg van twee", self.new)

    def test_witregels_kloppen(self):
        self.assertIn("  vervolg van open een\n\n- [ ] open drie", self.new)
        self.assertIn("- [ ] open vijf\n- [ ] open acht\n", self.new)
        self.assertTrue(self.new.endswith("- [ ] open acht\n"))
        self.assertNotIn("\n\n\n", self.new)

    def test_koppen_en_tekst_blijven(self):
        for keep in ("WAAR: test", "STAND: test", "OPEN PUNTEN", '### Uit TODO.md onder "Iets"', "Intro van de sectie."):
            self.assertIn(keep, self.new)

    def test_tekst_op_kolom_nul_onder_afgevinkt_punt_stopt(self):
        with self.assertRaises(bo.Skip):
            bo.split("- [x] klaar\nlosse tekst zonder inspringen\n")

    def test_alinea_na_afgevinkt_punt_plakt_niet_vast(self):
        new, _, _ = bo.split("Tekst\n- [x] a\n- [x] b\n\nVolgende alinea\n")
        self.assertEqual(new, "Tekst\n\nVolgende alinea\n")

    def test_ander_lijstteken_voor_open_subpunt_blijft(self):
        new, items, kept = bo.split("- [x] hoofdtaak\n  * [ ] nog uitvoeren\n- [x] ander\n  1. [ ] ook open\n")
        self.assertEqual(items, [])
        self.assertEqual(len(kept), 2)

    def test_vervolg_na_witregel_hoort_bij_het_punt(self):
        text = "- [ ] open\n\n- [x] hoofdtaak\n\n  - [ ] resterend werk\n\n- [x] klaar\n\n  tweede alinea\n\n- [ ] laatste\n"
        new, items, kept = bo.split(text)
        self.assertEqual(kept, ["- [x] hoofdtaak"])
        self.assertEqual(items[0], ["- [x] klaar", "", "  tweede alinea"])
        self.assertEqual(new, "- [ ] open\n\n- [x] hoofdtaak\n\n  - [ ] resterend werk\n\n- [ ] laatste\n")


class Write(unittest.TestCase):
    """Against a throwaway _backlogs folder with its own git, like the hourly snapshot keeps it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_grace, self.old_rescue = bo.GRACE, bo.RESCUE
        bo.GRACE, bo.RESCUE = 0, os.path.join(self.tmp.name, "herstel")
        self.bl = os.path.realpath(os.path.join(self.tmp.name, "bl"))
        os.makedirs(os.path.join(self.bl, "repo"))
        self.topic = os.path.join(self.bl, "repo", "onderwerp.md")
        with open(self.topic, "w", encoding="utf-8") as f:
            f.write(TOPIC)
        self.old_backlogs = bo.BACKLOGS
        bo.BACKLOGS = self.bl
        self._git("init", "-q")
        self.snapshot()

    def tearDown(self):
        bo.BACKLOGS = self.old_backlogs
        bo.GRACE, bo.RESCUE = self.old_grace, self.old_rescue
        self.tmp.cleanup()

    def _git(self, *args):
        subprocess.run(["git", "-C", self.bl, "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True,
                       capture_output=True)

    def snapshot(self):
        self._git("add", "-A")
        self._git("commit", "-q", "-m", "snapshot", "--allow-empty")

    def run_one(self):
        return bo.write_one(self.topic, "repo/onderwerp.md")

    def test_schrijven_en_tweede_run(self):
        out = self.run_one()
        self.assertIn("removed 4", out)
        self.assertIn("show ", out)
        commit = out.split("show ")[1].split(":")[0]
        in_git = subprocess.run(["git", "-C", self.bl, "show", f"{commit}:repo/onderwerp.md"], capture_output=True,
                                text=True).stdout
        self.assertIn("- [x] klaar twee\n  vervolg van twee", in_git)  # the full text stays in git
        self.assertEqual(bo.open_lines(bo.read(self.topic)), bo.open_lines(TOPIC))
        self.snapshot()
        self.assertIn("nothing to remove (1 kept)", self.run_one())

    def test_niet_vastgelegd_wacht_op_de_snapshot(self):
        with open(self.topic, "a", encoding="utf-8") as f:
            f.write("\n- [x] net afgevinkt, nog niet in git\n")
        before = bo.read(self.topic)
        with self.assertRaises(bo.Skip) as e:
            self.run_one()
        self.assertIn("snapshot", str(e.exception))
        self.assertEqual(bo.read(self.topic), before)

    def test_niet_in_git_wordt_overgeslagen(self):
        other = os.path.join(self.bl, "repo", "nieuw.md")
        with open(other, "w", encoding="utf-8") as f:
            f.write("- [x] klaar\n")
        with self.assertRaises(bo.Skip):
            bo.write_one(other, "repo/nieuw.md")
        self.assertEqual(bo.read(other), "- [x] klaar\n")

    def _terminal_schrijft(self, moment):
        real_read, seen = bo.read, []

        def read(path):
            if path.endswith(".pin-opschonen"):
                seen.append(1)
                if len(seen) == 1 and moment == "voor":
                    self._append()
                text = real_read(path)
                if len(seen) == 1 and moment == "na":
                    self._append()
                return text
            return real_read(path)
        bo.read = read
        try:
            with self.assertRaises(bo.Skip):
                self.run_one()
        finally:
            bo.read = real_read

    def _append(self):
        with open(self.topic, "a", encoding="utf-8") as f:
            f.write("\n- [ ] nieuw punt van een terminal\n")

    def _na_afloop(self):
        text = bo.read(self.topic)
        self.assertIn("nieuw punt van een terminal", text)
        self.assertIn("- [x] klaar twee", text)  # left alone
        self.snapshot()  # the next hourly snapshot
        self.run_one()
        self.assertIn("nieuw punt van een terminal", bo.read(self.topic))
        self.assertNotIn("klaar twee", bo.read(self.topic))
        self.assertEqual([f for f in os.listdir(os.path.dirname(self.topic)) if f.startswith(".")], [])

    def test_terminal_schrijft_voor_de_controle(self):
        self._terminal_schrijft("voor")
        self._na_afloop()

    def test_terminal_schrijft_vlak_voor_het_vervangen(self):
        self._terminal_schrijft("na")
        self._na_afloop()

    def test_schrijver_met_het_oude_bestand_open_schrijft_na_het_vervangen(self):
        handle = open(self.topic, "a", encoding="utf-8")  # a writer opened the file before the replace
        real_pause = bo.pause

        def pause(_):
            handle.write("\n- [ ] punt van een trage schrijver\n")
            handle.close()
        bo.pause = pause
        try:
            with self.assertRaises(bo.Skip) as e:
                self.run_one()
        finally:
            bo.pause = real_pause
        self.assertIn("back in place", str(e.exception))
        self.assertIn("punt van een trage schrijver", bo.read(self.topic))
        self.assertEqual(len(os.listdir(bo.RESCUE)), 1)

    def test_twee_schrijvers_tegelijk_niets_kwijt(self):
        handle = open(self.topic, "a", encoding="utf-8")
        real_pause = bo.pause

        def pause(_):
            handle.write("\n- [ ] punt van schrijver A\n")  # A writes into the replaced file
            handle.close()
            with open(self.topic, "a", encoding="utf-8") as f:  # B writes into the new file
                f.write("\n- [ ] punt van schrijver B\n")
        bo.pause = pause
        try:
            with self.assertRaises(bo.Skip) as e:
                self.run_one()
        finally:
            bo.pause = real_pause
        self.assertIn("merge by hand", str(e.exception))
        self.assertIn("punt van schrijver B", bo.read(self.topic))
        saved = os.path.join(bo.RESCUE, os.listdir(bo.RESCUE)[0])
        self.assertIn("punt van schrijver A", bo.read(saved))

    def test_proefrun_via_symlink_naar_de_backlogmap_stopt(self):
        out = os.path.join(self.tmp.name, "dry")
        os.makedirs(out)
        os.symlink(os.path.join(self.bl, "repo"), os.path.join(out, "repo"))
        r = self._dryrun(out)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("symlink", r.stdout)
        self.assertEqual(bo.read(self.topic), TOPIC)

    def test_alleen_onderwerpbestanden(self):
        for bad in (os.path.join(self.bl, "_backlog_repo.txt"), os.path.join(self.bl, "x.md"), "/etc/hosts",
                    os.path.join(self.bl, "repo", "sub", "x.md")):
            with self.assertRaises(bo.Skip):
                bo.check_path(bad)

    def _dryrun(self, outdir):
        env = dict(os.environ, BACKLOGS_DIR=self.bl, TMPDIR=self.tmp.name)
        return subprocess.run([sys.executable, "-I", os.path.join(HERE, "backlog_opschonen.py"), "dryrun", outdir,
                               self.topic], capture_output=True, text=True, env=env)

    def test_proefrun_schrijft_alleen_in_de_proefmap(self):
        out = os.path.join(self.tmp.name, "dry")
        r = self._dryrun(out)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("in git", r.stdout)
        self.assertEqual(bo.read(self.topic), TOPIC)
        self.assertNotIn("klaar twee", bo.read(os.path.join(out, "repo", "onderwerp.md")))

    def test_proefrun_in_de_backlogmap_stopt(self):
        r = self._dryrun(self.bl)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("overlaps", r.stdout + r.stderr)
        self.assertEqual(bo.read(self.topic), TOPIC)


if __name__ == "__main__":
    unittest.main()

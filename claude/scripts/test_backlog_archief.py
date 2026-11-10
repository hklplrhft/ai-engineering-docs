#!/usr/bin/env python3
"""Tests for backlog_archief.py (plan docs/plans/2026-11-10-backlog-archief.md).

Run: python3 claude/scripts/test_backlog_archief.py
"""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import backlog_archief as ba  # noqa: E402

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
        self.new, self.items, self.kept = ba.split(TOPIC)

    def test_alleen_afgevinkte_hoofdpunten_gaan(self):
        firsts = [b[0] for _, b in self.items]
        self.assertEqual(firsts, ["- [x] klaar twee", "- [x] klaar zes", "- [x] klaar zeven", "- [x] laatste, klaar negen"])

    def test_open_punten_en_subpunten_blijven_in_volgorde(self):
        self.assertEqual(ba.open_lines(self.new), ba.open_lines(TOPIC))
        self.assertIn("  - [x] afgevinkt subpunt blijft bij open drie", self.new)

    def test_afgevinkt_met_open_subpunt_blijft(self):
        self.assertEqual(self.kept, ["- [x] klaar vier, met open subpunt"])
        self.assertIn("- [x] klaar vier, met open subpunt\n  - [ ] nog open onder vier", self.new)

    def test_vervolgregels_gaan_mee(self):
        blocks = {b[0]: b for _, b in self.items}
        self.assertEqual(blocks["- [x] klaar twee"][1:], ["  vervolg van twee", "      (10 nov 2026, notitie)"])
        self.assertEqual(blocks["- [x] klaar zes"][1:], ["  **Gedaan:** vet en ingesprongen"])
        self.assertNotIn("vervolg van twee", self.new)

    def test_witregels_kloppen(self):
        self.assertIn("  vervolg van open een\n\n- [ ] open drie", self.new)  # one blank line, not two
        self.assertIn("- [ ] open vijf\n- [ ] open acht\n", self.new)  # list without blank lines stays tight
        self.assertTrue(self.new.endswith("- [ ] open acht\n"))  # last item gone, final newline kept, no blank tail
        self.assertNotIn("\n\n\n", self.new)

    def test_koppen_en_tekst_blijven(self):
        for keep in ("WAAR: test", "STAND: test", "OPEN PUNTEN", '### Uit TODO.md onder "Iets"', "Intro van de sectie."):
            self.assertIn(keep, self.new)

    def test_archief_met_kop_per_groep(self):
        body = ba.render(self.items)
        self.assertTrue(body.startswith(ba.NO_HEADING + "\n\n- [x] klaar twee"))
        self.assertIn('### Uit TODO.md onder "Iets"\n\n- [x] klaar zes', body)

    def test_tekst_op_kolom_nul_onder_afgevinkt_punt_stopt(self):
        with self.assertRaises(ba.Skip):
            ba.split("- [x] klaar\nlosse tekst zonder inspringen\n")

    def test_ander_lijstteken_voor_open_subpunt_blijft(self):
        new, items, kept = ba.split("- [x] hoofdtaak\n  * [ ] nog uitvoeren\n- [x] ander\n  1. [ ] ook open\n")
        self.assertEqual(items, [])
        self.assertEqual(len(kept), 2)

    def test_vervolg_na_witregel_hoort_bij_het_punt(self):
        text = "- [ ] open\n\n- [x] hoofdtaak\n\n  - [ ] resterend werk\n\n- [x] klaar\n\n  tweede alinea\n\n- [ ] laatste\n"
        new, items, kept = ba.split(text)
        self.assertEqual(kept, ["- [x] hoofdtaak"])
        self.assertEqual(items[0][1], ["- [x] klaar", "", "  tweede alinea"])
        self.assertEqual(new, "- [ ] open\n\n- [x] hoofdtaak\n\n  - [ ] resterend werk\n\n- [ ] laatste\n")

    def test_alinea_na_afgevinkt_punt_plakt_niet_vast(self):
        new, _, _ = ba.split("Tekst\n- [x] a\n- [x] b\n\nVolgende alinea\n")
        self.assertEqual(new, "Tekst\n\nVolgende alinea\n")


class Write(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.bl = os.path.join(self.tmp.name, "bl")
        os.makedirs(os.path.join(self.bl, "repo"))
        self.topic = os.path.join(self.bl, "repo", "onderwerp.md")
        with open(self.topic, "w", encoding="utf-8") as f:
            f.write(TOPIC)
        self.old_backlogs = ba.BACKLOGS
        ba.BACKLOGS = os.path.realpath(self.bl)
        self.topic = os.path.realpath(self.topic)
        self.arch = ba.archive_path(self.topic)

    def tearDown(self):
        ba.BACKLOGS = self.old_backlogs
        self.tmp.cleanup()

    def test_schrijven_en_tweede_run(self):
        self.assertIn("archived 4", ba.write_one(self.topic, "2026-11-10"))
        arch = ba.read(self.arch)
        self.assertTrue(arch.startswith("Archief van repo/onderwerp.md"))
        self.assertEqual(arch.count("- [x] klaar twee"), 1)
        self.assertEqual(ba.open_lines(ba.read(self.topic)), ba.open_lines(TOPIC))
        self.assertIn("nothing to archive (1 kept)", ba.write_one(self.topic, "2026-11-10"))
        self.assertEqual(ba.read(self.arch), arch)

    def test_herstart_na_crash_voor_het_vervangen(self):
        _, items, _ = ba.split(TOPIC)
        os.makedirs(os.path.dirname(self.arch))
        with open(self.arch, "w", encoding="utf-8") as f:  # earlier run appended, then crashed
            f.write(ba.header(self.topic, "2026-11-10") + "\nGearchiveerd op 2026-11-10 (4 punten):\n\n" + ba.render(items))
        ba.write_one(self.topic, "2026-11-11")
        self.assertEqual(ba.read(self.arch).count("- [x] klaar twee"), 1)
        self.assertNotIn("klaar twee", ba.read(self.topic))

    def _terminal_schrijft(self, moment):
        """Run write_one while "a terminal" appends an item in place: before the check or just after it."""
        real_read, seen = ba.read, []

        def read(path):
            if path.endswith(".pin-archief"):
                seen.append(1)
                if len(seen) == 1 and moment == "voor":
                    self._append()
                text = real_read(path)
                if len(seen) == 1 and moment == "na":
                    self._append()
                return text
            return real_read(path)
        ba.read = read
        try:
            with self.assertRaises(ba.Skip):
                ba.write_one(self.topic, "2026-11-10")
        finally:
            ba.read = real_read

    def _append(self):
        with open(self.topic, "a", encoding="utf-8") as f:
            f.write("\n- [ ] nieuw punt van een terminal\n")

    def _na_afloop(self):
        text = ba.read(self.topic)
        self.assertIn("nieuw punt van een terminal", text)
        self.assertIn("- [x] klaar twee", text)  # left alone; the archive holds the items for a rerun
        ba.write_one(self.topic, "2026-11-10")
        self.assertIn("nieuw punt van een terminal", ba.read(self.topic))
        self.assertNotIn("klaar twee", ba.read(self.topic))
        self.assertEqual(ba.read(self.arch).count("- [x] klaar twee"), 1)
        self.assertEqual([f for f in os.listdir(os.path.dirname(self.topic)) if f.startswith(".")], [])

    def test_terminal_schrijft_voor_de_controle(self):
        self._terminal_schrijft("voor")
        self._na_afloop()

    def test_terminal_schrijft_vlak_voor_het_vervangen(self):
        self._terminal_schrijft("na")
        self._na_afloop()

    def test_herstart_met_intussen_een_extra_afgevinkt_punt(self):
        _, items, _ = ba.split(TOPIC)
        os.makedirs(os.path.dirname(self.arch))
        with open(self.arch, "w", encoding="utf-8") as f:  # first run archived only "klaar twee", then crashed
            f.write(ba.header(self.topic, "2026-11-10") + "\nGearchiveerd op 2026-11-10 (1 punten):\n\n"
                    + ba.render(items[:1]))
        ba.write_one(self.topic, "2026-11-10")
        arch = ba.read(self.arch)
        self.assertEqual(arch.count("- [x] klaar twee"), 1)
        self.assertEqual(arch.count("- [x] klaar zes"), 1)

    def test_alleen_onderwerpbestanden(self):
        for bad in (os.path.join(self.bl, "_backlog_repo.txt"), os.path.join(self.bl, "repo", "archief", "x.md"),
                    os.path.join(self.bl, "x.md"), "/etc/hosts"):
            with self.assertRaises(ba.Skip):
                ba.check_path(bad)

    def test_proefrun_schrijft_alleen_in_de_proefmap(self):
        out = os.path.join(self.tmp.name, "dry")
        env = dict(os.environ, BACKLOGS_DIR=self.bl, TMPDIR=self.tmp.name)
        r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "backlog_archief.py"), "dryrun", out, self.topic],
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(ba.read(self.topic), TOPIC)
        self.assertFalse(os.path.exists(self.arch))
        self.assertTrue(os.path.exists(os.path.join(out, "repo", "archief", "onderwerp.md")))

    def test_proefrun_in_de_backlogmap_stopt(self):
        env = dict(os.environ, BACKLOGS_DIR=self.bl, TMPDIR=self.tmp.name)
        r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "backlog_archief.py"), "dryrun", self.bl, self.topic],
                           capture_output=True, text=True, env=env)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("overlaps", r.stdout + r.stderr)
        self.assertEqual(ba.read(self.topic), TOPIC)


if __name__ == "__main__":
    unittest.main()

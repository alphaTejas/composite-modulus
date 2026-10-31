import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from analysis.compare_models import evaluate, export_csv, fraction_grid, sweep
from utilities.materials import load_materials, Material

ROOT = Path(__file__).resolve().parents[1]


class ProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.material = load_materials(ROOT / "data/materials.json")["stiff_inclusions"]

    def test_data_provenance_is_present(self):
        for m in load_materials(ROOT / "data/materials.json").values():
            self.assertEqual(m.source_status, "illustrative")
            self.assertTrue(m.source_note)

    def test_unsupported_geometry_and_unknown_keys_rejected(self):
        raw = self.material.to_dict()
        raw.pop("unit")
        for change in [{"geometry": "cylinder"}, {"Ef_typo": 70}, {"Ef": -1}]:
            with self.assertRaises(ValueError):
                Material.from_dict({**raw, **change})

    def test_grid_includes_requested_key_fractions(self):
        values = fraction_grid(.6, 8)
        for vf in [0, .05, .1, .3, .5, .6]:
            self.assertIn(vf, values)
        self.assertEqual(values, sorted(set(values)))

    def test_bad_grids_rejected(self):
        for maximum, points in [(0, 61), (1.1, 61), (.6, 1), (.6, 3000)]:
            with self.assertRaises(ValueError):
                fraction_grid(maximum, points)

    def test_dilute_is_missing_above_cutoff(self):
        rows = evaluate(self.material, .3)
        dilute = next(r for r in rows if r["model"] == "eshelby_dilute")
        self.assertEqual(dilute["E"], "")
        self.assertEqual(dilute["status"], "not_evaluated")
        self.assertEqual(len(rows), 10)

    def test_cross_ordered_bounds_are_explicitly_unavailable(self):
        raw = self.material.to_dict()
        raw.pop("unit")
        # Larger E but lower K: phase ordering differs between K and G.
        m = Material.from_dict({**raw, "Ef": 12, "Em": 10, "nu_f": 0, "nu_m": .45})
        rows = evaluate(m, .05)
        hs = [r for r in rows if r["model"].startswith("hs_")]
        self.assertEqual(len(hs), 2)
        self.assertTrue(all(r["status"] == "not_applicable" and r["E"] == "" for r in hs))

    def test_csv_keeps_missing_values_and_notes(self):
        with tempfile.TemporaryDirectory() as d:
            target = export_csv(sweep(self.material, vf_max=.2, points=3), Path(d)/"data.csv")
            with target.open() as f:
                rows = list(csv.DictReader(f))
            dilute = [r for r in rows if r["model"] == "eshelby_dilute" and float(r["Vf"]) > .1]
            self.assertTrue(dilute)
            self.assertTrue(all(r["E"] == "" and r["note"] for r in dilute))

    def test_single_run_works_from_another_directory(self):
        with tempfile.TemporaryDirectory() as d:
            result = subprocess.run([sys.executable, str(ROOT/"main.py"), "--vf", ".05",
                                     "--output", d], cwd=d, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads((Path(d)/"stiff_inclusions_single.json").read_text())
            self.assertEqual(len(payload["results"]), 10)

    def test_cli_bad_case_is_readable(self):
        result = subprocess.run([sys.executable, str(ROOT/"main.py"), "--case", "missing"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Unknown case", result.stderr)

    def test_cli_rejects_inconsistent_volume_fractions(self):
        result = subprocess.run([sys.executable, str(ROOT/"main.py"), "--vf", ".2", "--vm", ".7"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Vf + Vm", result.stderr)


if __name__ == "__main__":
    unittest.main()

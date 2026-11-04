"""Exercise the real Streamlit form and compare it with the analytical engine."""
import csv
import importlib.util
import io
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Streamlit is not installed")
class WebAppTests(unittest.TestCase):
    def app(self):
        from streamlit.testing.v1 import AppTest
        return AppTest.from_file(str(ROOT / "app.py"), default_timeout=120).run()

    def test_default_values_match_analytical_reference(self):
        app = self.app()
        self.assertFalse(app.exception)
        metrics = {m.label: m.value for m in app.metric}
        self.assertEqual(metrics["Mori-Tanaka"], "3.847096 GPa")
        self.assertEqual(metrics["Eshelby / dilute"], "3.831404 GPa")
        self.assertEqual(set(metrics), {"Eshelby / dilute", "Mori-Tanaka"})
        self.assertEqual(len(app.dataframe[0].value), 2)
        self.assertEqual(app.multiselect[0].options, ["Eshelby / dilute", "Mori-Tanaka"])
        self.assertNotIn("ξ", " ".join(widget.label for widget in app.number_input))
        self.assertEqual(next(w for w in app.radio if w.label == "Comparison view").options,
                         ["Full fraction range", "Low-fraction detail"])

    def test_changed_fraction_matches_engine_and_omits_dilute(self):
        from models import mori_tanaka
        app = self.app()
        app.slider(key="vf_stiff_inclusions_GPa").set_value(.3)
        app.button[0].click().run()
        self.assertFalse(app.exception)
        expected = mori_tanaka(70, 3.5, .3, nu_f=.2, nu_m=.35)["E"]
        metrics = {m.label: m.value for m in app.metric}
        self.assertEqual(metrics["Mori-Tanaka"], f"{expected:.6f} GPa")
        self.assertEqual(metrics["Eshelby / dilute"], "Not evaluated")

    def test_invalid_zero_modulus_shows_readable_error(self):
        app = self.app()
        app.number_input(key="Ef_stiff_inclusions_GPa").set_value(0)
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertTrue(app.error)
        self.assertIn("greater than zero", app.error[0].value)
        self.assertEqual(len(app.metric), 0)

    def test_unit_selection_converts_preset_and_output(self):
        app = self.app()
        next(w for w in app.selectbox if w.label == "Modulus unit").select("MPa").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.number_input(key="Ef_stiff_inclusions_MPa").value, 70000)
        mt = next(m.value for m in app.metric if m.label == "Mori-Tanaka")
        self.assertEqual(mt, "3847.095921 MPa")

    def test_method_selection_filters_results(self):
        app = self.app()
        app.multiselect[0].set_value(["Mori-Tanaka"])
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.dataframe[0].value), 1)
        self.assertEqual(app.dataframe[0].value.iloc[0]["Method"], "Mori-Tanaka")

    def test_csv_preserves_unavailable_values(self):
        from analysis.web_results import csv_bytes, evaluate, sweep
        from utilities.materials import load_materials
        material = load_materials(ROOT / "data/materials.json")["stiff_inclusions"]
        rows = evaluate(material, .3)
        exported = list(csv.DictReader(io.StringIO(csv_bytes(rows).decode())))
        self.assertEqual({r["model"] for r in exported}, {"eshelby_dilute", "mori_tanaka"})
        self.assertEqual({r["model"] for r in sweep(material, points=2)},
                         {"eshelby_dilute", "mori_tanaka"})
        dilute = next(r for r in exported if r["model"] == "eshelby_dilute")
        self.assertEqual(dilute["E"], "")
        self.assertEqual(dilute["status"], "not_evaluated")

    def test_empty_selection_and_low_fraction_chart(self):
        app = self.app()
        next(w for w in app.radio if w.label == "Comparison view").set_value("Low-fraction detail").run()
        self.assertFalse(app.exception)
        app.multiselect[0].set_value([])
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.metric), 0)
        self.assertTrue(app.warning)


if __name__ == "__main__":
    unittest.main()

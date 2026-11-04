"""Streamlit interface for the validated analytical composite-modulus models."""
import io
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from analysis.web_results import (
    FAMILIES, LABELS, comparison_figure, csv_bytes, evaluate, material_from_record,
    selected_rows, sweep,
)
from utilities.materials import Material, load_materials

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Composite Modulus Lab", page_icon="🔬", layout="wide")


@st.cache_data(max_entries=24, ttl=3600, show_spinner=False)
def cached_sweep(serialized_material, vf_max, points):
    material = material_from_record(json.loads(serialized_material))
    return sweep(material, vf_max=vf_max, points=points)


def result_table(rows):
    """Display unavailable properties as missing, with the original status beside them."""
    data = []
    for row in rows:
        data.append({"Method": LABELS[row["model"]],
                     **{key: None if row[key] == "" else row[key] for key in ["E", "nu", "K", "G"]},
                     "Status": row["status"], "Interpretation": row["note"]})
    return pd.DataFrame(data)


def render():
    cases = load_materials(ROOT / "data/materials.json")
    with st.sidebar:
        st.markdown("### Study setup")
        preset_id = st.selectbox("Material case", list(cases) + ["custom"],
                                format_func=lambda k: "Custom material" if k == "custom" else cases[k].name)
        unit = st.selectbox("Modulus unit", ["GPa", "MPa", "Pa"])
        preset = cases.get(preset_id, cases["stiff_inclusions"])
        scale = {"GPa": 1, "MPa": 1000, "Pa": 1e9}[unit]
        suffix = preset_id + "_" + unit
        with st.form("material_inputs"):
            Ef = st.number_input("Inclusion modulus Ef", min_value=0.0, value=preset.Ef * scale,
                                 format="%.6f", key="Ef_" + suffix)
            Em = st.number_input("Matrix modulus Em", min_value=0.0, value=preset.Em * scale,
                                 format="%.6f", key="Em_" + suffix)
            nu_f = st.number_input("Inclusion Poisson ratio νf", min_value=-.999, max_value=.499,
                                   value=preset.nu_f, step=.01, format="%.3f", key="nuf_" + suffix)
            nu_m = st.number_input("Matrix Poisson ratio νm", min_value=-.999, max_value=.499,
                                   value=preset.nu_m, step=.01, format="%.3f", key="num_" + suffix)
            Vf = st.slider("Inclusion volume fraction Vf", 0.0, 1.0, .05, .01, key="vf_" + suffix)
            families = st.multiselect("Model families", list(FAMILIES), default=list(FAMILIES))
            st.form_submit_button("Calculate", type="primary", use_container_width=True)
        st.caption("Two phases without voids. Vm is calculated as 1 − Vf. All moduli use the unit selected above.")
        st.caption("Spherical inclusions · isotropic phases · perfect bonding · linear elasticity")

    st.caption("ANALYTICAL COMPOSITE MECHANICS")
    st.title("Composite Modulus Lab")
    st.markdown("Predict a composite's **effective Young's modulus** with **Eshelby / dilute** and **Mori-Tanaka**.")
    try:
        material = Material.from_dict({
            "id": preset_id, "name": "Current material inputs", "Ef": Ef, "Em": Em,
            "nu_f": nu_f, "nu_m": nu_m, "xi": preset.xi, "geometry": "spherical",
            "source_status": "user_supplied" if preset_id == "custom" else "illustrative / editable",
            "source_note": "Visitor-entered values; source, isotropy and geometry must be justified."
                           if preset_id == "custom" else "Hypothetical teaching inputs, not measured material data. Values can be edited in the sidebar.",
        }, unit)
        rows = evaluate(material, Vf)
    except (ValueError, RuntimeError, OverflowError) as exc:
        st.error(f"Please check the inputs: {exc}")
        st.stop()
    selected = selected_rows(rows, families)
    st.info("The presets are illustrative teaching inputs. The 3D models assume isotropic spherical inclusions; they do not predict woven or cylindrical-fiber architecture.")
    calculator, comparison, theory, downloads = st.tabs(["Calculator", "Compare fractions", "Theory & assumptions", "Downloads"])

    with calculator:
        metric_models = [name for name in ["eshelby_dilute", "mori_tanaka"]
                         if any(r["model"] == name for r in selected)]
        if metric_models:
            columns = st.columns(len(metric_models))
            for column, name in zip(columns, metric_models):
                row = next(r for r in rows if r["model"] == name)
                column.metric(LABELS[name], "Not evaluated" if row["E"] == "" else f"{row['E']:.6f} {unit}")
        st.caption(f"Current composition: Vf = {Vf:.2f} · Vm = {1-Vf:.2f}. E, K and G are in {unit}; ν is dimensionless.")
        if selected:
            st.dataframe(result_table(selected), hide_index=True, use_container_width=True)
        else:
            st.warning("Select at least one model family in Study setup and click Calculate.")
        if Vf > .1:
            st.caption("Dilute is omitted above Vf=0.1 in this teaching workflow. The cutoff is not a universal accuracy threshold.")
        with st.expander("Calculation details"):
            st.write({"Input source status": material.source_status,
                      "Inclusion geometry": material.geometry})
            st.caption("Both methods assume isotropic elastic phases and perfect bonding. Eshelby / dilute neglects inclusion interactions; Mori-Tanaka uses the average matrix strain.")

    with comparison:
        left, right = st.columns(2)
        vf_max = left.slider("Sweep maximum Vf", .1, 1.0, .6, .05)
        points = right.select_slider("Requested grid points", options=[21, 41, 61, 101], value=61)
        mode = st.radio("Comparison view", ["Full fraction range", "Low-fraction detail"], horizontal=True)
        with st.spinner("Calculating the selected fraction range…"):
            sweep_rows = cached_sweep(json.dumps(material.to_dict(), sort_keys=True), vf_max, points)
        visible_sweep = selected_rows(sweep_rows, families)
        figure = comparison_figure(visible_sweep, unit, mode=mode)
        st.pyplot(figure, use_container_width=True)
        image = io.BytesIO()
        figure.savefig(image, format="png", dpi=180, bbox_inches="tight")
        plt.close(figure)
        st.caption("Eshelby / dilute is displayed only for Vf≤0.1 because it neglects inclusion interactions. This teaching cutoff is not a universal validity threshold.")
        st.download_button("Download current chart (PNG)", image.getvalue(), "composite_modulus_chart.png", "image/png")

    with theory:
        st.markdown("### What are we predicting?")
        st.write("Young's modulus E measures elastic stiffness, not failure strength. Homogenization replaces the assumed internal structure with an equivalent material.")
        st.latex(r"V_f+V_m=1,\qquad K=\frac{E}{3(1-2\nu)},\qquad G=\frac{E}{2(1+\nu)}")
        st.latex(r"E_{\mathrm{eff}}=\frac{9K_{\mathrm{eff}}G_{\mathrm{eff}}}{3K_{\mathrm{eff}}+G_{\mathrm{eff}}}")
        descriptions = {
            "Eshelby / dilute": "A spherical Eshelby tensor determines strain concentration. The dilute stiffness estimate neglects interactions and is displayed only through Vf=0.1. That is an educational restriction, not a universal accuracy guarantee.",
            "Mori-Tanaka": "Uses the average matrix strain as the surrounding reference. The existing tensor implementation normalizes Eshelby-based strain concentration and returns effective K, G, E and ν.",
        }
        for family, description in descriptions.items():
            with st.expander(family):
                st.write(description)
        st.warning("Real biocomposite conclusions require sourced properties, an appropriate geometry/anisotropy model and validation data. No experimental accuracy claim is made by this app.")
        st.markdown("[Eshelby original paper](https://doi.org/10.1098/rspa.1957.0133) · [NPTEL micromechanics](https://archive.nptel.ac.in/content/storage2/courses/101104010/lecture34/34_2.htm)")

    with downloads:
        st.markdown("### Take the results with you")
        st.download_button("Download current results (CSV)", csv_bytes(selected), "composite_modulus_results.csv", "text/csv")
        st.download_button("Download fraction sweep (CSV)", csv_bytes(visible_sweep), "composite_modulus_sweep.csv", "text/csv")
        payload = {"material": {key: value for key, value in material.to_dict().items() if key != "xi"}, "Vf": Vf, "Vm": 1-Vf,
                   "selected_families": families, "results": selected,
                   "experimental_validation": False}
        st.download_button("Download inputs and results (JSON)", json.dumps(payload, indent=2),
                           "composite_modulus_case.json", "application/json")
    st.divider()
    st.caption("Composite Modulus Lab · Eshelby / dilute and Mori-Tanaka · Visitor inputs are not saved to project files.")


if __name__ == "__main__":
    render()

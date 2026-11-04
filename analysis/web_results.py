"""Presentation helpers for Streamlit; reuse the existing mechanics unchanged."""
import csv
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analysis.compare_models import FIELDS, fraction_grid
from models import eshelby_dilute, mori_tanaka
from utilities.input_checks import fractions
from utilities.materials import Material


FAMILIES = {
    "Eshelby / dilute": ["eshelby_dilute"],
    "Mori-Tanaka": ["mori_tanaka"],
}
LABELS = {
    "eshelby_dilute": "Eshelby / dilute", "mori_tanaka": "Mori-Tanaka",
}


def evaluate(material, Vf):
    """Calculate only the two inclusion models offered by the website."""
    Vf, Vm = fractions(Vf)
    inp = material.inputs(Vf)
    rows = []

    def add(model, values=None, status="ok", note=""):
        row = dict.fromkeys(FIELDS, "")
        row.update(case=material.id, unit=material.unit, Vf=Vf, Vm=Vm,
                   model=model, status=status, note=note)
        if values is not None:
            row.update({key: value for key, value in values.items() if key in FIELDS})
        rows.append(row)

    if Vf <= 0.1 + 1e-12:
        add("eshelby_dilute", eshelby_dilute(**{**inp, "Vf": min(Vf, 0.1)}),
            status="low_fraction", note="No inclusion interactions; accuracy is contrast-dependent.")
    else:
        add("eshelby_dilute", status="not_evaluated",
            note="Outside the configured low-fraction display interval (Vf<=0.1).")
    add("mori_tanaka", mori_tanaka(**inp),
        note="Spherical inclusions in a connected isotropic matrix.")
    return rows


def sweep(material, *, vf_max=0.6, points=61):
    return [row for vf in fraction_grid(vf_max, points) for row in evaluate(material, vf)]


def selected_rows(rows, families):
    names = {name for family in families for name in FAMILIES[family]}
    return [row for row in rows if row["model"] in names]


def csv_bytes(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def material_from_record(record):
    raw = dict(record)
    unit = raw.pop("unit")
    return Material.from_dict(raw, unit)


def comparison_figure(rows, unit, *, mode="Full fraction range"):
    """Create a figure in memory; never write visitor results to shared disk."""
    fig, ax = plt.subplots(figsize=(9, 4.8), layout="constrained")

    def series(name):
        items = [r for r in rows if r["model"] == name and r["E"] != ""]
        if mode == "Low-fraction detail":
            items = [r for r in items if r["Vf"] <= .1 + 1e-12]
        return [r["Vf"] for r in items], [r["E"] for r in items]

    if mode not in {"Full fraction range", "Low-fraction detail"}:
        raise ValueError("Unknown chart mode.")
    specs = [("eshelby_dilute", "#CD8625", "-"), ("mori_tanaka", "#087F8C", "--")]
    for name, color, style in specs:
        x, y = series(name)
        if x:
            ax.plot(x, y, color=color, ls=style, lw=2.3, label=LABELS[name])
    ax.set(xlabel="Inclusion volume fraction, Vf", ylabel=f"Young's modulus, E ({unit})")
    ax.set_title(mode, loc="left", color="#153B57", weight="bold", pad=14)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=.18)
    handles, _ = ax.get_legend_handles_labels()
    if handles:
        ax.legend(frameon=False, fontsize=8.5)
    else:
        ax.text(.5, .5, "Select applicable methods to display this chart.", transform=ax.transAxes,
                ha="center", va="center", color="#526779")
    return fig

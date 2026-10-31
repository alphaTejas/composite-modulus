"""Presentation helpers for Streamlit; reuse the existing mechanics unchanged."""
import csv
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analysis.compare_models import FIELDS
from utilities.materials import Material


FAMILIES = {
    "Rule of Mixtures": ["simple_voigt", "simple_reuss", "isotropic_vr_lower", "isotropic_vr_upper"],
    "Eshelby / dilute": ["eshelby_dilute"],
    "Mori-Tanaka": ["mori_tanaka"],
    "Self-consistent": ["self_consistent"],
    "Hashin-Shtrikman bounds": ["hs_lower", "hs_upper"],
    "Halpin-Tsai": ["halpin_tsai_demo"],
}
LABELS = {
    "simple_voigt": "Simple equal-strain E", "simple_reuss": "Simple equal-stress E",
    "isotropic_vr_lower": "Isotropic Reuss lower bound", "isotropic_vr_upper": "Isotropic Voigt upper bound",
    "eshelby_dilute": "Eshelby / dilute", "mori_tanaka": "Mori-Tanaka",
    "self_consistent": "Self-consistent", "hs_lower": "Hashin-Shtrikman lower bound",
    "hs_upper": "Hashin-Shtrikman upper bound", "halpin_tsai_demo": "Halpin-Tsai demonstration",
}


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


def comparison_figure(rows, unit, *, mode="Isotropic comparison"):
    """Create a figure in memory; never write visitor results to shared disk."""
    fig, ax = plt.subplots(figsize=(9, 4.8), layout="constrained")

    def series(name):
        items = [r for r in rows if r["model"] == name and r["E"] != ""]
        if mode == "Low-fraction detail":
            items = [r for r in items if r["Vf"] <= .1 + 1e-12]
        return [r["Vf"] for r in items], [r["E"] for r in items]

    if mode == "Isotropic comparison":
        for lo, hi, color, label in [
            ("isotropic_vr_lower", "isotropic_vr_upper", "#E5ECF3", "Isotropic Voigt-Reuss interval"),
            ("hs_lower", "hs_upper", "#ACDBDC", "Hashin-Shtrikman interval"),
        ]:
            x, lower = series(lo)
            xu, upper = series(hi)
            if x and x == xu:
                ax.fill_between(x, lower, upper, color=color, alpha=.8, label=label)
        specs = [("mori_tanaka", "#087F8C", "-"), ("self_consistent", "#153B57", "--")]
    elif mode == "Low-fraction detail":
        specs = [("eshelby_dilute", "#CD8625", "-"), ("mori_tanaka", "#087F8C", "--"),
                 ("self_consistent", "#153B57", ":")]
    elif mode == "Scalar / Halpin-Tsai demonstration":
        specs = [("simple_voigt", "#7A899B", "--"), ("simple_reuss", "#153B57", ":"),
                 ("halpin_tsai_demo", "#8460A9", "-")]
    else:
        raise ValueError("Unknown chart mode.")
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

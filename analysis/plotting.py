"""Export readable, scope-separated static figures without a display server."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


COLORS = {"navy": "#153B57", "teal": "#087F8C", "gold": "#D28B22",
          "purple": "#8561A8", "gray": "#718096"}


def _series(rows, model, key="E"):
    subset = [r for r in rows if r["model"] == model and r[key] != ""]
    return np.array([r["Vf"] for r in subset]), np.array([r[key] for r in subset])


def _style(ax, unit, title):
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Inclusion volume fraction, $V_f$")
    ax.set_ylabel(f"Young's modulus, E ({unit})")
    ax.grid(True, alpha=.18)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)


def _save(fig, directory, name):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for extension in ["png", "pdf"]:
        target = directory / f"{name}.{extension}"
        fig.savefig(target, dpi=180, bbox_inches="tight", facecolor="white")
        paths.append(target)
    plt.close(fig)
    return paths


def plot_case(material, rows, directory):
    """Return paths for an isotropic comparison and separate demonstrations."""
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.labelcolor": COLORS["navy"], "text.color": COLORS["navy"]})
    fig, ax = plt.subplots(figsize=(9, 4.8), layout="constrained")
    x, low = _series(rows, "isotropic_vr_lower")
    _, high = _series(rows, "isotropic_vr_upper")
    ax.fill_between(x, low, high, color="#E7EDF2", label="Isotropic Voigt-Reuss interval")
    hx, hl = _series(rows, "hs_lower")
    _, hu = _series(rows, "hs_upper")
    if len(hx):
        ax.fill_between(hx, hl, hu, color="#A8DADC", alpha=.65, label="Hashin-Shtrikman interval")
    x, y = _series(rows, "mori_tanaka")
    ax.plot(x, y, color=COLORS["teal"], lw=2.4, label="Mori-Tanaka")
    x, y = _series(rows, "self_consistent")
    ax.plot(x, y, color=COLORS["navy"], lw=2.2, ls="--", label="Self-consistent")
    _style(ax, material.unit, material.name)
    ax.legend(loc="best", frameon=False, fontsize=9)
    fig.supxlabel("Spherical, isotropic phases | Mathematical comparison; no experimental validation", fontsize=9)
    paths = _save(fig, directory, material.id + "_isotropic_comparison")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), layout="constrained")
    ax = axes[0]
    for model, label, color, ls in [
        ("eshelby_dilute", "Eshelby / dilute", COLORS["gold"], "-"),
        ("mori_tanaka", "Mori-Tanaka", COLORS["teal"], "--"),
        ("self_consistent", "Self-consistent", COLORS["navy"], ":"),
    ]:
        x, y = _series(rows, model)
        mask = x <= .1 + 1e-12
        ax.plot(x[mask], y[mask], label=label, color=color, ls=ls, lw=2)
    _style(ax, material.unit, "Low-fraction comparison")
    ax.legend(frameon=False, fontsize=9)
    ax = axes[1]
    for model, label, color, ls in [
        ("simple_voigt", "Simple equal-strain E", COLORS["gray"], "--"),
        ("simple_reuss", "Simple equal-stress E", COLORS["navy"], ":"),
        ("halpin_tsai_demo", f"Halpin-Tsai, xi={material.xi:g}", COLORS["purple"], "-"),
    ]:
        x, y = _series(rows, model)
        ax.plot(x, y, label=label, color=color, ls=ls, lw=2)
    _style(ax, material.unit, "Separate parameter demonstration")
    ax.legend(frameon=False, fontsize=9)
    fig.supxlabel("Dilute cutoff is illustrative | Halpin-Tsai xi is uncalibrated for the spherical cases", fontsize=9)
    paths += _save(fig, directory, material.id + "_model_demonstrations")
    return paths

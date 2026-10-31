"""Evaluate each model under explicit scope rules and export tidy tables."""
import csv
from pathlib import Path

import numpy as np

from models import (
    eshelby_dilute, halpin_tsai, hashin_shtrikman, isotropic_voigt_reuss,
    mori_tanaka, rule_of_mixtures, self_consistent,
)
from utilities.input_checks import finite_scalar, fractions


FIELDS = ["case", "unit", "Vf", "Vm", "model", "E", "nu", "K", "G",
          "status", "note", "residual_norm", "iterations"]


def evaluate(material, Vf):
    """Return one row per estimate/bound; unavailable results remain blank.

    Dilute is evaluated only through Vf=0.1 as an educational restriction,
    not a universal physical threshold. Cross-ordered HS bounds are skipped
    with a reason; other calculation errors propagate and stop the run.
    """
    Vf, Vm = fractions(Vf)
    inp = material.inputs(Vf)
    rows = []

    def add(model, values=None, status="ok", note=""):
        row = dict.fromkeys(FIELDS, "")
        row.update(case=material.id, unit=material.unit, Vf=Vf, Vm=Vm,
                   model=model, status=status, note=note)
        if values is not None:
            row.update({k: v for k, v in values.items() if k in FIELDS})
        rows.append(row)

    mixtures = rule_of_mixtures(material.Ef, material.Em, Vf)
    for name in ["voigt", "reuss"]:
        add("simple_" + name, {"E": mixtures["E_" + name]},
            status="idealization", note="1-D E mixture formula; separate from 3-D bounds.")
    vr = isotropic_voigt_reuss(**inp)
    for bound in ["lower", "upper"]:
        add("isotropic_vr_" + bound, vr[bound], note="Isotropic stiffness/compliance bound.")
    if Vf <= 0.1 + 1e-12:
        # Snap away grid roundoff at the educational cutoff only.
        add("eshelby_dilute", eshelby_dilute(**{**inp, "Vf": min(Vf, 0.1)}),
            status="low_fraction", note="No inclusion interactions; accuracy is contrast-dependent.")
    else:
        add("eshelby_dilute", status="not_evaluated",
            note="Outside the configured low-fraction display interval (Vf<=0.1).")
    add("mori_tanaka", mori_tanaka(**inp), note="Spherical inclusions in a connected isotropic matrix.")
    add("self_consistent", self_consistent(**inp), note="Both phases as spheres in the effective medium.")
    try:
        hs = hashin_shtrikman(**inp)
    except ValueError as exc:
        for bound in ["lower", "upper"]:
            add("hs_" + bound, status="not_applicable", note=str(exc))
    else:
        for bound in ["lower", "upper"]:
            add("hs_" + bound, hs[bound], note="Bound for an isotropic effective composite.")
    add("halpin_tsai_demo", halpin_tsai(material.Ef, material.Em, Vf, xi=material.xi),
        status="parameter_demo", note=f"xi={material.xi:g}; separate uncalibrated demonstration.")
    return rows


def fraction_grid(vf_max=0.6, points=61):
    vf_max = finite_scalar(vf_max, "vf_max")
    if not 0 < vf_max <= 1:
        raise ValueError("vf_max must be greater than 0 and at most 1.")
    if isinstance(points, bool) or not isinstance(points, int) or not 2 <= points <= 2001:
        raise ValueError("points must be an integer between 2 and 2001.")
    # Always include requested reporting fractions when inside the sweep.
    values = list(np.linspace(0, vf_max, points))
    values += [v for v in [0.05, 0.1, 0.3, 0.5, 0.6, 1.0] if v <= vf_max]
    return sorted(set(round(float(v), 12) for v in values))


def sweep(material, *, vf_max=0.6, points=61):
    return [row for vf in fraction_grid(vf_max, points) for row in evaluate(material, vf)]


def export_csv(rows, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def key_rows(rows):
    return [r for r in rows if any(abs(r["Vf"] - v) < 1e-10 for v in [0, .05, .1, .3, .5, .6, 1])]

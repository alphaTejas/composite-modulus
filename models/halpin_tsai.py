"""Scalar Halpin-Tsai semi-empirical Young's modulus estimate.

xi is required explicitly: its value depends on reinforcement geometry,
loading direction and the chosen calibration. There is no universal xi
for all composites. In particular xi=2 must not silently be taken as an
isotropic spherical-particle model. This module predicts E only, not a
complete stiffness tensor or a rigorous bound.

Reference:
https://archive.nptel.ac.in/content/storage2/courses/101104010/lecture34/34_4.htm
"""

from ._common import finite_scalar, fractions, positive


def halpin_tsai(Ef, Em, Vf, *, xi, Vm=None):
    """Return {'E': ..., 'eta': ..., 'xi': ...}.

    eta = (Ef/Em - 1)/(Ef/Em + xi)
    E = Em*(1 + xi*eta*Vf)/(1 - eta*Vf)

    xi >= 0 is allowed. xi=0 reduces to the simple Reuss E formula.
    Call separately for each scalar Vf when making a comparison plot.
    """
    Ef, Em = positive(Ef, "Ef"), positive(Em, "Em")
    Vf, _ = fractions(Vf, Vm)
    xi = finite_scalar(xi, "xi")
    if xi < 0:
        raise ValueError("xi must be nonnegative and justified for the case.")
    ratio = Ef / Em
    eta = (ratio - 1) / (ratio + xi)
    if Vf == 0:
        E = Em
    elif Vf == 1:
        E = Ef
    else:
        E = Em * (1 + xi * eta * Vf) / (1 - eta * Vf)
    return {"E": positive(E, "effective E"), "eta": eta, "xi": xi}

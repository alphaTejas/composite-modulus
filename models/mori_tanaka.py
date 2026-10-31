"""Mori-Tanaka for isotropic phases with spherical inclusions.

Uses the actual spherical Eshelby tensor, in orthonormal Kelvin notation.
The matrix is the connected host. Ideal interfaces and linear elasticity
are assumed. This is not a cylindrical-fiber or woven-fabric model.

Reference: https://doi.org/10.1093/jge/gxab034 (spherical P,Q factors).
"""

import numpy as np

from ._common import phases, properties, properties_from_stiffness, stiffness
from .eshelby import dilute_concentration


def mori_tanaka(Ef, Em, Vf, *, nu_f, nu_m, Vm=None):
    """Return E, nu, K, G; all dimensional values retain the input unit.

    B = Vm*I + Vf*A_dil
    A_f = A_dil * B^-1
    C_eff = Cm + Vf*(Cf-Cm)*A_f

    The Vf=1 limit is algebraically correct, although the connected-matrix
    interpretation loses physical relevance when the matrix disappears.
    """
    Kf, Gf, Km, Gm, Vf, Vm = phases(Ef, Em, Vf, nu_f, nu_m, Vm)
    if Vf == 0:
        return properties(Km, Gm)
    if Vf == 1:
        return properties(Kf, Gf)
    Cf, Cm = stiffness(Kf, Gf), stiffness(Km, Gm)
    A = dilute_concentration(Ef, Em, nu_f=nu_f, nu_m=nu_m)
    B = Vm * np.eye(6) + Vf * A
    # Solve for A @ inv(B) without explicitly forming an inverse.
    Af = np.linalg.solve(B.T, A.T).T
    return properties_from_stiffness(Cm + Vf * (Cf - Cm) @ Af)

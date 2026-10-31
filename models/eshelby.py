"""Spherical Eshelby tensor and its dilute effective-stiffness estimate.

Assumptions: small strain, linear elasticity, isotropic phases, perfect
bonding, spherical inclusions. Cylindrical fibers and woven architecture
are not implemented here. The dilute approximation neglects inclusion
interactions; it is not a valid full-volume-fraction prediction.

References:
Eshelby (1957), doi:10.1098/rspa.1957.0133.
https://jfbarthelemy.github.io/echoes/99_appendices/scheme_derivations.html
"""

import warnings

import numpy as np

from ._common import (
    fractions, phases, poisson, projectors, properties_from_stiffness,
    stiffness, to_bulk_shear,
)


def sphere_eshelby(nu_m, *, notation="kelvin"):
    """Return dimensionless S for a sphere in an infinite isotropic host.

    'kelvin' returns shape (6,6), using sqrt(2) shear scaling, NOT
    engineering Voigt notation. 'cartesian' returns S[i,j,k,l].
    S maps transformation eigenstrain to constrained inclusion strain;
    it is distinct from the inhomogeneity strain-concentration tensor.
    """
    nu_m = poisson(nu_m, "nu_m")
    a = (5 * nu_m - 1) / (15 * (1 - nu_m))
    b = (4 - 5 * nu_m) / (15 * (1 - nu_m))
    if notation == "kelvin":
        J, D = projectors()
        return ((1 + nu_m) / (3 * (1 - nu_m))) * J + 2 * b * D
    if notation == "cartesian":
        delta = np.eye(3)
        return (
            a * np.einsum("ij,kl->ijkl", delta, delta)
            + b * np.einsum("ik,jl->ijkl", delta, delta)
            + b * np.einsum("il,jk->ijkl", delta, delta)
        )
    raise ValueError("notation must be 'kelvin' or 'cartesian'.")


def dilute_concentration(Ef, Em, *, nu_f, nu_m):
    """Return Kelvin A = [I + S Cm^-1 (Cf-Cm)]^-1.

    A maps the undisturbed far-field matrix strain to inclusion strain.
    """
    Kf, Gf = to_bulk_shear(Ef, nu_f)
    Km, Gm = to_bulk_shear(Em, nu_m)
    Cf, Cm = stiffness(Kf, Gf), stiffness(Km, Gm)
    S = sphere_eshelby(nu_m)
    return np.linalg.solve(np.eye(6) + S @ np.linalg.solve(Cm, Cf - Cm), np.eye(6))


def eshelby_dilute(Ef, Em, Vf, *, nu_f, nu_m, Vm=None):
    """Return E, nu, K, G from C_dil = Cm + Vf*(Cf-Cm)*A.

    A warning above Vf=0.1 is a teaching reminder, not a universal
    validity threshold. Even below 0.1 accuracy depends on contrast and
    microstructure. Vf=1 is rejected: this approximation cannot recover
    the pure-inclusion limit in general. No endpoint is patched in.
    """
    Kf, Gf, Km, Gm, Vf, _ = phases(Ef, Em, Vf, nu_f, nu_m, Vm)
    if Vf == 1:
        raise ValueError("The dilute approximation is not valid at Vf=1.")
    if Vf > 0.1:
        warnings.warn(
            "Dilute estimate at Vf > 0.1: inclusion interactions are neglected; "
            "this is an extrapolation, not a validated prediction.",
            UserWarning, stacklevel=2,
        )
    Cf, Cm = stiffness(Kf, Gf), stiffness(Km, Gm)
    A = dilute_concentration(Ef, Em, nu_f=nu_f, nu_m=nu_m)
    return properties_from_stiffness(Cm + Vf * (Cf - Cm) @ A)

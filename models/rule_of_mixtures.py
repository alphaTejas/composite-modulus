"""Simple E mixture formulas and separate 3-D isotropic elastic bounds.

The arithmetic mixture of E is a 1-D equal-strain idealization. When phase
Poisson ratios differ it is not the rigorous 3-D Voigt upper bound on E.
Use isotropic_voigt_reuss for the full isotropic stiffness/compliance bounds.

Reference: https://jfbarthelemy.github.io/echoes/99_appendices/scheme_derivations.html
"""

from ._common import fractions, phases, positive, properties


def voigt(Ef, Em, Vf, Vm=None):
    """Return the simple equal-strain estimate Vf*Ef + Vm*Em."""
    Ef, Em = positive(Ef, "Ef"), positive(Em, "Em")
    Vf, Vm = fractions(Vf, Vm)
    return Vf * Ef + Vm * Em


def reuss(Ef, Em, Vf, Vm=None):
    """Return the simple equal-stress estimate 1/(Vf/Ef + Vm/Em)."""
    Ef, Em = positive(Ef, "Ef"), positive(Em, "Em")
    Vf, Vm = fractions(Vf, Vm)
    return 1 / (Vf / Ef + Vm / Em)


def rule_of_mixtures(Ef, Em, Vf, Vm=None):
    """Return both 1-D E estimates, in the same units as Ef and Em."""
    return {"E_voigt": voigt(Ef, Em, Vf, Vm), "E_reuss": reuss(Ef, Em, Vf, Vm)}


def isotropic_voigt_reuss(Ef, Em, Vf, *, nu_f, nu_m, Vm=None):
    """Return rigorous isotropic lower/upper elastic-property bounds.

    Average K and G arithmetically for Voigt, harmonically for Reuss,
    then convert each pair to E and nu. The returned nu values are those
    of the bounding isotropic tensors, not separate bounds on nu.
    """
    Kf, Gf, Km, Gm, Vf, Vm = phases(Ef, Em, Vf, nu_f, nu_m, Vm)
    return {
        "lower": properties(1 / (Vf / Kf + Vm / Km), 1 / (Vf / Gf + Vm / Gm)),
        "upper": properties(Vf * Kf + Vm * Km, Vf * Gf + Vm * Gm),
    }

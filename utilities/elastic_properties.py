"""Isotropic elastic conversions, phase preparation and sphere parameter."""
from .input_checks import positive, poisson, fractions


def to_bulk_shear(E, nu):
    """K = E/[3(1-2nu)] and G = E/[2(1+nu)]."""
    E, nu = positive(E, "E"), poisson(nu, "nu")
    K, G = E / (3 * (1 - 2 * nu)), E / (2 * (1 + nu))
    return positive(K, "K"), positive(G, "G")


def properties(K, G):
    """Return E, nu, K, G for a stable isotropic material."""
    K, G = positive(K, "effective K"), positive(G, "effective G")
    # Ratio form avoids unnecessary products of two dimensional moduli.
    r = G / K
    E = 9 * G / (3 + r)
    nu = (3 - 2 * r) / (2 * (3 + r))
    return {"E": positive(E, "effective E"), "nu": nu, "K": K, "G": G}


def phases(Ef, Em, Vf, nu_f, nu_m, Vm=None):
    Vf, Vm = fractions(Vf, Vm)
    Kf, Gf = to_bulk_shear(Ef, nu_f)
    Km, Gm = to_bulk_shear(Em, nu_m)
    return Kf, Gf, Km, Gm, Vf, Vm


def zeta(K, G):
    """Shear polarization parameter for a sphere in an isotropic host."""
    r = K / G
    return G * (9 * r + 8) / (6 * (r + 2))




def from_bulk_shear(K, G):
    """Public inverse conversion: returns E, nu, K, G."""
    return properties(K, G)

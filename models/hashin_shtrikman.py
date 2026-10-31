"""Hashin-Shtrikman bounds for well-ordered isotropic solid phases.

These bound an isotropic effective composite, without specifying spherical
microstructure. They must not be applied directly to a directional modulus
of an aligned-fiber composite. Phases must be ordered in BOTH K and G;
ordering only by Young's modulus is insufficient.

Reference: https://rockphypy.readthedocs.io/en/latest/_modules/rockphypy/EM.html
"""

from ._common import phases, properties, zeta


def hashin_shtrikman(Ef, Em, Vf, *, nu_f, nu_m, Vm=None):
    """Return {'lower': {E,nu,K,G}, 'upper': {E,nu,K,G}}.

    For host h and other phase i, use the nonsingular form
      K = Kh + vi*(Ki-Kh)/[1+vh*(Ki-Kh)/(Kh+4Gh/3)]
      G = Gh + vi*(Gi-Gh)/[1+vh*(Gi-Gh)/(Gh+zeta_h)].
    Soft host gives the lower bound; stiff host gives the upper bound.
    The nu values describe the bounding tensors, not bounds on nu.
    """
    Kf, Gf, Km, Gm, Vf, Vm = phases(Ef, Em, Vf, nu_f, nu_m, Vm)
    if Vf == 0 or Vf == 1:
        p = properties(Km, Gm) if Vf == 0 else properties(Kf, Gf)
        return {"lower": p.copy(), "upper": p.copy()}
    if Kf >= Km and Gf >= Gm:
        soft, stiff = (Km, Gm, Vm), (Kf, Gf, Vf)
    elif Km >= Kf and Gm >= Gf:
        soft, stiff = (Kf, Gf, Vf), (Km, Gm, Vm)
    else:
        raise ValueError(
            "This implementation requires well-ordered phases: one phase "
            "must have both K >= and G >= the other. Cross-ordered phases "
            "require more general bounds."
        )

    def host_bound(host, other):
        Kh, Gh, vh = host
        Ki, Gi, vi = other
        dK, dG = Ki - Kh, Gi - Gh
        K = Kh + vi * dK / (1 + vh * dK / (Kh + 4 * Gh / 3))
        G = Gh + vi * dG / (1 + vh * dG / (Gh + zeta(Kh, Gh)))
        return properties(K, G)

    return {"lower": host_bound(soft, stiff), "upper": host_bound(stiff, soft)}

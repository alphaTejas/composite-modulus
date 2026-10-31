"""Classical self-consistent scheme for two isotropic solid phases.

Both phases are modeled as spheres in the unknown isotropic effective
medium. This is the classical scheme, not the three-phase generalized
self-consistent coated-sphere model. Numerical solution of analytical
equations does not require a finite-element simulation.

References:
https://archive.nptel.ac.in/content/storage2/courses/101104010/lecture34/34_2.htm
https://jfbarthelemy.github.io/echoes/99_appendices/scheme_derivations.html
"""

import math

import numpy as np

from ._common import finite_scalar, phases, properties, zeta


def self_consistent(Ef, Em, Vf, *, nu_f, nu_m, Vm=None,
                    tolerance=1e-9, max_iterations=500):
    """Return E, nu, K, G and solver diagnostics.

    Solve simultaneously:
      sum_i Vi*(Ki-K)/(Ki+4G/3) = 0
      sum_i Vi*(Gi-G)/(Gi+zeta(K,G)) = 0

    For any positive trial G, the bulk equation gives K explicitly as a
    weighted harmonic mean of Ki+4G/3, minus 4G/3. A cancellation-free
    equivalent is used below. The remaining shear equation is solved by
    bisection in log(G), bracketed by the phase shear moduli. Both residuals
    are checked. Only NumPy and the Python standard library are required.
    """
    Kf, Gf, Km, Gm, Vf, Vm = phases(Ef, Em, Vf, nu_f, nu_m, Vm)
    tolerance = finite_scalar(tolerance, "tolerance")
    if not 1e-12 <= tolerance <= 1e-4:
        raise ValueError("tolerance must be between 1e-12 and 1e-4.")
    if isinstance(max_iterations, (bool, np.bool_)) or not isinstance(
        max_iterations, (int, np.integer)
    ) or max_iterations < 1:
        raise ValueError("max_iterations must be a positive integer.")

    def endpoint(K, G):
        return {**properties(K, G), "converged": True,
                "residual_norm": 0.0, "iterations": 0}

    if Vf == 0:
        return endpoint(Km, Gm)
    if Vf == 1:
        return endpoint(Kf, Gf)
    if Kf == Km and Gf == Gm:
        return endpoint(Km, Gm)

    scale = max(Kf, Gf, Km, Gm)
    Ks = np.array([Kf, Km]) / scale
    Gs = np.array([Gf, Gm]) / scale
    volumes = np.array([Vf, Vm])

    def evaluate(G):
        bulk_weights = volumes / (Ks + 4 * G / 3)
        K = float(np.dot(bulk_weights, Ks) / np.sum(bulk_weights))
        rK = float(np.sum(volumes * (Ks - K) / (Ks + 4 * G / 3)))
        rG = float(np.sum(volumes * (Gs - G) / (Gs + zeta(K, G))))
        return K, rK, rG

    lower, upper = float(np.min(Gs)), float(np.max(Gs))
    _, _, r_lower = evaluate(lower)
    _, _, r_upper = evaluate(upper)
    if r_lower < -tolerance or r_upper > tolerance:
        raise RuntimeError("Could not bracket a positive self-consistent solution.")
    lo, hi = math.log(lower), math.log(upper)
    last_norm = float("inf")
    for iteration in range(1, max_iterations + 1):
        mid = (lo + hi) / 2
        G = math.exp(mid)
        K, rK, rG = evaluate(G)
        last_norm = max(abs(rK), abs(rG))
        if last_norm <= tolerance:
            return {**properties(K * scale, G * scale), "converged": True,
                    "residual_norm": last_norm,
                    "iterations": iteration}
        if rG > 0:
            lo = mid
        else:
            hi = mid
    raise RuntimeError(
        f"Self-consistent solver did not converge; residual={last_norm:.3g}. "
        "Check the phase properties or increase max_iterations."
    )

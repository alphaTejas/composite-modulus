"""Orthonormal Kelvin tensor operations; not engineering Voigt notation."""
import numpy as np
from .elastic_properties import properties


def projectors():
    """Hydrostatic J and deviatoric D in orthonormal Kelvin notation.

    Vector order: [11, 22, 33, sqrt(2)*23, sqrt(2)*13, sqrt(2)*12].
    The same scaling applies to stress and strain, so ordinary matrix
    multiplication represents fourth-order tensor contraction.
    """
    h = np.array([1, 1, 1, 0, 0, 0], dtype=float) / np.sqrt(3)
    J = np.outer(h, h)
    return J, np.eye(6) - J


def stiffness(K, G):
    J, D = projectors()
    return 3 * K * J + 2 * G * D


def properties_from_stiffness(C):
    """Extract isotropic K and G from a Kelvin stiffness matrix."""
    J, D = projectors()
    K = float(np.sum(J * C) / 3)
    G = float(np.sum(D * C) / 10)
    return properties(K, G)

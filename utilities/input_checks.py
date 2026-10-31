"""Validation shared by all models; no silent property assumptions."""
import math
import numpy as np


def finite_scalar(value, name):
    if isinstance(value, (bool, np.bool_)) or np.ndim(value) != 0:
        raise ValueError(f"{name} must be a finite real scalar.")
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite real scalar.") from exc
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite.")
    return value


def positive(value, name):
    value = finite_scalar(value, name)
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero.")
    return value


def poisson(value, name):
    value = finite_scalar(value, name)
    if not -1 < value < 0.5:
        raise ValueError(f"{name} must satisfy -1 < nu < 0.5.")
    return value


def fractions(Vf, Vm=None):
    Vf = finite_scalar(Vf, "Vf")
    if not 0 <= Vf <= 1:
        raise ValueError("Vf must lie between 0 and 1 (not a percentage).")
    if Vm is not None:
        Vm = finite_scalar(Vm, "Vm")
        if not 0 <= Vm <= 1 or not math.isclose(Vf + Vm, 1, rel_tol=0, abs_tol=1e-10):
            raise ValueError("Vm must lie between 0 and 1 and Vf + Vm must equal 1.")
    # Use the exact complement after validating any supplied Vm.
    return Vf, 1.0 - Vf



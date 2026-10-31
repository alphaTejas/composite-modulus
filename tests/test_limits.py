import unittest
import warnings

import numpy as np

from models import (
    eshelby_dilute, halpin_tsai, hashin_shtrikman, mori_tanaka,
    reuss, self_consistent, sphere_eshelby, voigt,
)
from utilities.elastic_properties import from_bulk_shear, to_bulk_shear


class LimitTests(unittest.TestCase):
    def test_conversion_round_trip(self):
        for E in [1, 70, 200e9]:
            for nu in [-.3, 0, .35, .49]:
                with self.subTest(E=E, nu=nu):
                    result = from_bulk_shear(*to_bulk_shear(E, nu))
                    self.assertAlmostEqual(result["E"] / E, 1, places=12)
                    self.assertAlmostEqual(result["nu"], nu, places=12)

    def test_phase_endpoints(self):
        for model in [mori_tanaka, self_consistent]:
            for Vf, expected in [(0, 3.5), (1, 70)]:
                with self.subTest(model=model.__name__, Vf=Vf):
                    result = model(70, 3.5, Vf, nu_f=.2, nu_m=.35)
                    self.assertAlmostEqual(result["E"], expected, places=11)
        for Vf, expected in [(0, 3.5), (1, 70)]:
            for fn in [voigt, reuss]:
                self.assertAlmostEqual(fn(70, 3.5, Vf), expected)
            self.assertAlmostEqual(halpin_tsai(70, 3.5, Vf, xi=2)["E"], expected)
            for bound in hashin_shtrikman(70, 3.5, Vf, nu_f=.2, nu_m=.35).values():
                self.assertAlmostEqual(bound["E"], expected)

    def test_identical_phases(self):
        for fn in [mori_tanaka, self_consistent, eshelby_dilute]:
            self.assertAlmostEqual(fn(7, 7, .05, nu_f=.32, nu_m=.32)["E"], 7)

    def test_invalid_fractions_and_moduli(self):
        for value in [-.1, 1.1, float("nan"), float("inf"), True, [.1]]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                voigt(70, 3.5, value)
        for E in [0, -1, float("nan"), float("inf")]:
            with self.assertRaises(ValueError):
                voigt(E, 3.5, .2)
        with self.assertRaises(ValueError):
            voigt(70, 3.5, .2, Vm=.7)

    def test_invalid_poisson_ratios(self):
        for nu in [-1, .5, float("nan")]:
            with self.assertRaises(ValueError):
                mori_tanaka(70, 3.5, .2, nu_f=.2, nu_m=nu)

    def test_dilute_warning_and_rejected_endpoint(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            eshelby_dilute(70, 3.5, .3, nu_f=.2, nu_m=.35)
        self.assertEqual(len(caught), 1)
        with self.assertRaises(ValueError):
            eshelby_dilute(70, 3.5, 1, nu_f=.2, nu_m=.35)

    def test_halpin_tsai_reuss_limit(self):
        for vf in [0, .1, .5, 1]:
            self.assertAlmostEqual(halpin_tsai(70, 3.5, vf, xi=0)["E"], reuss(70, 3.5, vf))
        with self.assertRaises(ValueError):
            halpin_tsai(70, 3.5, .2, xi=-1)

    def test_solver_failure_is_reported(self):
        with self.assertRaises(RuntimeError):
            self_consistent(70, 3.5, .4, nu_f=.2, nu_m=.35, max_iterations=1)
        with self.assertRaises(ValueError):
            self_consistent(70, 3.5, .4, nu_f=.2, nu_m=.35, tolerance=0)

    def test_equal_shear_phase_case(self):
        result = self_consistent(12, 13, .4, nu_f=.2, nu_m=.3)
        self.assertAlmostEqual(result["G"], 5, places=12)

    def test_kelvin_and_cartesian_eshelby_agree(self):
        basis = np.zeros((6, 3, 3))
        for i in range(3):
            basis[i, i, i] = 1
        for a, (i, j) in enumerate([(1, 2), (0, 2), (0, 1)], 3):
            basis[a, i, j] = basis[a, j, i] = 1 / np.sqrt(2)
        for nu in [-.3, 0, .2, .35, .49]:
            S4 = sphere_eshelby(nu, notation="cartesian")
            converted = np.einsum("aij,ijkl,bkl->ab", basis, S4, basis)
            np.testing.assert_allclose(converted, sphere_eshelby(nu), atol=1e-14)
        with self.assertRaises(ValueError):
            sphere_eshelby(.3, notation="voigt")


if __name__ == "__main__":
    unittest.main()

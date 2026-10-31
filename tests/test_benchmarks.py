"""Analytical fixtures and seeded checks; no experimental accuracy claim."""
from fractions import Fraction as F
import unittest

import numpy as np

from models import (
    eshelby_dilute, hashin_shtrikman, isotropic_voigt_reuss,
    mori_tanaka, self_consistent,
)
from utilities.elastic_properties import to_bulk_shear


class BenchmarkTests(unittest.TestCase):
    def test_exact_rational_fixture(self):
        result = mori_tanaka(1800 / 17, 90 / 7, .25, nu_f=11 / 34, nu_m=2 / 7)
        expected_K = F(10) + F(1, 4) * 90 / (1 + F(3, 4) * 90 / F(50, 3))
        expected_G = F(5) + F(1, 4) * 35 / (1 + F(3, 4) * 35 / F(125, 12))
        self.assertAlmostEqual(result["K"], float(expected_K), places=11)
        self.assertAlmostEqual(result["G"], float(expected_G), places=11)

    def test_120_seeded_material_cases(self):
        rng = np.random.default_rng(42)
        for case in range(120):
            Ef, Em = 10 ** rng.uniform(-2, 4, 2)
            nuf, num = rng.uniform(-.3, .48, 2)
            vf = float(rng.uniform(.001, .999))
            inp = dict(Ef=Ef, Em=Em, Vf=vf, nu_f=nuf, nu_m=num)
            with self.subTest(case=case):
                kf, gf = to_bulk_shear(Ef, nuf)
                km, gm = to_bulk_shear(Em, num)
                z = gm * (9 * km + 8 * gm) / (6 * (km + 2 * gm))
                mt = mori_tanaka(**inp)
                expected = [
                    km + vf * (kf - km) / (1 + (1 - vf) * (kf - km) / (km + 4 * gm / 3)),
                    gm + vf * (gf - gm) / (1 + (1 - vf) * (gf - gm) / (gm + z)),
                ]
                np.testing.assert_allclose([mt["K"], mt["G"]], expected, rtol=2e-10)
                dilute = eshelby_dilute(**{**inp, "Vf": .02})
                np.testing.assert_allclose([dilute["K"], dilute["G"]], [
                    km + .02 * (kf - km) * (km + 4 * gm / 3) / (kf + 4 * gm / 3),
                    gm + .02 * (gf - gm) * (gm + z) / (gf + z),
                ], rtol=2e-10)
                sc = self_consistent(**inp, tolerance=1e-11)
                k, g = sc["K"], sc["G"]
                zg = g * (9 * k + 8 * g) / (6 * (k + 2 * g))
                residuals = [
                    vf * (kf - k) / (kf + 4 * g / 3) + (1 - vf) * (km - k) / (km + 4 * g / 3),
                    vf * (gf - g) / (gf + zg) + (1 - vf) * (gm - g) / (gm + zg),
                ]
                np.testing.assert_allclose(residuals, 0, atol=1.1e-11)
                swapped = self_consistent(Em, Ef, 1-vf, nu_f=num, nu_m=nuf, tolerance=1e-11)
                self.assertAlmostEqual(swapped["E"] / sc["E"], 1, places=8)
                scaled = self_consistent(**{**inp, "Ef": Ef*1e9, "Em": Em*1e9}, tolerance=1e-11)
                self.assertAlmostEqual(scaled["E"] / (sc["E"]*1e9), 1, places=8)
                vr = isotropic_voigt_reuss(**inp)
                if (kf-km)*(gf-gm) >= 0:
                    hs = hashin_shtrikman(**inp)
                    bound = "lower" if km <= kf and gm <= gf else "upper"
                    for key in ["E", "K", "G"]:
                        self.assertLessEqual(vr["lower"][key]*(1-1e-8), hs["lower"][key])
                        self.assertLessEqual(hs["lower"][key]*(1-1e-8), sc[key])
                        self.assertLessEqual(sc[key], hs["upper"][key]*(1+1e-8))
                        self.assertLessEqual(hs["upper"][key], vr["upper"][key]*(1+1e-8))
                        np.testing.assert_allclose(mt[key], hs[bound][key], rtol=1e-8)
                else:
                    with self.assertRaises(ValueError):
                        hashin_shtrikman(**inp)


if __name__ == "__main__":
    unittest.main()

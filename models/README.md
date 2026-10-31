# Composite modulus: models folder

This folder implements six model families in eight Python files. It is a
working first stage of the larger project, not a completed woven-fiber model.

## Files

| File | Purpose |
|---|---|
| `__init__.py` | Exposes the public functions for importing |
| `_common.py` | Compatibility imports for the shared utilities |
| `rule_of_mixtures.py` | Simple Voigt/Reuss E estimates and separate 3-D isotropic bounds |
| `eshelby.py` | Spherical Eshelby tensor, strain concentration and dilute estimate |
| `mori_tanaka.py` | Spherical Mori-Tanaka calculation using the Eshelby tensor |
| `self_consistent.py` | Coupled bulk/shear self-consistent equations and solver checks |
| `hashin_shtrikman.py` | Isotropic bounds for phases ordered in both bulk and shear modulus |
| `halpin_tsai.py` | Scalar semi-empirical estimate with explicitly supplied geometry parameter |

`_common.py` now re-exports the shared functions from the sibling `utilities/`
folder. Keep both folders together in the complete project. `__init__.py` is
a package entry point, not a model. The model function interfaces are unchanged.

## Installation and running

Requires Python 3.10 or newer and NumPy. From the directory containing
the `models` folder:

```sh
python -m pip install numpy
```

Create a Python script beside `models/`, or use a Python interpreter from that
directory. Do not run the individual model files directly: they use package
imports. Each function accepts one scalar volume fraction at a time.

```python
from models import (
    rule_of_mixtures, isotropic_voigt_reuss, sphere_eshelby,
    eshelby_dilute, mori_tanaka, self_consistent,
    hashin_shtrikman, halpin_tsai,
)

# Hypothetical teaching values, NOT a sourced material dataset.
# All dimensional inputs below are in GPa; all dimensional outputs are GPa.
base = dict(Ef=70.0, Em=3.5, Vf=0.05, Vm=0.95)
elastic = dict(**base, nu_f=0.20, nu_m=0.35)

print("Simple E mixtures:", rule_of_mixtures(**base))
print("Isotropic Voigt/Reuss:", isotropic_voigt_reuss(**elastic))
print("Spherical Eshelby tensor (Kelvin):", sphere_eshelby(0.35))
print("Eshelby dilute:", eshelby_dilute(**elastic))
print("Mori-Tanaka:", mori_tanaka(**elastic))
print("Self-consistent:", self_consistent(**elastic))
print("Hashin-Shtrikman bounds:", hashin_shtrikman(**elastic))

# Separate parameter demonstration only. xi=2 has not been calibrated for
# the hypothetical spherical material above, so this is NOT an equivalent
# spherical benchmark curve. Select xi for the actual geometry/direction.
print("Halpin-Tsai parameter demonstration:", halpin_tsai(**base, xi=2.0))
```

## Inputs and outputs

- `Ef`, `Em`: strictly positive finite reinforcement and matrix Young's moduli.
- `Vf`: reinforcement volume fraction in [0,1], e.g. 0.30 for 30%.
- `Vm`: optional matrix fraction. If supplied it must satisfy Vf + Vm = 1
  within 1e-10. The internal value is the exact complement 1-Vf.
- `nu_f`, `nu_m`: phase Poisson ratios, each strictly between -1 and 0.5.
  Required for 3-D elastic models; never silently assumed.
- `xi`: explicit nonnegative Halpin-Tsai geometry/loading/calibration parameter.

The sphere-based predictors return dictionaries with `E`, `nu`, `K`, `G`.
The self-consistent function also returns convergence diagnostics and raises
an error if its dimensionless residual exceeds the requested tolerance.
Bounds return `lower` and `upper` dictionaries; their `nu` entries are the
Poisson ratios of bounding tensors, not standalone bounds on Poisson ratio.
Simple E mixtures return `E_voigt` and `E_reuss`. Halpin-Tsai returns `E`,
`eta`, `xi`. The Eshelby tensor itself is dimensionless.

## Scope and comparison rules

1. Eshelby/dilute and Mori-Tanaka assume isotropic phases, spherical inclusions,
   perfect bonding, small strain and linear elasticity. Self-consistent uses
   spherical representatives of both phases in an unknown effective medium.
   There is no cylindrical-fiber, anisotropic natural-fiber, woven-fabric,
   damage, void, temperature, moisture or interface-slip model here.
2. Dilute theory neglects interactions and is intended for low inclusion
   content. The warning above Vf=0.1 is an educational reminder, not a universal
   accuracy threshold. Vf=1 is rejected rather than forced to the fiber value.
   Dilute extrapolations need not satisfy bounds over the full fraction range.
3. The arithmetic mixture of Young's moduli is a 1-D equal-strain idealization,
   not the general 3-D Voigt E upper bound when phase Poisson ratios differ.
   For isotropic 3-D comparisons use `isotropic_voigt_reuss`, which averages
   bulk/shear stiffness or compliance before converting to Young's modulus.
4. Hashin-Shtrikman bounds here require one phase to be at least as stiff in
   BOTH K and G. Cross-ordered phases raise an explanatory error. The bounds
   apply to an isotropic effective medium, not an arbitrary directional E.
5. For well-ordered phases with the softer material as matrix, spherical
   Mori-Tanaka coincides with the HS lower K/G bound (and corresponding E).
   Coincident curves are expected; do not fabricate separation between them.
6. Halpin-Tsai is a separate semi-empirical estimate. Its geometry and output
   direction must match a comparison case before plotting it with other models.
7. Fraction endpoints are mathematical checks, not a guarantee of physical
   accuracy at high inclusion concentration. No experimental validation or
   sourced biocomposite material case is supplied in this folder.
8. Tensor matrices use orthonormal Kelvin notation, in order
   [11,22,33,sqrt(2)*23,sqrt(2)*13,sqrt(2)*12]. They cannot be combined directly
   with engineering-Voigt matrices. `sphere_eshelby(..., notation="cartesian")`
   returns a fourth-order 3x3x3x3 tensor instead.

## Equations and references

Conversions: K=E/[3(1-2nu)], G=E/[2(1+nu)], E=9KG/(3K+G).
Self-consistent solves the phase-weighted bulk and shear contrast residuals
simultaneously; see the function docstring for the equations. All source
equations were implemented independently rather than copied from a library.

- Eshelby, J. D. (1957), *The determination of the elastic field of an
  ellipsoidal inclusion, and related problems*:
  https://doi.org/10.1098/rspa.1957.0133
- Echoes developer documentation, homogenization schemes and concentration
  tensors: https://jfbarthelemy.github.io/echoes/99_appendices/scheme_derivations.html
- *Effective moduli of rocks predicted by the Kuster–Toksöz and Mori–Tanaka
  models* (2021), spherical concentration factors, Appendix C:
  https://doi.org/10.1093/jge/gxab034
- RockPhyPy developer documentation, HS bound formulas:
  https://rockphypy.readthedocs.io/en/latest/_modules/rockphypy/EM.html
- NPTEL, self-consistent model:
  https://archive.nptel.ac.in/content/storage2/courses/101104010/lecture34/34_2.htm
- NPTEL, Halpin-Tsai model and geometry dependence:
  https://archive.nptel.ac.in/content/storage2/courses/101104010/lecture34/34_4.htm

## Implementation checks performed

The original model-only version passed 2,484 checks. The complete project now
includes a repeatable test suite covering 120 seeded material cases, spherical
tensor shear scaling, independent scalar-versus-tensor formulas, a rational
fixture, phase endpoints, identical phases, solver residuals, phase exchange,
unit scaling, applicable bounds and input handling. See the actual run record
in `outputs/verification.txt`. These checks verify implementation, not
experimental accuracy.

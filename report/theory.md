# Analytical prediction of effective composite modulus

## Objective and scope

Predict effective Young's modulus E from phase properties and volume fractions.
For a void-free two-phase material, Vf + Vm = 1. Here f denotes the inclusion
or reinforcement phase, not necessarily a geometrically modeled fiber.
The implemented 3-D estimates assume isotropic solid constituents, spherical
inclusions, perfect bonding, small strain and linear elasticity. No finite
element analysis is performed. Numerically solving implicit analytical
equations is still part of this analytical modeling workflow.

E measures elastic stiffness, not tensile strength. A larger E means a smaller
elastic extension under the same stress. It does not establish the failure
load, toughness, fatigue life, sustainability or suitability of a product.

## Why the original four inputs are insufficient for every method

Ef, Em, Vf and Vm are enough for simple scalar mixture formulas. Three-dimensional
elastic calculations also need nu_f and nu_m, the phase Poisson ratios.
Geometry and orientation determine whether the effective response is isotropic
or directional. Isotropic phases each require two independent elastic constants.
The required conversions are:

```text
K = E / [3(1 - 2 nu)]
G = E / [2(1 + nu)]
E = 9 K G / (3 K + G)
nu = (3 K - 2 G) / [2(3 K + G)]
```

All moduli use the same unit, here GPa in the shipped material cases. Volume
fractions and Poisson ratios are dimensionless. Stability requires E > 0 and
-1 < nu < 0.5 for the supported isotropic solid phases.

## Family 1: Rule of Mixtures

The equal-strain one-dimensional estimate is E = Vf Ef + Vm Em. The equal-stress
estimate is E = 1/(Vf/Ef + Vm/Em). These are useful baselines. The arithmetic
E formula is not the general 3-D Voigt E bound if phase Poisson ratios differ.
For an isotropic 3-D comparison the program instead averages K and G, then
converts the resulting pair to E: arithmetic averages give Voigt stiffness,
and harmonic averages give Reuss compliance. [R1]

## Family 2: Eshelby inclusion theory and dilute approximation

Eshelby's solution describes the response of an ellipsoidal inclusion in an
infinite elastic host. This project implements the spherical case. The Eshelby
tensor S relates a transformation eigenstrain to constrained inclusion strain.
For a material inhomogeneity, the dilute strain-concentration tensor is
A = [I + S Cm^-1 (Cf - Cm)]^-1. The effective dilute stiffness is
Cm + Vf (Cf - Cm) A. [R2, R3]

For isotropic spheres define zeta_m = Gm(9Km + 8Gm)/[6(Km + 2Gm)]. Equivalent
scalar expressions provide an independent check of the tensor implementation:

```text
K_dil = Km + Vf (Kf - Km)(Km + 4Gm/3)/(Kf + 4Gm/3)
G_dil = Gm + Vf (Gf - Gm)(Gm + zeta_m)/(Gf + zeta_m)
```

The dilute approximation neglects interactions. Displaying it only through
Vf=0.1 is a chosen teaching restriction, not an accuracy guarantee. Its formula
does not generally recover the pure-inclusion endpoint and may violate bounds
when extrapolated. The project does not patch that endpoint artificially.

## Family 3: Mori-Tanaka

Mori-Tanaka uses average matrix strain as the surrounding strain seen by the
inclusions. The tensor calculation normalizes the dilute concentration factors
so that phase-averaged strain equals macroscopic strain. The spherical scalar
forms are:

```text
K_MT = Km + Vf(Kf - Km)/[1 + Vm(Kf - Km)/(Km + 4Gm/3)]
G_MT = Gm + Vf(Gf - Gm)/[1 + Vm(Gf - Gm)/(Gm + zeta_m)]
```

It assumes a matrix-inclusion topology. It is an estimate, and a mathematical
endpoint or bound check does not demonstrate experimental accuracy. [R3]

## Family 4: Classical self-consistent scheme

Each phase is represented as a sphere embedded in the unknown effective
medium. Solve the following phase-weighted residual equations for K and G:

```text
sum_i Vi (Ki - K)/(Ki + 4G/3) = 0
sum_i Vi (Gi - G)/(Gi + zeta(K,G)) = 0
zeta(K,G) = G(9K + 8G)/[6(K + 2G)]
```

The bulk equation is rearranged analytically for K at a trial G. The remaining
shear residual is solved by bisection in log(G), between phase shear moduli.
Both dimensionless residuals are checked against a tolerance before accepting
the result. The implementation is classical self-consistent, not the distinct
generalized self-consistent coated-sphere model. [R4]

## Family 5: Hashin-Shtrikman bounds

These constrain isotropic effective K and G based on constituent properties
and fractions. This implementation requires the phases to be ordered in both
K and G. It rejects cross-ordered phases in direct model calls; comparison
tables mark those bounds as not applicable. Soft-reference and stiff-reference
formulas provide lower and upper bounds, which are converted to E. [R5]

In the well-ordered isotropic spherical case, Mori-Tanaka equals the HS lower
bound when the matrix is the softer phase and the upper bound when the matrix
is the stiffer phase. Overlap is a consistency check. HS bounds are not general
bounds for arbitrary directional Young's moduli of aligned-fiber materials.

## Family 6: Halpin-Tsai

```text
eta = (Ef/Em - 1)/(Ef/Em + xi)
E_HT = Em (1 + xi eta Vf)/(1 - eta Vf)
```

This semi-empirical relation requires a geometry/loading-dependent parameter
xi. The shipped xi=2 is an uncalibrated demonstration, not a universal spherical
inclusion law. Its graph is separated from the 3-D isotropic comparison. With
xi=0 it reduces to the simple Reuss E expression. [R6]

## Interpretation of the six families

Bounds, predictions, theoretical building blocks and semi-empirical estimates
serve different roles. Counting six families does not imply six independent,
equally applicable curves. Their agreement or disagreement must be interpreted
using their assumptions, not by choosing the largest result or averaging them.
References R1-R9 are listed in references.md.

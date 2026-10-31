# Background, learning guide and viva preparation

## Composite classification

A composite combines distinct constituents. The reinforcement and surrounding
matrix cooperate to carry load; the interface transfers stress between them.
Classification by matrix includes polymer, metal and ceramic matrix materials.
Classification by reinforcement includes particles, continuous or short fibers,
and other forms. Architecture includes unidirectional alignment, woven textiles,
random reinforcement and laminates. These categories describe different
features and should not be treated as competing names. [R7, R8]

Natural plant fibers such as flax, jute and hemp are relevant to biocomposite
research. Natural-fiber reinforcement does not itself establish biodegradability
of the whole composite. The matrix and processing choices still matter.
The present numerical examples are hypothetical and must not be labeled as
measured flax, jute, hemp, glass or carbon composite data.

## Woven structures

Six examples for the background review are plain, twill, satin, basket, warp
rib and weft rib. Plain alternates yarn crossings; twill has a progressing
diagonal pattern; satin spaces interlacings; basket groups yarns; warp and weft
rib are derivatives of plain weave with different directional grouping. [R9]
This is a list of examples, not an assertion that only six woven types exist.

A woven stiffness model needs warp/weft fractions, yarn stiffnesses and
directions, crimp or waviness, and matrix pockets. Treating a woven yarn as a
perfect isotropic sphere loses these architectural effects. This project
reviews woven structures but does not calculate their effective stiffness.

## What to learn and in which order

1. Calculate stress as force/area and strain as change in length/original length.
2. Understand E as the slope in the elastic stress-strain region.
3. Distinguish volume fraction from mass fraction; use fractions such as 0.30.
4. Calculate simple equal-strain/equal-stress mixtures by hand.
5. Learn nu, K, G and isotropic elastic-property conversion.
6. Understand a strain-concentration factor before studying the Eshelby tensor.
7. Explain how Mori-Tanaka changes the dilute surrounding-strain assumption.
8. Explain why the self-consistent properties appear on both sides of its equations.
9. Distinguish bounds from predictions and calibration from verification.
10. Read each plot's assumptions, units and data provenance before interpreting it.

## Viva questions with short answers

**What are you predicting?** Effective elastic Young's modulus of an idealized
two-phase composite, with the assumptions stated for each method.

**Why is E not strength?** E describes elastic deformation. Strength concerns
failure and requires additional information.

**Why do you need Poisson ratios?** Three-dimensional isotropic elasticity needs
two independent phase constants. E alone does not specify K and G.

**Why do the mixture formulas differ?** They assume equal strain or equal stress
between the phases, respectively.

**Is Eshelby itself a complete finite-concentration composite model?** Its
inclusion solution supplies concentration information. Here it supports a
dilute estimate and the Mori-Tanaka implementation.

**Why do some curves overlap?** For the stated ordered isotropic spherical
case, Mori-Tanaka matches the appropriate Hashin-Shtrikman bound.

**Why does the dilute line stop early?** Inclusion interactions are neglected.
The display restriction prevents implying accuracy across the whole range.

**Why is Halpin-Tsai on another graph?** Its xi parameter needs a geometry and
loading justification before an equivalent comparison can be claimed.

**Why is a numerical solver used in an analytical project?** The analytical
self-consistent equations are implicit. Solving those equations numerically
does not require meshing or finite elements.

**What has been verified?** Limiting cases, tensor conventions, independent
formula reductions, residuals, scaling, bounds and the executable workflow.

**What has not been validated?** Accuracy against experiments or measured
properties of an actual biocomposite specimen.

**What would be needed for woven or real natural-fiber material?** Sourced
phase properties, appropriate anisotropy, geometry/orientation descriptions,
architecture modeling and reference measurements for comparison.

# Results and discussion

All shipped cases use hypothetical inputs. These results demonstrate the models; they are not measurements or validated predictions of a real biocomposite.

## Stiff spherical inclusions (illustrative)

Hypothetical teaching inputs, not measured glass/epoxy data. xi=2 is an uncalibrated parameter demonstration and is not a spherical-model calibration.

Ef=70, Em=3.5 GPa; nu_f=0.2, nu_m=0.35.

| Vf | Mori-Tanaka (GPa) | Self-consistent | HS lower | HS upper |
|---|---|---|---|---|
| 0.05 | 3.847096 | 3.863537 | 3.847096 | 5.374874 |
| 0.1 | 4.227868 | 4.302733 | 4.227868 | 7.308810 |
| 0.3 | 6.213662 | 7.443979 | 6.213662 | 15.960330 |
| 0.5 | 9.489556 | 16.107946 | 9.489556 | 26.657094 |
| 0.6 | 12.087590 | 24.121328 | 12.087590 | 33.048728 |

Across the computed sweep, Mori-Tanaka E changes from 3.500000 to 12.087590 GPa (+245.36%). The trend reflects the assumed phase contrast and geometry.

![Isotropic comparison](../figures/stiff_inclusions_isotropic_comparison.png)

![Separate demonstrations](../figures/stiff_inclusions_model_demonstrations.png)

## Moderate stiffness contrast (illustrative)

Hypothetical sensitivity case, not a measured biocomposite dataset. Real natural fibers require geometry and anisotropic-property decisions. xi=2 is an uncalibrated demonstration.

Ef=30, Em=3 GPa; nu_f=0.3, nu_m=0.35.

| Vf | Mori-Tanaka (GPa) | Self-consistent | HS lower | HS upper |
|---|---|---|---|---|
| 0.05 | 3.265951 | 3.275885 | 3.265951 | 3.780784 |
| 0.1 | 3.554972 | 3.598834 | 3.554972 | 4.592243 |
| 0.3 | 5.016853 | 5.614022 | 5.016853 | 8.222153 |
| 0.5 | 7.271400 | 9.650932 | 7.271400 | 12.659957 |
| 0.6 | 8.932614 | 12.721859 | 8.932614 | 15.281120 |

Across the computed sweep, Mori-Tanaka E changes from 3.000000 to 8.932614 GPa (+197.75%). The trend reflects the assumed phase contrast and geometry.

![Isotropic comparison](../figures/moderate_contrast_isotropic_comparison.png)

![Separate demonstrations](../figures/moderate_contrast_model_demonstrations.png)

## Soft spherical inclusions (illustrative)

Hypothetical case to check softening and reversed phase ordering. The inclusion is a solid, not a void. xi=2 is an uncalibrated demonstration.

Ef=1, Em=10 GPa; nu_f=0.3, nu_m=0.25.

| Vf | Mori-Tanaka (GPa) | Self-consistent | HS lower | HS upper |
|---|---|---|---|---|
| 0.05 | 9.215423 | 9.190006 | 7.994991 | 9.215423 |
| 0.1 | 8.490159 | 8.395297 | 6.607517 | 8.490159 |
| 0.3 | 6.065214 | 5.452283 | 3.701626 | 6.065214 |
| 0.5 | 4.202618 | 3.181374 | 2.398872 | 4.202618 |
| 0.6 | 3.424082 | 2.404518 | 1.984088 | 3.424082 |

Across the computed sweep, Mori-Tanaka E changes from 10.000000 to 3.424082 GPa (-65.76%). The trend reflects the assumed phase contrast and geometry.

![Isotropic comparison](../figures/soft_inclusions_isotropic_comparison.png)

![Separate demonstrations](../figures/soft_inclusions_model_demonstrations.png)

## Interpretation and limitations

For the well-ordered isotropic sphere cases, Mori-Tanaka follows the HS boundary associated with the matrix phase. This overlap is expected. Self-consistent uses a different surrounding medium, so differing predictions are not a solver error.

The dilute model is displayed only through Vf=0.1, an educational display cutoff rather than a universal validity threshold. Halpin-Tsai is kept as a separate uncalibrated parameter demonstration. No curve is ranked as experimentally most accurate.

A real biocomposite or woven-material conclusion requires sourced inputs, an appropriate geometry/anisotropy model and validation data. These are not supplied by the professor's handwritten outline alone.

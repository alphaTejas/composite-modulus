# References and data provenance

Accessed for this project on 31 October 2026. Material inputs in the shipped
JSON are explicitly hypothetical; none of the references below is claimed as
the source of those numeric inputs. References support the theory and checks.

- **R1.** Voigt/Reuss tensor averaging: [Echoes developer documentation, homogenization schemes](https://jfbarthelemy.github.io/echoes/99_appendices/scheme_derivations.html).
- **R2.** Eshelby, J. D. (1957), *The determination of the elastic field of an ellipsoidal inclusion, and related problems*. [Original paper DOI](https://doi.org/10.1098/rspa.1957.0133).
- **R3.** *Effective moduli of rocks predicted by the Kuster-Toksoz and Mori-Tanaka models* (2021), Appendix C spherical concentration factors. [Original research DOI](https://doi.org/10.1093/jge/gxab034).
- **R4.** [NPTEL, Lecture 34, Self Consistent Method](https://archive.nptel.ac.in/content/storage2/courses/101104010/lecture34/34_2.htm).
- **R5.** [RockPhyPy developer documentation, EM.HS implementation](https://rockphypy.readthedocs.io/en/latest/_modules/rockphypy/EM.html), used as an independent formula reference, not copied source code.
- **R6.** [NPTEL, Lecture 34, Halpin-Tsai Semi-Empirical Relations](https://archive.nptel.ac.in/content/storage2/courses/101104010/lecture34/34_4.htm).
- **R7.** [NPTEL, Introduction to Composites, classification](https://archive.nptel.ac.in/content/storage2/courses/101104010/lecture1/1_4.htm).
- **R8.** [NPTEL, Reinforcement: Materials and Forms](https://archive.nptel.ac.in/content/storage2/courses/101104010/lecture2/2_3.htm).
- **R9.** [NPTEL, Weave Design](https://archive.nptel.ac.in/content/storage2/courses/116102005/m5-design/l21-weave%20design.htm).

Before claiming a real material prediction, record the actual source, phase
conditioning, units, loading direction and the justification for any isotropic
approximation in the material file. Do not change source_status to measured
or literature unless the data provenance supports that description.

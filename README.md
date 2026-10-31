# Composite Modulus: analytical major-project framework

**Live calculator:** [Composite Modulus Lab](https://composite-modulus-lab.streamlit.app/)

**Source code:** [alphaTejas/composite-modulus](https://github.com/alphaTejas/composite-modulus)

Predict effective elastic Young's modulus using six model families. This is
a complete runnable implementation of the agreed **isotropic spherical-inclusion
scope**, with illustrative material studies, reproducible results and a report.
It does not claim to predict woven architecture or validate a real biocomposite.

## Quick start in VS Code

1. Extract the complete project ZIP and open **the folder containing main.py**
   using File > Open Folder. Keep all project folders together.
2. Install Python 3.10+ and Microsoft's Python extension.
3. Use Python: Create Environment > Venv and select it with Python: Select
   Interpreter. Open a new VS Code terminal in the project folder.
4. Install dependencies and run:

```sh
python -m pip install -r requirements.txt
python main.py
```

On macOS/Linux, if your command is `python3`, use that spelling consistently.
If desired, create and activate the environment manually:

```sh
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

```powershell
# Windows PowerShell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, select `.venv` through VS Code instead or use
`.\.venv\Scripts\python.exe` directly in place of `python`; changing the
machine's script policy is unnecessary for this project.

## Generate all results and the report

```sh
python main.py --all --report
```

This regenerates three material sweeps, CSV result tables, six charts (each
available as PNG and vector PDF), a Markdown/PDF report, a manifest and actual
test output. It runs the tests before producing the report. The shipped outputs
already contain a completed default run, so you can inspect them immediately.

Other useful commands:

```sh
python main.py --list-cases
python main.py --case stiff_inclusions --vf 0.05 --vm 0.95
python main.py --compare --case moderate_contrast
python main.py --all --vf-max 1 --points 101
python main.py --case stiff_inclusions --vf 0.05 --xi 3
python -m unittest discover -s tests -v
```

`--vf` and `--vm` apply to single runs. For sweeps use `--vf-max`. The default
sweep is 0 to 0.6. Phase endpoints are mathematical checks, not evidence of
physical accuracy at high inclusion content. Key fractions are added to the
requested plot grid automatically. `--output PATH` changes the result folder.
Relative paths supplied at the command line are relative to your terminal's
working directory; built-in defaults resolve relative to the project itself.

VS Code's Run and Debug menu includes **Run one material case** and
**Generate all results and report** configurations. Run `main.py`, not a model
file directly. The model files use package imports.

## Folder structure

```text
composite_modulus/
├── main.py
├── requirements.txt
├── requirements-tested.txt       # Versions used to generate shipped results
├── README.md
├── .gitignore
├── .vscode/
│   ├── launch.json
│   └── settings.json
├── data/
│   └── materials.json
├── models/
│   ├── __init__.py
│   ├── _common.py                # Compatibility imports from utilities
│   ├── rule_of_mixtures.py
│   ├── eshelby.py
│   ├── mori_tanaka.py
│   ├── self_consistent.py
│   ├── hashin_shtrikman.py
│   ├── halpin_tsai.py
│   └── README.md
├── utilities/
│   ├── __init__.py
│   ├── input_checks.py
│   ├── elastic_properties.py
│   ├── tensor_operations.py
│   └── materials.py
├── analysis/
│   ├── __init__.py
│   ├── compare_models.py
│   └── plotting.py
├── tests/
│   ├── __init__.py
│   ├── test_limits.py
│   ├── test_benchmarks.py
│   └── test_project.py
├── report/
│   ├── __init__.py
│   ├── build_report.py
│   ├── theory.md
│   ├── background_and_viva.md
│   ├── references.md
│   └── discussion.md              # Generated from actual results
└── outputs/
    ├── figures/                  # PNG and vector PDF graphs
    ├── tables/                   # CSV: all cases and key fractions
    ├── report/                   # Generated Markdown and PDF report
    ├── run_manifest.json
    ├── verification.json
    └── verification.txt
```

The compatibility `_common.py` preserves the previously delivered model
interfaces; shared calculations now live in `utilities`. Keep these folders
together. This replaces the earlier standalone-models archive as the complete
project distribution.

## Streamlit website

The web interface calls the same analytical functions as `main.py`.

```sh
python -m pip install -r requirements.txt
streamlit run app.py
```

Select an illustrative material or custom inputs in the sidebar, enter phase
properties and Vf, select method families, then click Calculate. Vm is 1-Vf.
The unit selector converts preset moduli to the chosen unit; any edited values
must also use that unit. Compare-fraction charts keep the isotropic models,
low-fraction dilute calculation and scalar HT demonstration in separate views.
Downloads include the selected rows, sweep, input snapshot, chart and example
PDF study material. Visitor results are generated in memory and are not written
to shared project files. No external API key or database is required.

For Streamlit Community Cloud, select this repository's `main` branch and
`app.py` as the entry point, with Python 3.12. Dependencies are listed in
`requirements.txt`; theme/server settings are in `.streamlit/config.toml`.
Keep `.streamlit/secrets.toml` untracked if secrets are ever added. This
repository and the deployed app are public, as authorized by the owner.

Generated `outputs/` are intentionally not tracked on GitHub. Run the existing
command-line workflow to regenerate them after a clone. The original local
download includes precomputed results, and `docs/` contains fixed example PDFs.
The original study guide explains the analytical core before the web additions.

CI runs the model suite and Streamlit AppTest checks. Web tests cover the
reference output, changed fractions, missing dilute values, invalid input,
unit conversion, selected methods and CSV export. Run all checks with:

```sh
python -m unittest discover -s tests -v
```

## Enter your actual material data

Edit `data/materials.json`, or copy it and pass `--data your_file.json`.
Every case must supply these fields:

| Field | Meaning |
|---|---|
| id | Unique filename-safe identifier |
| name | Descriptive label |
| Ef, Em | Positive phase Young's moduli in the file's common unit |
| nu_f, nu_m | Phase Poisson ratios, strictly between -1 and 0.5 |
| xi | Explicit nonnegative Halpin-Tsai demonstration/calibration parameter |
| geometry | Must be `spherical` for this implementation |
| source_status | Honest description, e.g. illustrative or literature |
| source_note | Actual data source and any modeling assumptions |

The file has schema_version=1, unit (Pa, MPa or GPa), and a materials list.
The three shipped cases are hypothetical stiffness-contrast studies. They are
**not measured glass/epoxy, natural-fiber or other named material datasets**.
Neither fiber names nor property sources are invented.

```sh
python main.py --data data/materials.json --case stiff_inclusions --compare
```

For a real natural fiber, one scalar E and nu may be an insufficient material
description. Decide whether an isotropic idealization is appropriate before
entering such data; the program does not turn fibers into spheres physically.

## Reading the results

- The main plot compares 3-D isotropic Voigt/Reuss bounds, HS bounds,
  Mori-Tanaka and self-consistent predictions under a consistent spherical case.
- A separate plot compares low-fraction dilute results and separately shows
  the simple E mixtures and an uncalibrated Halpin-Tsai parameter demonstration.
- Dilute rows above Vf=0.1 are blank and marked `not_evaluated`; this cutoff
  is educational, not a universal validity threshold.
- Cross-ordered phase K/G produces explicit `not_applicable` HS rows. It does
  not stop valid calculations of the other models.
- CSV files retain E, nu, K, G, status, assumptions, units and solver diagnostics.
  Blank cells mean unavailable, not zero.
- The run manifest stores the actual inputs and configured comparison scope.
- The scalar arithmetic E mixture is not the general 3-D Voigt upper E bound
  when constituent Poisson ratios differ.
- MT and the appropriate HS boundary can coincide. That is expected for these
  ordered isotropic spherical cases.

## Verification and report use

The included suite checks endpoints, identical phases, conversions, tensor
conventions, independent scalar formulas, an exact rational fixture, 120
seeded material cases, self-consistent residuals, phase exchange, unit scaling,
applicable bounds, input validation, CSV export and command-line behavior.
See the shipped verification log for the actual result, not an assumed pass.

The report contains the objective, equations, assumptions, numerical results,
discussion, composite classifications, woven examples and references. Add your
own institution's cover details only if required. The viva guide explains
the choices you should understand before presenting the work.

**Remaining scientific scope:** real biocomposite data and experimental
validation are not supplied. Cylindrical/anisotropic fibers and woven
architecture need additional models; FEM was deliberately outside this stage.
Discuss that scope with your professor before presenting this as a prediction
of a specific woven or natural-fiber specimen.

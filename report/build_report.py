"""Build a readable report from actual rows; verify the code before reporting."""
import html
import json
from pathlib import Path
import re
import subprocess
import sys


def _value(rows, model, vf, key="E"):
    match = next((r for r in rows if r["model"] == model and abs(r["Vf"]-vf) < 1e-10), None)
    return match[key] if match is not None and match[key] != "" else None


def verify_project(root, output):
    """Record the real test output; a failing suite blocks report creation."""
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=root, capture_output=True, text=True,
    )
    text = result.stdout + result.stderr
    (output / "verification.txt").write_text(text, encoding="utf-8")
    count = re.search(r"Ran (\d+) tests", text)
    metadata = {"passed": result.returncode == 0,
                "test_methods": int(count.group(1)) if count else None,
                "seeded_material_cases": 120,
                "validation_type": "implementation verification; no experimental validation"}
    (output / "verification.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    if result.returncode:
        raise RuntimeError(f"Project tests failed. See {output / 'verification.txt'}")
    return metadata


def _discussion(materials, all_rows):
    lines = ["# Results and discussion", "",
             "All shipped cases use hypothetical inputs. These results demonstrate the models; "
             "they are not measurements or validated predictions of a real biocomposite.", ""]
    for material in materials:
        rows = [r for r in all_rows if r["case"] == material.id]
        lines += [f"## {material.name}", "", material.source_note, "",
                  f"Ef={material.Ef:g}, Em={material.Em:g} {material.unit}; "
                  f"nu_f={material.nu_f:g}, nu_m={material.nu_m:g}.", "",
                  f"| Vf | Mori-Tanaka ({material.unit}) | Self-consistent | HS lower | HS upper |",
                  "|---|---|---|---|---|"]
        fractions = sorted(set(r["Vf"] for r in rows if any(abs(r["Vf"]-v)<1e-10 for v in [.05,.1,.3,.5,.6,1])))
        for vf in fractions:
            values = [_value(rows, model, vf) for model in ["mori_tanaka","self_consistent","hs_lower","hs_upper"]]
            line = " | ".join("N/A" if v is None else f"{v:.6f}" for v in values)
            lines.append(f"| {vf:g} | {line} |")
        mt0, mt1 = _value(rows,"mori_tanaka",0), _value(rows,"mori_tanaka",max(r["Vf"] for r in rows))
        change = (mt1/mt0-1)*100
        lines += ["", f"Across the computed sweep, Mori-Tanaka E changes from {mt0:.6f} "
                  f"to {mt1:.6f} {material.unit} ({change:+.2f}%). "
                  "The trend reflects the assumed phase contrast and geometry.", "",
                  f"![Isotropic comparison](../figures/{material.id}_isotropic_comparison.png)", "",
                  f"![Separate demonstrations](../figures/{material.id}_model_demonstrations.png)", ""]
    lines += ["## Interpretation and limitations", "",
              "For the well-ordered isotropic sphere cases, Mori-Tanaka follows the HS boundary "
              "associated with the matrix phase. This overlap is expected. Self-consistent "
              "uses a different surrounding medium, so differing predictions are not a solver error.", "",
              "The dilute model is displayed only through Vf=0.1, an educational display cutoff "
              "rather than a universal validity threshold. Halpin-Tsai is kept as a separate "
              "uncalibrated parameter demonstration. No curve is ranked as experimentally most accurate.", "",
              "A real biocomposite or woven-material conclusion requires sourced inputs, an "
              "appropriate geometry/anisotropy model and validation data. These are not supplied "
              "by the professor's handwritten outline alone.", ""]
    return "\n".join(lines)


def build_report(materials, all_rows, output, root):
    output, root = Path(output), Path(root)
    verification = verify_project(root, output)
    directory = output / "report"
    directory.mkdir(parents=True, exist_ok=True)
    discussion = _discussion(materials, all_rows)
    (directory / "discussion.md").write_text(discussion, encoding="utf-8")
    # Keep the originally planned report source folder complete as well.
    (root / "report/discussion.md").write_text(discussion, encoding="utf-8")
    sections = [(root / "report" / name).read_text(encoding="utf-8")
                for name in ["theory.md", "background_and_viva.md", "references.md"]]
    combined = "\n\n---\n\n".join([sections[0], discussion, sections[1], sections[2]])
    combined += f"\n\n## Verification run\n\n{verification['test_methods']} test methods passed, "
    combined += "including 120 seeded material cases. Full output: ../verification.txt.\n"
    markdown = directory / "project_report.md"
    markdown.write_text(combined, encoding="utf-8")
    pdf = directory / "project_report.pdf"
    _write_pdf(pdf, materials, all_rows, output, verification)
    return [markdown, pdf]


def _write_pdf(path, materials, all_rows, output, verification):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
    )

    navy, teal = colors.HexColor("#153B57"), colors.HexColor("#087F8C")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("TitleCustom", fontName="Helvetica-Bold", fontSize=29,
                              leading=33, textColor=navy, spaceAfter=20))
    styles.add(ParagraphStyle("SectionCustom", fontName="Helvetica-Bold", fontSize=19,
                              leading=23, textColor=navy, spaceAfter=15))
    styles.add(ParagraphStyle("SubCustom", fontName="Helvetica-Bold", fontSize=12,
                              leading=16, textColor=teal, spaceBefore=10, spaceAfter=6))
    styles.add(ParagraphStyle("BodyCustom", fontName="Helvetica", fontSize=10.4,
                              leading=15.4, textColor=navy, spaceAfter=10))
    styles.add(ParagraphStyle("EquationCustom", fontName="Courier", fontSize=8.6,
                              leading=13, textColor=navy, backColor=colors.HexColor("#F1F5F8"),
                              borderPadding=8, spaceBefore=5, spaceAfter=15))
    styles.add(ParagraphStyle("SmallCustom", parent=styles["BodyCustom"], fontSize=8.8, leading=12))
    story = []
    width = A4[0] - 104

    def p(text, style="BodyCustom"):
        story.append(Paragraph(text, styles[style]))

    def h(text):
        p(text, "SubCustom")

    def eq(text):
        p(html.escape(text).replace("\n", "<br/>"), "EquationCustom")

    def page(title):
        if story:
            story.append(PageBreak())
        p(title, "SectionCustom")

    def table(data, widths=None):
        wrapped = [[Paragraph(html.escape(str(cell)), styles["SmallCustom"]) for cell in row]
                   for row in data]
        t = Table(wrapped, colWidths=widths, repeatRows=1, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DFEEF0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, 0), .6, teal),
            ("LINEBELOW", (0, 1), (-1, -1), .3, colors.HexColor("#DCE4EA")),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

    p("ANALYTICAL COMPOSITE MECHANICS", "SubCustom")
    story.append(Spacer(1, 26))
    p("Predicting effective<br/>Young's modulus", "TitleCustom")
    p("Six model families | Reproducible Python project", "SubCustom")
    story.append(Spacer(1, 20))
    p("<b>Objective.</b> Calculate effective elastic stiffness from constituent "
      "properties, volume fractions and explicitly stated geometry assumptions.")
    p("<b>Implemented scope.</b> Linear elastic, perfectly bonded, isotropic solid "
      "phases with spherical inclusions. The program includes simple mixture "
      "formulas, Eshelby/dilute, Mori-Tanaka, classical self-consistent, "
      "Hashin-Shtrikman bounds and a separate Halpin-Tsai parameter demonstration.")
    p("<b>Data status.</b> The shipped inputs are hypothetical teaching cases. "
      "This report demonstrates analytical behavior and implementation verification; "
      "it does not claim experimental accuracy or a measured biocomposite result.")
    table([["Delivered component", "Included"],
           ["Executable workflow", "Single cases, material-file inputs, fraction sweeps"],
           ["Results", "CSV tables, PNG/PDF graphs, run manifest"],
           ["Verification", f"{verification['test_methods']} tests; 120 seeded material cases"],
           ["Study material", "Theory, assumptions, classification, references and viva guide"]],
          [width*.32, width*.68])
    p("Woven architectures, real-fiber anisotropy and experimental validation "
      "remain extensions. Their background is discussed without claiming that "
      "the spherical model predicts those structures.", "SmallCustom")

    page("01 / Background and learning path")
    h("What is a composite?")
    p("A composite combines constituents with distinct roles. The matrix surrounds "
      "the reinforcement and transfers load through the interface. Young's modulus "
      "E describes elastic stiffness: it is not a prediction of failure strength.")
    table([["Classification", "Examples"],
           ["By matrix", "Polymer, metal, ceramic"],
           ["By reinforcement", "Particles, short fibers, continuous fibers"],
           ["By architecture", "Unidirectional, woven, random reinforcement, laminate"],
           ["Woven examples", "Plain, twill, satin, basket, warp rib, weft rib"]],
          [width*.30,width*.70])
    p("Natural fibers such as flax, jute and hemp motivate biocomposite research. "
      "A real natural-fiber case needs sourced properties and a defensible geometry "
      "and anisotropy model. The current data are not measurements of these fibers. [R7-R9]")
    h("Learning sequence")
    for text in ["1. Stress, strain and the meaning of elastic modulus.",
                 "2. Phase volume fractions, interfaces and loading direction.",
                 "3. Simple mixtures; then Poisson ratio, bulk and shear modulus.",
                 "4. Concentration tensors, Eshelby and mean-field assumptions.",
                 "5. Bounds, numerical residuals, plots and limits of validation."]:
        p(text)
    h("Why woven geometry matters")
    p("Warp/weft fractions, yarn directions, crimp and matrix pockets influence "
      "woven stiffness. These cannot be recovered from Ef, Em, Vf and Vm alone.")

    page("02 / Inputs, baselines and Eshelby")
    p("For a void-free two-phase system, Vf + Vm = 1. Use Vf=0.30 for 30%, "
      "not 30. Phase Poisson ratios are required by the three-dimensional models.")
    eq("K = E/[3(1-2 nu)]     G = E/[2(1+nu)]\nE = 9KG/(3K+G)       nu = (3K-2G)/[2(3K+G)]")
    h("Simple mixtures and proper isotropic bounds")
    eq("E_equal_strain = Vf Ef + Vm Em\nE_equal_stress = 1/(Vf/Ef + Vm/Em)")
    p("These scalar idealizations are displayed separately from the 3-D isotropic "
      "comparison. The latter averages K and G arithmetically for Voigt and "
      "harmonically for Reuss, then converts the pairs to E. [R1]")
    h("Spherical Eshelby and dilute stiffness")
    eq("A_dil = [I + S Cm^-1 (Cf-Cm)]^-1\nC_dil = Cm + Vf (Cf-Cm) A_dil")
    p("The actual spherical Eshelby tensor is implemented in orthonormal Kelvin "
      "notation, with square-root-of-two scaling of shear components. It is "
      "also available as a Cartesian fourth-order tensor. [R2]")
    p("Dilute theory ignores inclusion interactions. It appears only for Vf up "
      "to 0.1 in the comparison workflow. This chosen cutoff is a teaching "
      "restriction, not proof of accuracy. The Vf=1 dilute endpoint is rejected.")

    page("03 / Mean-field estimates and bounds")
    h("Mori-Tanaka: the matrix as host")
    eq("zeta_m = Gm(9Km+8Gm)/[6(Km+2Gm)]\nK_MT = Km + Vf(Kf-Km)/[1+Vm(Kf-Km)/(Km+4Gm/3)]\nG_MT = Gm + Vf(Gf-Gm)/[1+Vm(Gf-Gm)/(Gm+zeta_m)]")
    p("The tensor implementation normalizes the dilute concentration factors to "
      "satisfy the average-strain condition. Independent scalar reductions check "
      "that implementation. A connected matrix-inclusion topology is assumed. [R3]")
    h("Classical self-consistent: the composite as host")
    eq("sum_i Vi(Ki-K)/(Ki+4G/3) = 0\nsum_i Vi(Gi-G)/(Gi+zeta(K,G)) = 0")
    p("K is eliminated analytically at each trial G. Bisection in log(G) solves "
      "the remaining equation. Both dimensionless residuals must pass the "
      "tolerance check before a result is returned. This is not a finite element "
      "calculation or the generalized coated-sphere scheme. [R4]")
    h("Hashin-Shtrikman: a permissible range")
    p("Lower and upper K/G bounds are computed for well-ordered isotropic phases "
      "and converted to E. Phase ordering must hold in both K and G. Cross-ordered "
      "cases are explicitly marked unavailable in the tables. [R5]")
    p("For ordered isotropic spherical cases, Mori-Tanaka matches the HS boundary "
      "associated with its matrix phase. Coincident curves are expected, not a "
      "reason to change a model to make the plot look different.")

    page("04 / Halpin-Tsai and reproducible execution")
    h("A separate semi-empirical demonstration")
    eq("eta = (Ef/Em-1)/(Ef/Em+xi)\nE_HT = Em(1+xi eta Vf)/(1-eta Vf)")
    p("xi depends on geometry, loading and calibration. The shipped xi=2 is a "
      "parameter demonstration only. The associated plots are kept separate "
      "from the isotropic 3-D estimates. xi=0 recovers the simple Reuss E "
      "expression and supplies a useful limiting check. [R6]")
    h("Reproduce the entire analysis")
    eq("python -m pip install -r requirements.txt\npython main.py --all --report")
    p("The command creates per-case sweeps, key-fraction CSV tables, PNG/PDF "
      "graphs, a run manifest, actual test output and this report. The shipped "
      "sweep spans Vf=0 to 0.6; pure-phase endpoints are verified separately.")
    h("Use actual inputs")
    p("Edit or copy data/materials.json. Supply consistent units, Ef, Em, "
      "nu_f, nu_m, a case id, xi and source notes. Then run the selected case "
      "or comparison. Do not relabel an illustrative value as measured data.")
    eq("python main.py --case stiff_inclusions --vf 0.05\npython main.py --compare --case stiff_inclusions\npython main.py --data data/materials.json --list-cases")

    for index, material in enumerate(materials, 1):
        page(f"Results {index:02d} / {html.escape(material.id)}")
        p(html.escape(material.name), "SubCustom")
        p(f"Ef={material.Ef:g}, Em={material.Em:g} {material.unit}; "
          f"nu_f={material.nu_f:g}, nu_m={material.nu_m:g}. "
          f"Data status: {html.escape(material.source_status)}.", "SmallCustom")
        fig = output / "figures" / f"{material.id}_isotropic_comparison.png"
        from PIL import Image as PILImage
        with PILImage.open(fig) as im:
            ratio = im.height / im.width
        story.append(Image(str(fig), width=width, height=width*ratio))
        story.append(Spacer(1, 10))
        rows = [r for r in all_rows if r["case"] == material.id]
        grid = [["Vf", f"MT E ({material.unit})", "SC E", "HS lower E", "HS upper E"]]
        selected_vf = [v for v in [.05,.1,.3,.5,.6,1] if _value(rows,"mori_tanaka",v) is not None]
        for vf in selected_vf:
            values = [_value(rows,m,vf) for m in ["mori_tanaka","self_consistent","hs_lower","hs_upper"]]
            grid.append([f"{vf:g}"] + ["N/A" if v is None else f"{v:.4f}" for v in values])
        if len(grid)>1:
            table(grid, [width*.10] + [width*.225]*4)
        vmax = max(r["Vf"] for r in rows)
        initial, final = _value(rows,"mori_tanaka",0), _value(rows,"mori_tanaka",vmax)
        p(f"Over Vf=0 to {vmax:g}, Mori-Tanaka changes from {initial:.4f} "
          f"to {final:.4f} {material.unit}, a change of {(final/initial-1)*100:+.2f}%. "
          "This is a model trend for the stated inputs, not a measured improvement.")
        p(html.escape(material.source_note), "SmallCustom")

    page("05 / Low-fraction and parameter demonstrations")
    material = materials[0]
    p(f"Example shown: {html.escape(material.name)}. Equivalent figures for "
      "every other case are included in the outputs/figures folder.")
    fig = output / "figures" / f"{material.id}_model_demonstrations.png"
    from PIL import Image as PILImage
    with PILImage.open(fig) as im:
        ratio = im.height / im.width
    story.append(Image(str(fig), width=width, height=width*ratio))
    story.append(Spacer(1, 16))
    h("Read the panels differently")
    p("The left panel compares low-fraction isotropic estimates. Dilute and "
      "Mori-Tanaka approach one another in the dilute limit. The right panel "
      "illustrates scalar mixture and Halpin-Tsai behavior; it is not an "
      "equivalent spherical-model benchmark.")
    h("No accuracy ranking from agreement alone")
    p("A model falling between bounds is mechanically consistent with those "
      "bounds under the stated assumptions. That does not prove that it is the "
      "best prediction for a real specimen. Calibration and experimental "
      "validation are separate tasks.")

    page("06 / Verification, limitations and conclusion")
    p(f"The report was generated after the real test suite passed: "
      f"<b>{verification['test_methods']} test methods</b>, including a fixed "
      "120-case material sweep with independent checks. The full record is "
      "outputs/verification.txt; machine-readable status is verification.json.")
    table([["Check", "Purpose"],
           ["Phase endpoints and identical phases", "Recover known material limits"],
           ["Kelvin vs Cartesian tensor mapping", "Detect shear-scaling convention errors"],
           ["Rational fixture and scalar reductions", "Independently check tensor model calculations"],
           ["SC residuals, phase exchange and units", "Verify solver equations and invariances"],
           ["VR/HS ordering and MT overlap", "Check applicable theoretical constraints"],
           ["Input, CSV and CLI integration", "Check readable errors and reproducible output"]],
          [width*.43,width*.57])
    h("Limitations")
    p("No experiments, FEM, cylindrical fibers, woven architecture, real-fiber "
      "anisotropy, voids, damage, interface slip or environmental effects are "
      "modeled. All shipped numeric material cases are illustrative. Source "
      "data, geometry decisions and validation measurements are still required "
      "before making a real biocomposite claim.")
    h("Conclusion")
    p("The project provides a reproducible analytical framework for predicting "
      "and comparing effective isotropic stiffness under explicit assumptions. "
      "It distinguishes bounds, mean-field predictions and semi-empirical "
      "demonstrations and checks their mathematical consistency.")

    page("07 / References and next study steps")
    refs = [
        ("R1", "Echoes: Voigt/Reuss and homogenization schemes", "https://jfbarthelemy.github.io/echoes/99_appendices/scheme_derivations.html"),
        ("R2", "Eshelby (1957): original inclusion solution", "https://doi.org/10.1098/rspa.1957.0133"),
        ("R3", "Effective moduli: spherical concentration factors (2021)", "https://doi.org/10.1093/jge/gxab034"),
        ("R4", "NPTEL: Self Consistent Method", "https://archive.nptel.ac.in/content/storage2/courses/101104010/lecture34/34_2.htm"),
        ("R5", "RockPhyPy: independent HS bound formula reference", "https://rockphypy.readthedocs.io/en/latest/_modules/rockphypy/EM.html"),
        ("R6", "NPTEL: Halpin-Tsai relations", "https://archive.nptel.ac.in/content/storage2/courses/101104010/lecture34/34_4.htm"),
        ("R7", "NPTEL: Composite classification", "https://archive.nptel.ac.in/content/storage2/courses/101104010/lecture1/1_4.htm"),
        ("R8", "NPTEL: Reinforcement materials and forms", "https://archive.nptel.ac.in/content/storage2/courses/101104010/lecture2/2_3.htm"),
        ("R9", "NPTEL: Weave design", "https://archive.nptel.ac.in/content/storage2/courses/116102005/m5-design/l21-weave%20design.htm"),
    ]
    for number, label, url in refs:
        p(f'{number}. <link href="{html.escape(url, quote=True)}" color="#087F8C">'
          f'{html.escape(label)}</link>', "SmallCustom")
    h("Prepare for the project presentation")
    p("Explain E versus strength, why Poisson ratios are needed, the host-medium "
      "assumption of each scheme, why MT and HS may overlap, the dilute restriction "
      "and the need to justify xi. A longer question-and-answer guide is supplied "
      "in report/background_and_viva.md.")
    p("The references support theory and implementation checks. They are not "
      "sources for the hypothetical input numbers. No institutional format, "
      "student identity, experimental results or supervisor approval is invented.", "SmallCustom")

    def footer(canvas, doc):
        canvas.setStrokeColor(colors.HexColor("#DCE4EA"))
        canvas.line(52, 43, A4[0]-52, 43)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(navy)
        canvas.drawString(52, 29, "COMPOSITE MODULUS | Analytical study | Illustrative data")
        canvas.drawRightString(A4[0]-52, 29, str(doc.page))

    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=52, rightMargin=52,
                            topMargin=49, bottomMargin=57,
                            title="Analytical prediction of effective composite modulus",
                            author="Composite Modulus Project")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)

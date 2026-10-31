"""Run a single case, export comparisons, or generate the project report."""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys

from analysis.compare_models import evaluate, export_csv, key_rows, sweep
from utilities.input_checks import fractions
from utilities.materials import load_materials

ROOT = Path(__file__).resolve().parent


def parser():
    p = argparse.ArgumentParser(description="Analytical modulus prediction for idealized isotropic composites.")
    p.add_argument("--data", type=Path, default=ROOT / "data/materials.json", help="Material JSON file.")
    p.add_argument("--case", default="stiff_inclusions", help="Case id from the material file.")
    p.add_argument("--list-cases", action="store_true", help="Show available inputs and their provenance.")
    p.add_argument("--vf", type=float, default=.05, help="Single-run inclusion volume fraction, default 0.05.")
    p.add_argument("--vm", type=float, help="Optional single-run matrix fraction; must equal 1-vf.")
    p.add_argument("--xi", type=float, help="Override the Halpin-Tsai demonstration parameter.")
    p.add_argument("--compare", action="store_true", help="Sweep the selected material case.")
    p.add_argument("--all", action="store_true", help="Sweep every material case.")
    p.add_argument("--vf-max", type=float, default=.6, help="Sweep maximum, default 0.6; must be in (0,1].")
    p.add_argument("--points", type=int, default=61, help="Sweep grid size, default 61; key fractions also included.")
    p.add_argument("--report", action="store_true", help="Generate comparisons plus Markdown and PDF report.")
    p.add_argument("--output", type=Path, default=ROOT / "outputs", help="Output directory.")
    return p


def run(argv=None):
    p = parser()
    args = p.parse_args(argv)
    try:
        cases = load_materials(args.data)
        if args.list_cases:
            for m in cases.values():
                print(f"{m.id}: {m.name}\n  Ef={m.Ef:g}, Em={m.Em:g} {m.unit}; "
                      f"nu_f={m.nu_f:g}, nu_m={m.nu_m:g}\n  {m.source_status}: {m.source_note}")
            return 0
        if not args.all and args.case not in cases:
            raise ValueError(f"Unknown case '{args.case}'. Choose: {', '.join(cases)}")
        selected = list(cases.values()) if args.all else [cases[args.case]]
        if args.xi is not None:
            # Revalidate the override through the same schema checks.
            selected = [replace(m, xi=args.xi) for m in selected]
            from models import halpin_tsai
            for m in selected:
                halpin_tsai(m.Ef, m.Em, 0, xi=m.xi)
        out = args.output.resolve()
        out.mkdir(parents=True, exist_ok=True)
        if args.compare or args.all or args.report:
            if args.vm is not None or args.vf != .05:
                raise ValueError("--vf/--vm apply to single runs; use --vf-max for a comparison sweep.")
            from analysis.plotting import plot_case
            all_rows, generated = [], []
            for material in selected:
                rows = sweep(material, vf_max=args.vf_max, points=args.points)
                all_rows.extend(rows)
                export_csv(rows, out / "tables" / f"{material.id}_all_results.csv")
                export_csv(key_rows(rows), out / "tables" / f"{material.id}_key_fractions.csv")
                generated += [str(p.relative_to(out)) for p in plot_case(material, rows, out / "figures")]
                print(f"Completed {material.id}: {len(rows)//10} fractions, tables and figures.")
            export_csv(all_rows, out / "tables/all_cases_results.csv")
            manifest = {
                "project": "Analytical composite modulus", "geometry": "spherical",
                "data_file": str(args.data.resolve()), "materials": [m.to_dict() for m in selected],
                "vf_max": args.vf_max, "requested_grid_points": args.points,
                "dilute_display_cutoff": .1, "experimental_validation": False,
                "halpin_tsai_role": "separate uncalibrated parameter demonstration",
                "figures": generated,
            }
            (out / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            if args.report:
                from report.build_report import build_report
                report_files = build_report(selected, all_rows, out, ROOT)
                for path in report_files:
                    print(f"Report: {path}")
            print(f"Results saved to: {out}")
        else:
            Vf, _ = fractions(args.vf, args.vm)
            material = selected[0]
            rows = evaluate(material, Vf)
            print(f"\n{material.name}\nInputs: Ef={material.Ef:g}, Em={material.Em:g} {material.unit}, "
                  f"nu_f={material.nu_f:g}, nu_m={material.nu_m:g}, Vf={Vf:g}, Vm={1-Vf:g}")
            print(f"Data status: {material.source_status}\n{material.source_note}\n")
            print(f"{'Method':<24} {'E ('+material.unit+')':>13}  Status")
            for row in rows:
                value = f"{row['E']:.6f}" if row["E"] != "" else "--"
                print(f"{row['model']:<24} {value:>13}  {row['status']}")
            export_csv(rows, out / "tables" / f"{material.id}_single.csv")
            payload = {"material": material.to_dict(), "Vf": Vf, "results": rows}
            (out / f"{material.id}_single.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
            print("\nDilute appears only for Vf<=0.1. HT is a separate parameter demonstration.")
        return 0
    except (ValueError, OSError, RuntimeError, ImportError) as exc:
        p.exit(2, f"Error: {exc}\n")


if __name__ == "__main__":
    sys.exit(run())

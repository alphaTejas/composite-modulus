"""Load documented isotropic material cases from JSON."""
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re

from .input_checks import finite_scalar, positive, poisson


@dataclass(frozen=True)
class Material:
    id: str
    name: str
    Ef: float
    Em: float
    nu_f: float
    nu_m: float
    xi: float
    source_status: str
    source_note: str
    geometry: str = "spherical"
    unit: str = "GPa"

    @classmethod
    def from_dict(cls, raw, unit="GPa"):
        if not isinstance(raw, dict):
            raise ValueError("Each material case must be a JSON object.")
        required = {"id", "name", "Ef", "Em", "nu_f", "nu_m", "xi", "source_status", "source_note"}
        missing = sorted(required - raw.keys())
        unknown = sorted(raw.keys() - required - {"geometry"})
        if missing or unknown:
            raise ValueError(f"Material fields: missing={missing}, unknown={unknown}")
        for key in ["id", "name", "source_status", "source_note"]:
            if not isinstance(raw[key], str) or not raw[key].strip():
                raise ValueError(f"{key} must be a nonempty string.")
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", raw["id"]):
            raise ValueError("Material id may contain only letters, numbers, _ and -.")
        if raw.get("geometry", "spherical") != "spherical":
            raise ValueError("Only spherical isotropic inclusion cases are implemented.")
        if unit not in {"Pa", "MPa", "GPa"}:
            raise ValueError("unit must be Pa, MPa or GPa; every modulus must use it.")
        xi = finite_scalar(raw["xi"], "xi")
        if xi < 0:
            raise ValueError("xi must be nonnegative.")
        return cls(
            id=raw["id"], name=raw["name"],
            Ef=positive(raw["Ef"], "Ef"), Em=positive(raw["Em"], "Em"),
            nu_f=poisson(raw["nu_f"], "nu_f"), nu_m=poisson(raw["nu_m"], "nu_m"),
            xi=xi, source_status=raw["source_status"], source_note=raw["source_note"],
            geometry="spherical", unit=unit,
        )

    def inputs(self, Vf):
        return dict(Ef=self.Ef, Em=self.Em, Vf=Vf, nu_f=self.nu_f, nu_m=self.nu_m)

    def to_dict(self):
        return asdict(self)


def load_materials(path):
    with Path(path).open(encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Material data must be an object with schema_version=1.")
    if set(data) != {"schema_version", "unit", "materials"}:
        raise ValueError("Material file must contain schema_version, unit and materials only.")
    if not isinstance(data["materials"], list) or not data["materials"]:
        raise ValueError("materials must be a nonempty list.")
    result = {}
    for raw in data["materials"]:
        material = Material.from_dict(raw, data["unit"])
        if material.id in result:
            raise ValueError(f"Duplicate material id: {material.id}")
        result[material.id] = material
    return result

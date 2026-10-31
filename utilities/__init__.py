"""Shared material, validation and tensor tools."""
from .elastic_properties import to_bulk_shear, from_bulk_shear

__all__ = ["to_bulk_shear", "from_bulk_shear"]

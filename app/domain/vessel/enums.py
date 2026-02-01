from __future__ import annotations

from enum import Enum, IntEnum


class VesselType(str, Enum):
    """
    Mareon domain vessel types (generalized categories).
    Keep this small + product-facing.
    """
    CARGO = "CARGO"
    TANKER = "TANKER"
    PASSENGER = "PASSENGER"
    FISHING = "FISHING"

    TUG_TOW = "TUG_TOW"
    SERVICE = "SERVICE"          # pilot, SAR, law enforcement, port tender, etc.
    MILITARY = "MILITARY"
    SAILING = "SAILING"
    PLEASURE = "PLEASURE"
    HIGH_SPEED = "HIGH_SPEED"    # HSC
    WIG = "WIG"                  # wing-in-ground

    OTHER = "OTHER"
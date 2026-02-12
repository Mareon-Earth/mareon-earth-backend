from __future__ import annotations

from enum import Enum


class VesselType(str, Enum):
    CARGO       = "CARGO",      # Bulk carriers, container ships, general cargo, ro-ro
    TANKER      = "TANKER",     # Oil, chemical, gas, LNG, LPG, product tankers
    PASSENGER   = "PASSENGER",  # Passenger ships, cruise, ferries
    FISHING     = "FISHING",    # Trawlers, fishing vessels
    TUG_TOW     = "TUG_TOW",    # Tugs, tugboats, towing vessels
    SERVICE     = "SERVICE",    # PSV, OSV, AHTS, supply, icebreaker, research, dredger, cable layer, rescue, patrol
    MILITAR     = "MILITARY",   # Navy, coast guard, warships
    SAILING     = "SAILING",    # Sailing vessels
    PLEASUR     = "PLEASURE",   # Yachts, pleasure craft
    HIGH_SP     = "HIGH_SPEED", # High speed craft (HSC)
    WIG         = "WIG",        # Wing-in-ground effect craft
    OTHER       = "OTHER",      # Unknown or unlisted types

class CertificateDomain(str, Enum):
    CLASS       = "CLASS"
    STATUTORY       = "STATUTORY"
    MANAGEMENT      = "MANAGEMENT"
    SECURITY        = "SECURITY"
    LABOUR          = "LABOUR"
    OTHER           = "OTHER"


class CertificateStatus(Enum):
    VALID = "VALID"
    EXPIRED = "EXPIRED"
    EXPIRING_SOON = "EXPIRING_SOON"
    WITHDRAWN = "WITHDRAWN"
    UNKNOWN = "UNKNOWN"


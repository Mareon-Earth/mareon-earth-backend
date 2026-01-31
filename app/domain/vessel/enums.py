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


class AisShipType(IntEnum):
    """
    AIS ship type codes (Message 5 / static data) commonly represented as 2 digits.
    Source tables are consistent across common references. :contentReference[oaicite:2]{index=2}
    """

    NOT_AVAILABLE = 0

    # 1-19 reserved
    RESERVED_01 = 1
    RESERVED_02 = 2
    RESERVED_03 = 3
    RESERVED_04 = 4
    RESERVED_05 = 5
    RESERVED_06 = 6
    RESERVED_07 = 7
    RESERVED_08 = 8
    RESERVED_09 = 9
    RESERVED_10 = 10
    RESERVED_11 = 11
    RESERVED_12 = 12
    RESERVED_13 = 13
    RESERVED_14 = 14
    RESERVED_15 = 15
    RESERVED_16 = 16
    RESERVED_17 = 17
    RESERVED_18 = 18
    RESERVED_19 = 19

    # 20-29 WIG
    WIG_ALL = 20
    WIG_HAZ_A = 21
    WIG_HAZ_B = 22
    WIG_HAZ_C = 23
    WIG_HAZ_D = 24
    WIG_RESERVED_25 = 25
    WIG_RESERVED_26 = 26
    WIG_RESERVED_27 = 27
    WIG_RESERVED_28 = 28
    WIG_RESERVED_29 = 29

    # 30-39 special
    FISHING = 30
    TOWING = 31
    TOWING_LARGE = 32
    DREDGING_UNDERWATER_OPS = 33
    DIVING_OPS = 34
    MILITARY_OPS = 35
    SAILING = 36
    PLEASURE_CRAFT = 37
    RESERVED_38 = 38
    RESERVED_39 = 39

    # 40-49 HSC
    HSC_ALL = 40
    HSC_HAZ_A = 41
    HSC_HAZ_B = 42
    HSC_HAZ_C = 43
    HSC_HAZ_D = 44
    HSC_RESERVED_45 = 45
    HSC_RESERVED_46 = 46
    HSC_RESERVED_47 = 47
    HSC_RESERVED_48 = 48
    HSC_NO_ADDITIONAL_INFO = 49

    # 50-59 official/special craft
    PILOT_VESSEL = 50
    SEARCH_AND_RESCUE = 51
    TUG = 52
    PORT_TENDER = 53
    ANTI_POLLUTION = 54
    LAW_ENFORCEMENT = 55
    LOCAL_VESSEL_56 = 56
    LOCAL_VESSEL_57 = 57
    MEDICAL_TRANSPORT = 58
    NONCOMBATANT = 59

    # 60-69 passenger
    PASSENGER_ALL = 60
    PASSENGER_HAZ_A = 61
    PASSENGER_HAZ_B = 62
    PASSENGER_HAZ_C = 63
    PASSENGER_HAZ_D = 64
    PASSENGER_RESERVED_65 = 65
    PASSENGER_RESERVED_66 = 66
    PASSENGER_RESERVED_67 = 67
    PASSENGER_RESERVED_68 = 68
    PASSENGER_NO_ADDITIONAL_INFO = 69

    # 70-79 cargo
    CARGO_ALL = 70
    CARGO_HAZ_A = 71
    CARGO_HAZ_B = 72
    CARGO_HAZ_C = 73
    CARGO_HAZ_D = 74
    CARGO_RESERVED_75 = 75
    CARGO_RESERVED_76 = 76
    CARGO_RESERVED_77 = 77
    CARGO_RESERVED_78 = 78
    CARGO_NO_ADDITIONAL_INFO = 79

    # 80-89 tanker
    TANKER_ALL = 80
    TANKER_HAZ_A = 81
    TANKER_HAZ_B = 82
    TANKER_HAZ_C = 83
    TANKER_HAZ_D = 84
    TANKER_RESERVED_85 = 85
    TANKER_RESERVED_86 = 86
    TANKER_RESERVED_87 = 87
    TANKER_RESERVED_88 = 88
    TANKER_NO_ADDITIONAL_INFO = 89

    # 90-99 other
    OTHER_ALL = 90
    OTHER_HAZ_A = 91
    OTHER_HAZ_B = 92
    OTHER_HAZ_C = 93
    OTHER_HAZ_D = 94
    OTHER_RESERVED_95 = 95
    OTHER_RESERVED_96 = 96
    OTHER_RESERVED_97 = 97
    OTHER_RESERVED_98 = 98
    OTHER_NO_ADDITIONAL_INFO = 99


def vessel_type_from_ais(ship_type: int | AisShipType | None) -> VesselType:
    """
    Generalizes AIS ship type codes into Mareon VesselType buckets.
    This mirrors common aggregation patterns (cargo/passenger/tanker/tug...). :contentReference[oaicite:3]{index=3}
    """
    if ship_type is None:
        return VesselType.OTHER

    code = int(ship_type)

    if 70 <= code <= 79:
        return VesselType.CARGO
    if 80 <= code <= 89:
        return VesselType.TANKER
    if 60 <= code <= 69:
        return VesselType.PASSENGER
    if code == 30:
        return VesselType.FISHING
    if code in (31, 32, 52):
        return VesselType.TUG_TOW
    if code == 35:
        return VesselType.MILITARY
    if code == 36:
        return VesselType.SAILING
    if code == 37:
        return VesselType.PLEASURE
    if 40 <= code <= 49:
        return VesselType.HIGH_SPEED
    if 20 <= code <= 29:
        return VesselType.WIG
    if 50 <= code <= 59 or code in (33, 34):
        return VesselType.SERVICE

    return VesselType.OTHER

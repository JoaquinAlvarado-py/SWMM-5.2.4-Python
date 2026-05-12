from enum import Enum
from core.project_base import Section


class InletType(Enum):
    """Type of street inlet design"""
    GRATE = 0
    CURB = 1
    COMBO = 2
    SLOTTED = 3
    DROP_GRATE = 4
    DROP_CURB = 5
    CUSTOM = 6


class GrateType(Enum):
    """Predefined grate inlet types"""
    P_BAR_50 = 0
    P_BAR_50x100 = 1
    P_BAR_30 = 2
    CURVED_VANE = 3
    TILT_BAR_45 = 4
    TILT_BAR_30 = 5
    RETICULINE = 6
    GENERIC = 7


# String representations used in INP files
GRATE_TYPE_NAMES = [
    "P_BAR-50", "P_BAR-50x100", "P_BAR-30", "CURVED_VANE",
    "TILT_BAR-45", "TILT_BAR-30", "RETICULINE", "GENERIC"
]

# Keywords used in INP file for inlet types
INLET_TYPE_KEYWORDS = {
    InletType.GRATE: "GRATE",
    InletType.CURB: "CURB",
    InletType.SLOTTED: "SLOTTED",
    InletType.DROP_GRATE: "DROP_GRATE",
    InletType.DROP_CURB: "DROP_CURB",
    InletType.CUSTOM: "CUSTOM",
}

# Reverse mapping from keyword to InletType
KEYWORD_TO_INLET_TYPE = {v: k for k, v in INLET_TYPE_KEYWORDS.items()}


class ThroatType(Enum):
    """Curb inlet throat angle"""
    VERTICAL = 0
    INCLINED = 1
    HORIZONTAL = 2


THROAT_TYPE_NAMES = ["VERTICAL", "INCLINED", "HORIZONTAL"]


class InletPlacement(Enum):
    """Inlet placement on the street"""
    AUTOMATIC = 0
    ON_GRADE = 1
    ON_SAG = 2


PLACEMENT_NAMES = ["AUTOMATIC", "ON_GRADE", "ON_SAG"]


class Inlet(Section):
    """Defines the design of a drainage inlet that can be placed in street/channel conduits."""

    def __init__(self):
        Section.__init__(self)

        ## Inlet design name/ID
        self.name = "Unnamed"

        ## Type of inlet
        self.inlet_type = InletType.GRATE

        # -- Grate properties (used by GRATE, COMBO, DROP_GRATE) --

        ## Grate type name (one of GRATE_TYPE_NAMES)
        self.grate_type = "P_BAR-50"

        ## Length of grate inlet (ft or m)
        self.grate_length = "2"

        ## Width of grate inlet (ft or m)
        self.grate_width = "2"

        ## Fraction of grate that is open (only for GENERIC grate type)
        self.grate_open_fraction = "0.8"

        ## Splash-over velocity (ft/s or m/s, only for GENERIC grate type)
        self.grate_splash_velocity = "0"

        # -- Curb opening properties (used by CURB, COMBO, DROP_CURB) --

        ## Length of curb opening (ft or m)
        self.curb_length = "2"

        ## Height of curb opening (ft or m)
        self.curb_height = "0.5"

        ## Throat angle type (one of THROAT_TYPE_NAMES)
        self.curb_throat = "VERTICAL"

        # -- Slotted drain properties (used by SLOTTED) --

        ## Length of slotted drain (ft or m)
        self.slotted_length = "4"

        ## Width of slotted drain (ft or m)
        self.slotted_width = "0.5"

        # -- Custom inlet properties (used by CUSTOM) --

        ## Name of diversion curve for custom inlet
        self.custom_curve = ""


class InletUsage(Section):
    """Assigns an inlet design to a specific conduit link for capturing street/channel flow."""

    def __init__(self):
        Section.__init__(self)

        ## Name of conduit where inlet is placed
        self.conduit_id = ""

        ## Name of the inlet design being used
        self.inlet_id = ""

        ## Name of the node receiving captured flow
        self.capture_node_id = ""

        ## Number of inlets placed on each side of street
        self.number_inlets = "1"

        ## Percent of inlet area that is clogged (0-100)
        self.percent_clogged = "0"

        ## Maximum flow captured per inlet (0 = unlimited, flow units)
        self.flow_restriction = "0"

        ## Local gutter depression height (ft or m)
        self.depress_height = "0"

        ## Local gutter depression width (ft or m)
        self.depress_width = "0"

        ## Inlet placement: AUTOMATIC, ON_GRADE, or ON_SAG
        self.placement = "AUTOMATIC"

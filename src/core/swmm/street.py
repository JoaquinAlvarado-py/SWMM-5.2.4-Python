from enum import Enum
from core.project_base import Section


class Street(Section):
    """Defines a street cross-section geometry for conduits.
       Used with STREET-shaped conduits for street flow and inlet capture modeling."""

    def __init__(self):
        Section.__init__(self)

        ## Street section name/ID
        self.name = "Unnamed"

        ## Width of street cross-section from curb to crown (ft or m)
        self.tcrown = "30"

        ## Height of curb (ft or m)
        self.hcurb = "0.5"

        ## Street cross slope (%)
        self.sx = "2"

        ## Manning's n of road surface
        self.nroad = "0.016"

        ## Gutter depression height (ft or m)
        self.a_depression = "0"

        ## Gutter width (ft or m)
        self.w_gutter = "0"

        ## Number of sides (1 or 2)
        self.sides = "2"

        ## Width of backing/sidewalk area (ft or m)
        self.tback = "0"

        ## Backing slope (%)
        self.sback = "0"

        ## Manning's n of backing
        self.nback = "0"

    @property
    def max_depth(self):
        """Calculate the maximum depth of the street cross-section."""
        try:
            ydep = float(self.a_depression)
            ycurb = float(self.hcurb)
            wcrown = float(self.tcrown)
            scross = float(self.sx)
            wback = float(self.tback)
            sback_val = float(self.sback)
            d1 = ydep + ycurb + wback * sback_val / 100.0
            d2 = ydep + wcrown * scross / 100.0
            return max(d1, d2)
        except (ValueError, ZeroDivisionError):
            return 0.0

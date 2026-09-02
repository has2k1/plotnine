from __future__ import annotations

from ..doctools import document
from ..mapping.evaluation import after_stat
from .contours import contour_bands
from .stat_contour import stat_contour


@document
class stat_contour_filled(stat_contour):
    """
    Filled contour bands for a gridded surface

    {usage}

    The `x` and `y` values must form a grid with one `z` value per
    coordinate. When `z` is missing, cells that touch it are not contoured.

    Parameters
    ----------
    {common_parameters}
    bins :
        Number of contour bands. Takes precedence over `binwidth`.
    binwidth :
        Distance between adjacent contour values.
    breaks :
        Explicit contour values, or a function that receives the `z` range
        and distance between contours. Explicit values override `bins` and
        `binwidth`. A function uses the distance selected by `bins` or
        `binwidth`. By default, values are selected for ten bands.

    See Also
    --------
    plotnine.geom_contour_filled : The default `geom` for this `stat`.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "level"       # band, an ordered interval such as "(0.005, 0.01]"
    "level_low"   # lower bound of the band
    "level_high"  # upper bound of the band
    "level_mid"   # midpoint between the bounds
    "nlevel"      # upper bound, scaled to a maximum of 1
    "piece"       # numeric id of a band in a given group
    ```
    """
    DEFAULT_AES = {"fill": after_stat("level")}
    DEFAULT_PARAMS = {"geom": "contour_filled"}
    CREATES = {
        "level",
        "level_low",
        "level_high",
        "level_mid",
        "nlevel",
        "piece",
        "subgroup",
    }

    def compute_contours(self, x, y, Z, breaks, group):
        """
        Trace each band between neighbouring breaks on an axis-aligned grid
        """
        return contour_bands(x, y, Z, breaks, group)

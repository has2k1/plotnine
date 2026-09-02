from __future__ import annotations

from ..doctools import document
from ..mapping.evaluation import after_stat
from .contours import contour_bands
from .stat_density_2d import stat_density_2d


@document
class stat_density_2d_filled(stat_density_2d):
    """
    Filled contour bands for a two-dimensional density estimate

    {usage}

    Parameters
    ----------
    {common_parameters}
    contour :
        Whether to contour the two-dimensional density estimate.
    contour_var :
        Computed variable that sets contour heights. Use `density`,
        `ndensity` or `count`.
    n :
        Number of equally spaced points at which the density is to
        be estimated. For efficient computation, it should be a power
        of two.
    bins :
        Number of contour bands. Takes precedence over `binwidth`.
    binwidth :
        Distance between adjacent contour values.
    breaks :
        Explicit contour values, or a function that receives the range of
        `contour_var` and distance between contours. Explicit values
        override `bins` and `binwidth`. A function uses the distance
        selected by `bins` or `binwidth`. By default, values are selected
        for ten bands.
    package :
        Package whose kernel density estimation to use.
    kde_params :
        Keyword arguments to pass on to the kde class.

    See Also
    --------
    plotnine.stat_density_2d : The same estimate, contoured into lines.
    plotnine.geom_density_2d_filled : The default `geom` for this `stat`.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "density"     # Computed density at a point
    "ndensity"    # Density, scaled to a maximum of 1
    "count"       # Density scaled by the number of observations
    "n"           # Number of observations at a point
    "level"       # band, an ordered interval such as "(0.005, 0.01]"
    "level_low"   # lower bound of the band
    "level_high"  # upper bound of the band
    "level_mid"   # midpoint between the bounds
    "nlevel"      # upper bound, scaled to a maximum of 1
    "piece"       # numeric id of a band in a given group
    "subgroup"    # ring index within a piece; 0 is outer, rest are holes
    ```

    Without contouring, the output contains `density`, `ndensity`, `count`
    and `n`. With contouring, it contains the band level and bounds,
    `nlevel`, `piece` and `subgroup`.
    """
    DEFAULT_AES = {"fill": after_stat("level")}
    DEFAULT_PARAMS = {"geom": "density_2d_filled"}
    CREATES = {
        "y",
        "density",
        "ndensity",
        "count",
        "n",
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

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

    DEFAULT_AES = {"fill": after_stat("level")}
    DEFAULT_PARAMS = {"geom": "density_2d_filled"}

    def compute_contours(self, x, y, Z, breaks, group):
        """
        Trace each band between neighbouring breaks on an axis-aligned grid
        """
        return contour_bands(x, y, Z, breaks, group)

from ..doctools import document
from .geom_polygon import geom_polygon


@document
class geom_contour_filled(geom_polygon):
    """
    Filled contour bands for a gridded surface

    {usage}

    Represent a three-dimensional surface in two dimensions with bands
    between neighbouring contour values.

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.stat_contour_filled : The default `stat` for this `geom`.
    """

    DEFAULT_PARAMS = {"stat": "contour_filled"}

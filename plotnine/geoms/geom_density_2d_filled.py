from ..doctools import document
from .geom_polygon import geom_polygon


@document
class geom_density_2d_filled(geom_polygon):
    """
    Filled contour bands for a two-dimensional density estimate

    {usage}

    Fill the regions between neighbouring contour values from a
    two-dimensional kernel density estimate.

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.stat_density_2d_filled : The default `stat` for this `geom`.
    """

    DEFAULT_PARAMS = {"stat": "density_2d_filled"}

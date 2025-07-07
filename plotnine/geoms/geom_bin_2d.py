from ..doctools import document
from .geom_rect import geom_rect


@document
class geom_bin_2d(geom_rect):
    """
    Heatmap of 2d bin counts

    {usage}

    Divides the plane into rectangles, counts the number of
    cases in each rectangle, and then (by default) maps the number
    of cases to the rectangle's fill. This is a useful alternative
    to geom_point in the presence of overplotting.

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.stat_bin_2d : The default stat for this `geom`.
    """

    DEFAULT_PARAMS = {"stat": "bin_2d", "position": "identity", "na_rm": False}


geom_bin2d = geom_bin_2d

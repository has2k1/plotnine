from ..doctools import document
from .geom_path import geom_path


@document
class geom_contour(geom_path):
    """
    Contour lines for a gridded surface

    {usage}

    Represent a three-dimensional surface in two dimensions with lines
    of equal `z`.

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.stat_contour : The default `stat` for this `geom`.
    """

    DEFAULT_PARAMS = {"stat": "contour"}

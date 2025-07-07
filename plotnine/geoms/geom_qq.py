from ..doctools import document
from .geom_point import geom_point


@document
class geom_qq(geom_point):
    """
    Quantile-Quantile plot

    {usage}

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.stat_qq : The default `stat` for this `geom`.
    """

    DEFAULT_PARAMS = {"stat": "qq", "position": "identity", "na_rm": False}

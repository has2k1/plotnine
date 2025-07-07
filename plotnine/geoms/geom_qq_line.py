from ..doctools import document
from .geom_path import geom_path


@document
class geom_qq_line(geom_path):
    """
    Quantile-Quantile Line plot

    {usage}

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.stat_qq_line : The default `stat` for this `geom`.
    """

    DEFAULT_PARAMS = {
        "stat": "qq_line",
        "position": "identity",
        "na_rm": False,
    }

from ..doctools import document
from .geom_path import geom_path


@document
class geom_quantile(geom_path):
    """
    Quantile lines from a quantile regression

    {usage}

    Parameters
    ----------
    {common_parameters}
    lineend : Literal["butt", "round", "projecting"], default="butt"
        Line end style. This option is applied for solid linetypes.
    linejoin : Literal["round", "miter", "bevel"], default="round"
        Line join style. This option is applied for solid linetypes.

    See Also
    --------
    plotnine.stat_quantile : The default `stat` for this `geom`.
    """

    DEFAULT_AES = {
        "alpha": 1,
        "color": "#3366FF",
        "linetype": "solid",
        "size": 0.5,
    }
    DEFAULT_PARAMS = {
        "stat": "quantile",
        "position": "identity",
        "na_rm": False,
        "lineend": "butt",
        "linejoin": "round",
    }

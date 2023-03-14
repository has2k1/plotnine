from ..doctools import document
from .geom_point import geom_point


@document
class geom_pointdensity(geom_point):
    """
    Scatterplot with density estimation at each point

    {usage}

    Parameters
    ----------
    {common_parameters}
    """

    DEFAULT_PARAMS = {
        "stat": "pointdensity",
        "position": "identity",
        "na_rm": False,
    }

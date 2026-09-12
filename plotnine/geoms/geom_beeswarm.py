from ..doctools import document
from .geom_point import geom_point


@document
class geom_beeswarm(geom_point):
    """
    Draw a beeswarm plot

    {usage}

    A beeswarm plot arranges points along one variable and spreads
    nearby values sideways into a swarm. The default deterministic
    placement assigns a low-discrepancy sequence by `y` rank.

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.stat_beeswarm : The default `stat` for this `geom`.
    """

    DEFAULT_PARAMS = {"stat": "beeswarm", "position": "dodge"}

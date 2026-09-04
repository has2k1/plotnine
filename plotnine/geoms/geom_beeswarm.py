from ..doctools import document
from .geom_point import geom_point


@document
class geom_beeswarm(geom_point):
    """
    Draw a beeswarm plot

    {usage}

    A beeswarm plot is a data visualization chart suitable for plotting
    any single variable in a multiclass dataset. It is an enhanced
    jitter strip chart, where the width of the jitter is controlled
    by the density distribution of the data within each class.

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.stat_beeswarm : The default `stat` for this `geom`.

    References
    ----------

    """

    DEFAULT_PARAMS = {"stat": "beeswarm", "position": "dodge"}

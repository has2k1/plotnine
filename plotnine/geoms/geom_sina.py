from ..doctools import document
from .geom_point import geom_point


@document
class geom_sina(geom_point):
    """
    Draw a sina plot

    A sina plot is a data visualization chart suitable for plotting
    any single variable in a multiclass dataset. It is an enhanced
    jitter strip chart, where the width of the jitter is controlled
    by the density distribution of the data within each class.

    {usage}

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.stats.stat_sina

    References
    ----------
    Sidiropoulos, N., S. H. Sohi, T. L. Pedersen, B. T. Porse, O. Winther,
    N. Rapin, and F. O. Bagger. 2018.
    "SinaPlot: An Enhanced Chart for Simple and Truthful Representation of
    Single Observations over Multiple Classes."
    J. Comp. Graph. Stat 27: 673–76.
    """
    DEFAULT_PARAMS = {'stat': 'sina', 'position': 'dodge',
                      'na_rm': False}

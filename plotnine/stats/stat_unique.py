from ..doctools import document
from .stat import stat


@document
class stat_unique(stat):
    """
    Remove duplicates

    {usage}

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.geom_point : The default `geom` for this `stat`.
    """

    DEFAULT_PARAMS = {"geom": "point", "position": "identity", "na_rm": False}

    def compute_panel(self, data, scales):
        return data.drop_duplicates()

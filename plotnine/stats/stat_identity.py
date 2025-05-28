from ..doctools import document
from .stat import stat


@document
class stat_identity(stat):
    """
    Identity (do nothing) statistic

    {usage}

    Parameters
    ----------
    {common_parameters}
    """

    DEFAULT_PARAMS = {"geom": "point", "position": "identity", "na_rm": False}

    def compute_panel(self, data, scales):
        return data

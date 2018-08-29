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
    DEFAULT_PARAMS = {'geom': 'point', 'position': 'identity',
                      'na_rm': False}

    @classmethod
    def compute_panel(cls, data, scales, **params):
        return data

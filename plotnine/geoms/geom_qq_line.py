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
    """
    DEFAULT_PARAMS = {'stat': 'qq_line', 'position': 'identity',
                      'na_rm': False}

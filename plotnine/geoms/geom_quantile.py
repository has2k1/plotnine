from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils.doctools import document
from .geom_path import geom_path


@document
class geom_quantile(geom_path):
    """
    Quantile lines from a quantile regression

    {usage}

    Parameters
    ----------
    {common_parameters}

    {aesthetics}
    """
    DEFAULT_AES = {'alpha': 1, 'color': '#3366FF',
                   'linetype': 'solid', 'size': 0.5}
    DEFAULT_PARAMS = {'stat': 'quantile', 'position': 'identity',
                      'lineend': 'butt', 'linejoin': 'round',
                      'na_rm': False}

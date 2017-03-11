from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

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
    lineend : str (default: butt)
        Line end style, of of *butt*, *round* or *projecting.*
        This option is applied for solid linetypes.
    linejoin : str (default: round)
        Line join style, one of *round*, *miter* or *bevel*.
        This option is applied for solid linetypes.

    {aesthetics}
    """
    DEFAULT_AES = {'alpha': 1, 'color': '#3366FF',
                   'linetype': 'solid', 'size': 0.5}
    DEFAULT_PARAMS = {'stat': 'quantile', 'position': 'identity',
                      'na_rm': False, 'lineend': 'butt',
                      'linejoin': 'round'}

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils.doctools import document
from .geom_area import geom_area


@document
class geom_density(geom_area):
    """
    Smooth density estimate

    {documentation}
    """
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'fill': None,
                   'linetype': 'solid', 'size': 0.5, 'weight': 1}
    DEFAULT_PARAMS = {'stat': 'density', 'position': 'identity',
                      'na_rm': False}

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .geom_area import geom_area


class geom_density(geom_area):
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'fill': None,
                   'linetype': 'solid', 'size': 1.0, 'weight': 1}
    DEFAULT_PARAMS = {'stat': 'density', 'position': 'identity'}

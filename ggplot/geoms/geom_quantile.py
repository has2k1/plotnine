from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .geom_path import geom_path


class geom_quantile(geom_path):
    DEFAULT_AES = {'alpha': 1, 'color': '#3366FF',
                   'linetype': 'solid', 'size': 1.5}
    DEFAULT_PARAMS = {'stat': 'quantile', 'position': 'identity',
                      'lineend': 'butt', 'linejoin': 'round'}

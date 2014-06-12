from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom_bar import geom_bar

class geom_histogram(geom_bar):
    DEFAULT_PARAMS = {'stat': 'bin', 'position': 'stack'}

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from copy import deepcopy

from .geom_point import geom_point


class geom_jitter(geom_point):
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'jitter'}

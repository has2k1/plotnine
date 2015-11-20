from __future__ import (absolute_import, division, print_function)

from .geom_path import geom_path


_params = geom_path.DEFAULT_PARAMS.copy()
_params['stat'] = 'bin'


class geom_freqpoly(geom_path):
    DEFAULT_PARAMS = _params

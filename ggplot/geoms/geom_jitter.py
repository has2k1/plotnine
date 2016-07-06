from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils.exceptions import GgplotError
from ..positions import position_jitter
from .geom_point import geom_point


class geom_jitter(geom_point):
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'jitter',
                      'width': None, 'height': None}

    def __init__(self, *args, **kwargs):
        if 'width' in kwargs or 'height' in kwargs:
            if 'position' in kwargs:
                raise GgplotError(
                    "Specify either 'position' or 'width'/'height'")

            try:
                width = kwargs.pop('width')
            except KeyError:
                width = None

            try:
                height = kwargs.pop('height')
            except KeyError:
                height = None

            kwargs['position'] = position_jitter(
                width=width, height=height)
        geom_point.__init__(self, *args, **kwargs)

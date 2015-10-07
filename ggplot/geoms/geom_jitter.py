from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import suppress
from ..utils.exceptions import GgplotError
from ..positions import position_jitter
from .geom_point import geom_point


class geom_jitter(geom_point):
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'jitter',
                      'width': None, 'height': None}

    def __init__(self, *args, **kwargs):
        print(kwargs)
        if 'width' in kwargs or 'height' in kwargs:
            if 'position' in kwargs:
                raise GgplotError(
                    "Specify either 'position' or 'width'/'height'")

            with suppress(KeyError):
                width = None
                width = kwargs.pop('width')

            with suppress(KeyError):
                height = None
                height = kwargs.pop('height')

            kwargs['position'] = position_jitter(
                width=width, height=height)
        geom_point.__init__(self, *args, **kwargs)

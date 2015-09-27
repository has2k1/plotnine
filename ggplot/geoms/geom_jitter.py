from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import suppress
from ..utils.exceptions import GgplotError
from ..positions import position_jitter
from .geom_point import geom_point


class geom_jitter(geom_point):
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'jitter'}

    def __init__(self, *args, **kwargs):
        if 'width' not in kwargs and 'height' not in kwargs:
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
        super(geom_jitter, self).__init__(*args, **kwargs)

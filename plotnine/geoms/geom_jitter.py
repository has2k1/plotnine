from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils.doctools import document
from ..utils.exceptions import PlotnineError
from ..positions import position_jitter
from .geom_point import geom_point


@document
class geom_jitter(geom_point):
    """
    Scatter plot with points jittered to reduce overplotting

    {documentation}

    See Also
    --------
    :class:`~plotnine.positions.position_jitter` for the documentation
    of the parameters that affect the jittering.
    """
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'jitter',
                      'width': None, 'height': None, 'prng': None}

    def __init__(self, *args, **kwargs):
        if {'width', 'height', 'prng'} & set(kwargs):
            if 'position' in kwargs:
                raise PlotnineError(
                    "Specify either 'position' or "
                    "'width'/'height'/'prng'")

            try:
                width = kwargs.pop('width')
            except KeyError:
                width = None

            try:
                height = kwargs.pop('height')
            except KeyError:
                height = None

            try:
                prng = kwargs.pop('prng')
            except KeyError:
                prng = None

            kwargs['position'] = position_jitter(
                width=width, height=height, prng=prng)
        geom_point.__init__(self, *args, **kwargs)

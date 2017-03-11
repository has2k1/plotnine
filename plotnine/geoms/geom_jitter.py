from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils.doctools import document
from ..exceptions import PlotnineError
from ..positions import position_jitter
from .geom_point import geom_point


@document
class geom_jitter(geom_point):
    """
    Scatter plot with points jittered to reduce overplotting

    {usage}

    Parameters
    ----------
    {common_parameters}
    width : float, optional
        Proportion to jitter in horizontal direction.
        The default value is that from
        :class:`~plotnine.positions.position_jitter`
    height : float, optional
        Proportion to jitter in vertical direction.
        The default value is that from
        :class:`~plotnine.positions.position_jitter`.
    prng : numpy.random.RandomState, optional
        Random number generator to use. If `None`, then numpy
        global generator :class:`numpy.random` is used.

    {aesthetics}

    See Also
    --------
    * :class:`~plotnine.positions.position_jitter`
    * :class:`~plotnine.geoms.geom_point`
    """
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'jitter',
                      'na_rm': False, 'width': None, 'height': None,
                      'prng': None}

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

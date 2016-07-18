from __future__ import absolute_import, division, print_function

import numpy as np
from mizani.bounds import rescale_max
from mizani.palettes import abs_area, area_pal, rescale_pal

from ..utils import alias
from .scale import scale_discrete, scale_continuous


class scale_size_discrete(scale_discrete):
    """
    Discrete area size scale

    Parameters
    ----------
    range : array_like
        Minimum and maximum size of the plotting symbol.
        It must be of size 2.
    kwargs : dict
        Parameters passed on to :class:`.scale_discrete`
    """
    aesthetics = ['size']

    def __init__(self, range=(2, 6), **kwargs):
        def palette(n):
            area = np.linspace(range[0]**2, range[1]**2, n)
            return np.sqrt(area)

        self.palette = palette
        scale_discrete.__init__(self, **kwargs)


class scale_size_continuous(scale_continuous):
    """
    Continuous area size scale

    Parameters
    ----------
    range : array_like
        Minimum and maximum area of the plotting symbol.
        It must be of size 2.
    kwargs : dict
        Parameters passed on to :class:`.scale_continuous`
    """
    aesthetics = ['size']

    def __init__(self, range=(1, 6), **kwargs):
        self.palette = area_pal(range)
        scale_continuous.__init__(self, **kwargs)


alias('scale_size', scale_size_continuous)


class scale_size_radius(scale_continuous):
    """
    Continuous radius size scale

    Parameters
    ----------
    range : array_like
        Minimum and maximum radius of the plotting symbol.
        It must be of size 2.
    kwargs : dict
        Parameters passed on to :class:`.scale_continuous`
    """
    aesthetics = ['size']

    def __init__(self, range=(1, 6), **kwargs):
        self.palette = rescale_pal(range)
        scale_continuous.__init__(self, **kwargs)


class scale_size_area(scale_continuous):
    """
    Continuous area size scale

    Parameters
    ----------
    max_size : float
        Maximum size of the plotting symbol.
    kwargs : dict
        Parameters passed on to :class:`.scale_continuous`
    """
    aesthetics = ['size']
    rescaler = staticmethod(rescale_max)

    def __init__(self, max_size=6, **kwargs):
        self.palette = abs_area(max_size)
        scale_continuous.__init__(self, **kwargs)

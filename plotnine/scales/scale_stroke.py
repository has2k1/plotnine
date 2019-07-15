from warnings import warn

import numpy as np
from mizani.palettes import rescale_pal

from ..doctools import document
from ..exceptions import PlotnineWarning
from ..utils import alias
from .scale import scale_discrete, scale_continuous


@document
class scale_stroke_continuous(scale_continuous):
    """
    Continuous Stroke Scale

    Parameters
    ----------
    range : array_like
        Range ([Minimum, Maximum]) of output stroke values.
        Should be between 0 and 1. Default is ``(1, 6)``
    {superclass_parameters}
    """
    _aesthetics = ['stroke']

    def __init__(self, range=(1, 6), **kwargs):
        self.palette = rescale_pal(range)
        scale_continuous.__init__(self, **kwargs)


@document
class scale_stroke_ordinal(scale_discrete):
    """
    Discrete Stroke Scale

    Parameters
    ----------
    range : array_like
        Range ([Minimum, Maximum]) of output stroke values.
        Should be between 0 and 1. Default is ``(1, 6)``
    {superclass_parameters}
    """
    _aesthetics = ['stroke']

    def __init__(self, range=(1, 6), **kwargs):
        def palette(n):
            return np.linspace(range[0], range[1], n)

        self.palette = palette
        scale_discrete.__init__(self, **kwargs)


@document
class scale_stroke_discrete(scale_stroke_ordinal):
    """
    Discrete Stroke Scale

    Parameters
    ----------
    {superclass_parameters}
    """
    _aesthetics = ['stroke']

    def __init__(self, **kwargs):
        warn(
            "Using stroke for a ordinal variable is not advised.",
            PlotnineWarning
        )
        super().__init__(self, **kwargs)


alias('scale_stroke', scale_stroke_continuous)

from warnings import warn

import numpy as np

from .._utils.registry import alias
from ..doctools import document
from ..exceptions import PlotnineWarning
from .scale_continuous import scale_continuous
from .scale_discrete import scale_discrete


@document
class scale_stroke_continuous(scale_continuous):
    """
    Continuous Stroke Scale

    Parameters
    ----------
    range :
        Range ([Minimum, Maximum]) of output stroke values.
        Should be between 0 and 1.
    {superclass_parameters}
    """

    _aesthetics = ["stroke"]

    def __init__(self, range: tuple[float, float] = (1, 6), **kwargs):
        from mizani.palettes import rescale_pal

        # TODO: fix types in mizani
        self.palette = rescale_pal(range)  # pyright: ignore
        scale_continuous.__init__(self, **kwargs)


@document
class scale_stroke_ordinal(scale_discrete):
    """
    Discrete Stroke Scale

    Parameters
    ----------
    range :
        Range ([Minimum, Maximum]) of output stroke values.
        Should be between 0 and 1.
    {superclass_parameters}
    """

    _aesthetics = ["stroke"]

    def __init__(self, range: tuple[float, float] = (1, 6), **kwargs):
        def palette(value: int):
            return np.linspace(range[0], range[1], value)

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

    _aesthetics = ["stroke"]

    def __init__(self, **kwargs):
        warn(
            "Using stroke for a ordinal variable is not advised.",
            PlotnineWarning,
        )
        super().__init__(**kwargs)


@alias
class scale_stroke(scale_stroke_continuous):
    pass

from warnings import warn

import numpy as np

from .._utils.registry import alias
from ..doctools import document
from ..exceptions import PlotnineWarning
from .scale_continuous import scale_continuous
from .scale_datetime import scale_datetime
from .scale_discrete import scale_discrete


@document
class scale_alpha(scale_continuous):
    """
    Continuous Alpha Scale

    Parameters
    ----------
    range :
        Range ([Minimum, Maximum]) of output alpha values.
        Should be between 0 and 1.
    {superclass_parameters}
    """

    _aesthetics = ["alpha"]

    def __init__(self, range: tuple[float, float] = (0.1, 1), **kwargs):
        from mizani.palettes import rescale_pal

        self._palette = rescale_pal(range)
        scale_continuous.__init__(self, **kwargs)


@alias
class scale_alpha_continuous(scale_alpha):
    pass


@document
class scale_alpha_ordinal(scale_discrete):
    """
    Ordinal Alpha Scale

    Parameters
    ----------
    range :
        Range ([Minimum, Maximum]) of output alpha values.
        Should be between 0 and 1.
    {superclass_parameters}
    """

    _aesthetics = ["alpha"]

    def __init__(self, range: tuple[float, float] = (0.1, 1), **kwargs):
        def palette(value):
            return np.linspace(range[0], range[1], value)

        self.palette = palette
        scale_discrete.__init__(self, **kwargs)


@document
class scale_alpha_discrete(scale_alpha_ordinal):
    """
    Discrete Alpha Scale

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["alpha"]

    def __init__(self, **kwargs):
        warn(
            "Using alpha for a discrete variable is not advised.",
            PlotnineWarning,
        )
        super().__init__(**kwargs)


@document
class scale_alpha_datetime(scale_datetime):
    """
    Datetime Alpha Scale

    Parameters
    ----------
    range : tuple
        Range ([Minimum, Maximum]) of output alpha values.
        Should be between 0 and 1.
    {superclass_parameters}
    """

    _aesthetics = ["alpha"]

    def __init__(self, range: tuple[float, float] = (0.1, 1), **kwargs):
        from mizani.palettes import rescale_pal

        # TODO: fix types in mizani
        self.palette = rescale_pal(range)  # pyright: ignore
        scale_datetime.__init__(self, **kwargs)

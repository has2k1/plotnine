from warnings import warn

import numpy as np
from mizani.bounds import rescale_max

from .._utils.registry import alias
from ..doctools import document
from ..exceptions import PlotnineWarning
from .scale_continuous import scale_continuous
from .scale_datetime import scale_datetime
from .scale_discrete import scale_discrete


@document
class scale_size_ordinal(scale_discrete):
    """
    Discrete area size scale

    Parameters
    ----------
    range :
        Minimum and maximum size of the plotting symbol.
        It must be of size 2.
    {superclass_parameters}
    """

    _aesthetics = ["size"]

    def __init__(self, range: tuple[float, float] = (2, 6), **kwargs):
        def palette(value):
            area = np.linspace(range[0] ** 2, range[1] ** 2, value)
            return np.sqrt(area)

        self.palette = palette
        scale_discrete.__init__(self, **kwargs)


@document
class scale_size_discrete(scale_size_ordinal):
    """
    Discrete area size scale

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["size"]

    def __init__(self, **kwargs):
        warn(
            "Using size for a discrete variable is not advised.",
            PlotnineWarning,
        )
        super().__init__(**kwargs)


@document
class scale_size_continuous(scale_continuous):
    """
    Continuous area size scale

    Parameters
    ----------
    range :
        Minimum and maximum area of the plotting symbol.
        It must be of size 2.
    {superclass_parameters}
    """

    _aesthetics = ["size"]

    def __init__(self, range: tuple[float, float] = (1, 6), **kwargs):
        from mizani.palettes import area_pal

        # TODO: fix types in mizani
        self.palette = area_pal(range)  # pyright: ignore
        scale_continuous.__init__(self, **kwargs)


@alias
class scale_size(scale_size_continuous):
    pass


@document
class scale_size_radius(scale_continuous):
    """
    Continuous radius size scale

    Parameters
    ----------
    range :
        Minimum and maximum radius of the plotting symbol.
        It must be of size 2.
    {superclass_parameters}
    """

    _aesthetics = ["size"]

    def __init__(self, range: tuple[float, float] = (1, 6), **kwargs):
        from mizani.palettes import rescale_pal

        # TODO: fix types in mizani
        self.palette = rescale_pal(range)  # pyright: ignore
        scale_continuous.__init__(self, **kwargs)


@document
class scale_size_area(scale_continuous):
    """
    Continuous area size scale

    Parameters
    ----------
    max_size :
        Maximum size of the plotting symbol.
    {superclass_parameters}
    """

    _aesthetics = ["size"]
    rescaler = staticmethod(rescale_max)

    def __init__(self, max_size: float = 6, **kwargs):
        from mizani.palettes import abs_area

        # TODO: fix types in mizani
        self.palette = abs_area(max_size)  # pyright: ignore
        scale_continuous.__init__(self, **kwargs)


@document
class scale_size_datetime(scale_datetime):
    """
    Datetime area-size scale

    Parameters
    ----------
    range :
        Minimum and maximum area of the plotting symbol.
        It must be of size 2.
    {superclass_parameters}
    """

    _aesthetics = ["size"]

    def __init__(self, range: tuple[float, float] = (1, 6), **kwargs):
        from mizani.palettes import area_pal

        # TODO: fix types in mizani
        self.palette = area_pal(range)  # pyright: ignore
        scale_datetime.__init__(self, **kwargs)

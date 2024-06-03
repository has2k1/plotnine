from dataclasses import KW_ONLY, InitVar, dataclass
from typing import Literal
from warnings import warn

import numpy as np
from mizani.bounds import rescale_max

from .._utils.registry import alias
from ..exceptions import PlotnineWarning
from .scale_continuous import scale_continuous
from .scale_datetime import scale_datetime
from .scale_discrete import scale_discrete


@dataclass
class scale_size_ordinal(scale_discrete):
    """
    Discrete area size scale
    """

    _aesthetics = ["size"]
    range: InitVar[tuple[float, float]] = (2, 6)
    """
    Range ([Minimum, Maximum]) of the size.
    """

    def __post_init__(self, range):
        super().__post_init__()

        def palette(value):
            area = np.linspace(range[0] ** 2, range[1] ** 2, value)
            return np.sqrt(area)

        self.palette = palette  # type: ignore


@dataclass
class scale_size_discrete(scale_size_ordinal):
    """
    Discrete area size scale
    """

    _aesthetics = ["size"]

    def __post_init__(self, range):
        warn(
            "Using size for a discrete variable is not advised.",
            PlotnineWarning,
        )
        super().__post_init__(range)


@dataclass
class scale_size_continuous(scale_continuous[Literal["legend"] | None]):
    """
    Continuous area size scale
    """

    _aesthetics = ["size"]
    range: InitVar[tuple[float, float]] = (1, 6)
    """
    Range ([Minimum, Maximum]) of the size.
    """

    _: KW_ONLY
    guide: Literal["legend"] | None = "legend"

    def __post_init__(self, range):
        from mizani.palettes import area_pal

        super().__post_init__()
        self.palette = area_pal(range)


@alias
class scale_size(scale_size_continuous):
    pass


@dataclass
class scale_size_radius(scale_continuous[Literal["legend"] | None]):
    """
    Continuous radius size scale
    """

    _aesthetics = ["size"]
    range: InitVar[tuple[float, float]] = (1, 6)
    """
    Range ([Minimum, Maximum]) of the size.
    """

    _: KW_ONLY
    guide: Literal["legend"] | None = "legend"

    def __post_init__(self, range):
        from mizani.palettes import rescale_pal

        super().__post_init__()
        self.palette = rescale_pal(range)


@dataclass
class scale_size_area(scale_continuous[Literal["legend"] | None]):
    """
    Continuous area size scale
    """

    _aesthetics = ["size"]
    max_size: InitVar[float] = 6
    """
    Maximum size of the plotting symbol.
    """

    _: KW_ONLY
    rescaler = rescale_max
    guide: Literal["legend"] | None = "legend"

    def __post_init__(self, max_size):
        from mizani.palettes import abs_area

        super().__post_init__()
        self.palette = abs_area(max_size)


@dataclass
class scale_size_datetime(scale_datetime):
    """
    Datetime area-size scale
    """

    _aesthetics = ["size"]
    range: InitVar[tuple[float, float]] = (1, 6)
    """
    Range ([Minimum, Maximum]) of the size.
    """

    _: KW_ONLY
    guide: Literal["legend"] | None = "legend"

    def __post_init__(
        self, range, date_breaks, date_labels, date_minor_breaks
    ):
        from mizani.palettes import area_pal

        super().__post_init__(date_breaks, date_labels, date_minor_breaks)
        self.palette = area_pal(range)

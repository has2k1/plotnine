from dataclasses import KW_ONLY, InitVar, dataclass
from typing import Literal
from warnings import warn

import numpy as np

from .._utils.registry import alias
from ..exceptions import PlotnineWarning
from .scale_continuous import scale_continuous
from .scale_datetime import scale_datetime
from .scale_discrete import scale_discrete


@dataclass
class scale_alpha(scale_continuous[Literal["legend"]]):
    """
    Continuous Alpha Scale
    """

    _aesthetics = ["alpha"]
    range: InitVar[tuple[float, float]] = (0.1, 1)
    """
    Range ([Minimum, Maximum]) of output alpha values.
    Should be between 0 and 1.
    """

    _: KW_ONLY
    guide: Literal["legend"] = "legend"

    def __post_init__(self, range):
        from mizani.palettes import rescale_pal

        super().__post_init__()
        self.palette = rescale_pal(range)


@alias
class scale_alpha_continuous(scale_alpha):
    pass


@dataclass
class scale_alpha_ordinal(scale_discrete):
    """
    Ordinal Alpha Scale
    """

    _aesthetics = ["alpha"]
    range: InitVar[tuple[float, float]] = (0.1, 1)
    """
    Range ([Minimum, Maximum]) of output alpha values.
    Should be between 0 and 1.
    """

    def __post_init__(self, range):
        super().__post_init__()

        def palette(n):
            return np.linspace(range[0], range[1], n)

        self.palette = palette


@dataclass
class scale_alpha_discrete(scale_alpha_ordinal):
    """
    Discrete Alpha Scale
    """

    def __post_init__(self, range):
        warn(
            "Using alpha for a discrete variable is not advised.",
            PlotnineWarning,
        )
        super().__post_init__(range)


@dataclass
class scale_alpha_datetime(scale_datetime):
    """
    Datetime Alpha Scale
    """

    _aesthetics = ["alpha"]
    range: InitVar[tuple[float, float]] = (0.1, 1)
    """
    Range ([Minimum, Maximum]) of output alpha values.
    Should be between 0 and 1.
    """

    _: KW_ONLY
    guide: Literal["legend"] = "legend"

    def __post_init__(
        self,
        date_breaks: str | None,
        date_labels: str | None,
        date_minor_breaks: str | None,
        range: tuple[float, float],
    ):
        from mizani.palettes import rescale_pal

        self.palette = rescale_pal(range)
        super().__post_init__(date_breaks, date_labels, date_minor_breaks)

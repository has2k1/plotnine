from dataclasses import KW_ONLY, InitVar, dataclass
from typing import Literal
from warnings import warn

import numpy as np

from .._utils.registry import alias
from ..exceptions import PlotnineWarning
from .scale_continuous import scale_continuous
from .scale_discrete import scale_discrete


@dataclass
class scale_stroke_continuous(scale_continuous[Literal["legend"] | None]):
    """
    Continuous Stroke Scale
    """

    _aesthetics = ["stroke"]
    range: InitVar[tuple[float, float]] = (1, 6)
    """
    Range ([Minimum, Maximum]) of output stroke values.
    Should be between 0 and 1.
    """
    _: KW_ONLY
    guide: Literal["legend"] | None = "legend"

    def __post_init__(self, range):
        from mizani.palettes import rescale_pal

        super().__post_init__()
        self.palette = rescale_pal(range)


@dataclass
class scale_stroke_ordinal(scale_discrete):
    """
    Discrete Stroke Scale
    """

    _aesthetics = ["stroke"]
    range: InitVar[tuple[float, float]] = (1, 6)
    """
    Range ([Minimum, Maximum]) of output stroke values.
    Should be between 0 and 1.
    """

    def __post_init__(self, range):
        super().__post_init__()

        def palette(n: int):
            return np.linspace(range[0], range[1], n)

        self.palette = palette


@dataclass
class scale_stroke_discrete(scale_stroke_ordinal):
    """
    Discrete Stroke Scale
    """

    _aesthetics = ["stroke"]

    def __post_init__(self, range):
        warn(
            "Using stroke for a ordinal variable is not advised.",
            PlotnineWarning,
        )
        super().__post_init__(
            range,
        )


@alias
class scale_stroke(scale_stroke_continuous):
    pass

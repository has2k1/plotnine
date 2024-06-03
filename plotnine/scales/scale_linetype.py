from dataclasses import dataclass
from warnings import warn

from .._utils.registry import alias
from ..exceptions import PlotnineError, PlotnineWarning
from .scale_continuous import scale_continuous
from .scale_discrete import scale_discrete

LINETYPES = ["solid", "dashed", "dashdot", "dotted"]


@dataclass
class scale_linetype(scale_discrete):
    """
    Scale for line patterns

    Notes
    -----
    The available linetypes are
    `'solid', 'dashed', 'dashdot', 'dotted'`
    If you need more custom linetypes, use
    [](`~plotnine.scales.scale_linetype_manual`)
    """

    _aesthetics = ["linetype"]

    def __post_init__(self):
        from mizani.palettes import manual_pal

        super().__post_init__()
        self.palette = manual_pal(LINETYPES)


@dataclass
class scale_linetype_ordinal(scale_linetype):
    """
    Scale for line patterns
    """

    _aesthetics = ["linetype"]

    def __post_init__(self):
        super().__post_init__()

        warn(
            "Using linetype for an ordinal variable is not advised.",
            PlotnineWarning,
        )


class scale_linetype_continuous(scale_continuous):
    """
    Linetype scale
    """

    def __init__(self):
        raise PlotnineError(
            "A continuous variable can not be mapped to linetype"
        )


@alias
class scale_linetype_discrete(scale_linetype):
    pass

from dataclasses import KW_ONLY, dataclass
from warnings import warn

from plotnine.scales._runtime_typing import OptionalLegend

from .._utils.registry import alias
from ..exceptions import PlotnineError, PlotnineWarning
from .scale_continuous import scale_continuous
from .scale_discrete import scale_discrete

HATCHES = ["/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]


@dataclass
class scale_hatch(scale_discrete[OptionalLegend]):
    r"""
    Scale for hatch patterns

    Notes
    -----
    The available hatch patterns are those standard in matplotlib:
    `'/', '\', '|', '-', '+', 'x', 'o', 'O', '.', '*'`

    Repeating a character increases the density of that pattern, and
    characters can be combined: `'//'`, `'xx'`, `'.o'`. If you need
    per-level control, use [](`~plotnine.scales.scale_hatch_manual`).
    """

    _aesthetics = ["hatch"]

    _: KW_ONLY
    guide: OptionalLegend = "legend"

    def __post_init__(self):
        from mizani.palettes import manual_pal

        super().__post_init__()
        self.palette = manual_pal(HATCHES)


@dataclass
class scale_hatch_ordinal(scale_hatch):
    """
    Scale for hatch patterns of an ordinal variable
    """

    _aesthetics = ["hatch"]

    def __post_init__(self):
        super().__post_init__()

        warn(
            "Using hatch for an ordinal variable is not advised.",
            PlotnineWarning,
        )


class scale_hatch_continuous(scale_continuous):
    """
    Hatch scale

    Notes
    -----
    A continuous variable cannot be mapped to hatch. `Scales.add_defaults`
    swallows this error and leaves the column unscaled, so the message a
    user sees comes from the geom, not from here -- the same as
    `scale_linetype_continuous`.
    """

    def __init__(self):
        raise PlotnineError("A continuous variable cannot be mapped to hatch")


@alias
class scale_hatch_discrete(scale_hatch):
    pass

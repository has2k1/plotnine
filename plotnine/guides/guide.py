from __future__ import annotations

from abc import ABC
from dataclasses import asdict, dataclass, field
from functools import cached_property
from types import SimpleNamespace as NS
from typing import TYPE_CHECKING, cast

from .._utils import ensure_xy_location, get_opposite_side
from .._utils.registry import Register
from ..themes.theme import theme as Theme

if TYPE_CHECKING:
    from typing import Literal, Optional, TypeAlias

    import pandas as pd
    from matplotlib.offsetbox import PackerBase
    from typing_extensions import Self

    from plotnine import aes, guides
    from plotnine.layer import Layers, layer
    from plotnine.scales.scale import scale
    from plotnine.typing import (
        LegendPosition,
        Orientation,
        Side,
    )

    from .guides import GuidesElements

    AlignDict: TypeAlias = dict[
        Literal["ha", "va"], dict[tuple[Orientation, Side], str]
    ]


@dataclass
class guide(ABC, metaclass=Register):
    """
    Base class for all guides

    Notes
    -----
    At the moment not all parameters have been fully implemented.
    """

    title: Optional[str] = None
    """
    Title of the guide. Default is the name of the aesthetic or the
    name specified using [](`~plotnine.components.labels.lab`)
    """

    theme: Theme = field(default_factory=Theme)
    """A theme to style the guide. If `None`, the plots theme is used."""

    position: Optional[LegendPosition] = None
    """Where to place the guide relative to the panels."""

    direction: Optional[Orientation] = None
    """
    Direction of the guide. The default is depends on
    [](`~plotnine.themes.themeable.legend_position`).
    """

    reverse: bool = False
    """Whether to reverse the order of the legend keys."""

    order: int = 0
    """Order of this guide among multiple guides."""

    # Non-Parameter Attributes
    available_aes: set[str] = field(init=False, default_factory=set)

    def __post_init__(self):
        self.hash: str
        self.key: pd.DataFrame
        self.plot_layers: Layers
        self.plot_mapping: aes
        self._elements_cls = GuideElements
        self.elements = cast("GuideElements", None)
        self.guides_elements: GuidesElements

    def legend_aesthetics(self, layer: layer):
        """
        Return the aesthetics that contribute to the legend

        Parameters
        ----------
        layer : Layer
            Layer whose legend is to be drawn

        Returns
        -------
        matched : list
            List of the names of the aethetics that contribute
            to the legend.
        """
        l = layer
        legend_ae = set(self.key.columns) - {"label"}
        all_ae = (
            l.mapping.keys()
            | (self.plot_mapping if l.inherit_aes else set())
            | l.stat.DEFAULT_AES.keys()
        )
        geom_ae = l.geom.REQUIRED_AES | l.geom.DEFAULT_AES.keys()
        matched = all_ae & geom_ae & legend_ae
        matched = list(matched - set(l.geom.aes_params))
        return matched

    def setup(self, guides: guides):
        """
        Setup guide for drawing process
        """
        # guide theme has priority and its targets are tracked
        # independently.
        self.theme = guides.plot.theme + self.theme
        self.theme.setup(guides.plot)
        self.plot_layers = guides.plot.layers
        self.plot_mapping = guides.plot.mapping
        self.elements = self._elements_cls(self.theme, self)
        self.guides_elements = guides.elements

    @property
    def _resolved_position_justification(
        self,
    ) -> tuple[Side, float] | tuple[tuple[float, float], tuple[float, float]]:
        """
        Return the final position & justification to draw the guide
        """
        pos = self.elements.position
        just_view = asdict(self.guides_elements.justification)
        if isinstance(pos, str):
            just = cast("float", just_view[pos])
            return (pos, just)
        else:
            # If no justification is given for an inside legend,
            # we use the position of the legend
            if (just := just_view["inside"]) is None:
                just = pos
            just = cast("tuple[float, float]", just)
            return (pos, just)

    def train(
        self, scale: scale, aesthetic: Optional[str] = None
    ) -> Self | None:
        """
        Create the key for the guide

        Returns guide if training is successful
        """

    def draw(self) -> PackerBase:
        """
        Draw guide
        """
        raise NotImplementedError

    def create_geoms(self) -> Optional[Self]:
        """
        Create layers of geoms for the guide

        Returns
        -------
        :
            self if geom layers were create or None of no geom layers
            were created.
        """
        raise NotImplementedError


@dataclass
class GuideElements:
    """
    Access & calculate theming for the guide
    """

    theme: Theme
    guide: guide

    def __post_init__(self):
        self.guide_kind = type(self.guide).__name__.split("_")[-1]
        self._elements_cls = GuideElements

    @cached_property
    def margin(self):
        return self.theme.getp("legend_margin")

    @cached_property
    def title(self):
        ha = self.theme.getp(("legend_title", "ha"))
        va = self.theme.getp(("legend_title", "va"), "center")
        _margin = self.theme.getp(("legend_title", "margin")).pt
        _loc = get_opposite_side(self.title_position)[0]
        margin = getattr(_margin, _loc)
        top_or_bottom = self.title_position in ("top", "bottom")
        is_blank = self.theme.T.is_blank("legend_title")

        # The original ha & va values are used by the HPacker/VPacker
        # to align the title textarea with the bundled legend keys.
        if self.is_vertical:
            align = (ha or "left") if top_or_bottom else va
        else:
            align = (ha or "center") if top_or_bottom else va

        return NS(
            margin=margin,
            align=align,
            ha="center",
            va="baseline",
            is_blank=is_blank,
        )

    @cached_property
    def text_position(self) -> Side:
        raise NotImplementedError

    @cached_property
    def _text_margin(self) -> float:
        _margin = self.theme.getp(
            (f"legend_text_{self.guide_kind}", "margin")
        ).pt
        _loc = get_opposite_side(self.text_position)[0]
        return getattr(_margin, _loc)

    @cached_property
    def title_position(self) -> Side:
        if not (pos := self.theme.getp("legend_title_position")):
            pos = "top" if self.is_vertical else "left"
        return pos

    @cached_property
    def direction(self) -> Orientation:
        if self.guide.direction:
            return self.guide.direction

        if not (direction := self.theme.getp("legend_direction")):
            direction = (
                "horizontal"
                if self.position in ("bottom", "top")
                else "vertical"
            )
        return direction

    @cached_property
    def position(self) -> Side | tuple[float, float]:
        if (guide_pos := self.guide.position) == "inside":
            guide_pos = self._position_inside

        if guide_pos:
            return guide_pos

        if (pos := self.theme.getp("legend_position", "right")) == "inside":
            pos = self._position_inside
        return pos

    @cached_property
    def _position_inside(self) -> Side | tuple[float, float]:
        pos = self.theme.getp("legend_position_inside")
        if isinstance(pos, tuple):
            return pos

        just = self.theme.getp("legend_justification_inside", (0.5, 0.5))
        return ensure_xy_location(just)

    #  These do not track the themeables directly
    @cached_property
    def is_vertical(self) -> bool:
        """
        Whether the guide is vertical
        """
        return self.direction == "vertical"

    @cached_property
    def is_horizontal(self) -> bool:
        """
        Whether the guide is horizontal
        """
        return self.direction == "horizontal"

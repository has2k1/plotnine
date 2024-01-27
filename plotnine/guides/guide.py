from __future__ import annotations

from abc import ABC
from copy import deepcopy
from dataclasses import dataclass, field
from functools import cached_property
from types import SimpleNamespace as NS
from typing import TYPE_CHECKING

from .._utils import get_opposite_side, no_init_mutable
from .._utils.registry import Register
from ..themes.theme import theme as Theme

if TYPE_CHECKING:
    from typing import Any, Literal, Optional, TypeAlias

    import pandas as pd
    from matplotlib.offsetbox import PackerBase
    from typing_extensions import Self

    from plotnine import aes, ggplot, theme
    from plotnine.layer import Layers
    from plotnine.scales.scale import scale
    from plotnine.typing import (
        LegendPosition,
        Orientation,
        SidePosition,
        Theme,
    )

    AlignDict: TypeAlias = dict[
        Literal["ha", "va"], dict[tuple[Orientation, SidePosition], str]
    ]


@dataclass
class guide(ABC, metaclass=Register):
    """
    Base class for all guides

    Parameters
    ----------
    title :
        Title of the guide. Default is the name of the aesthetic or the
        name specified using [](`~plotnine.components.labels.lab`)
    theme :
        A theme to style the guide. If `None`, the plots theme is used.
    position :
        Where to place the guide relative to the panels.
    direction :
        Direction of the guide. The default is depends on
        [](`~plotnine.themes.themeable.legend_position`).
    reverse : bool, default=False
        Whether to reverse the order of the legend keys.
    order : int
        Order of this guide among multiple guides.

    Notes
    -----
    At the moment not all parameters have been fully implemented.
    """

    title: Optional[str] = None
    theme: theme = field(default_factory=Theme)
    position: Optional[LegendPosition] = None
    direction: Optional[Orientation] = None
    reverse: bool = False
    order: int = 0

    # Non-Parameter Attributes
    available_aes: set[str] = no_init_mutable(set())

    def __post_init__(self):
        self.hash: str
        self.key: pd.DataFrame
        self.plot_layers: Layers
        self.plot_mapping: aes
        # if self.theme is None:
        #     self.theme = theme()

    def legend_aesthetics(self, layer):
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

    def setup(self, plot: ggplot):
        """
        Setup guide for drawing process
        """
        # guide theme has priority and its targets are tracked
        # independently.
        self.theme = plot.theme + self.theme
        self.plot_layers = plot.layers
        self.plot_mapping = plot.mapping

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

    theme: theme
    guide: guide

    def __post_init__(self):
        self.guide_kind = type(self.guide).__name__.split("_")[-1]

    @cached_property
    def margin(self):
        return self.theme.getp("legend_margin")

    @cached_property
    def title(self):
        ha = self.theme.getp(("legend_title", "ha"))
        va = self.theme.getp(("legend_title", "va"), "center")
        _margin = self.theme.getp(("legend_title", "margin"))
        _loc = get_opposite_side(self.title_position)[0]
        margin = _margin.get_as(_loc, "pt")
        top_or_bottom = self.title_position in ("top", "bottom")

        # The original ha & va values are used by the HPacker/VPacker
        # to align the title textarea with the bundled legend keys.
        if self.is_vertical:
            align = (ha or "left") if top_or_bottom else va
        else:
            align = (ha or "center") if top_or_bottom else va

        return NS(margin=margin, align=align, ha="center", va="baseline")

    @cached_property
    def text_position(self) -> SidePosition:
        if (pos := self.theme.P("legend_text_position")) == "auto":
            pos = "right" if self.is_vertical else "bottom"
        return pos

    @cached_property
    def title_position(self) -> SidePosition:
        if (pos := self.theme.P("legend_title_position")) == "auto":
            pos = "top" if self.is_vertical else "left"
        return pos

    @cached_property
    def direction(self) -> Orientation:
        if self.guide.direction:
            return self.guide.direction

        if (direction := self.theme.P("legend_direction")) == "auto":
            direction = (
                "vertical"
                if self.position in ("right", "left")
                else "horizontal"
            )
        return direction

    @cached_property
    def position(self) -> LegendPosition:
        return self.guide.position or self.theme.P("legend_position")

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

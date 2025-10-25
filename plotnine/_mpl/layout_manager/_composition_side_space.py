from __future__ import annotations

from typing import TYPE_CHECKING

from ._composition_layout_items import CompositionLayoutItems
from ._side_space import GridSpecParams, _side_space

if TYPE_CHECKING:
    from plotnine.composition._compose import Compose


class _composition_side_space(_side_space):
    """
    Base class for the side space around a composition
    """

    def __init__(self, items: CompositionLayoutItems):
        self.items = items
        self.gridspec = items.cmp._gridspec
        self._calculate()


class composition_left_space(_composition_side_space):
    plot_margin: float = 0

    def _calculate(self):
        theme = self.items.cmp.theme
        self.plot_margin = theme.getp("plot_margin_left")

    @property
    def offset(self) -> float:
        """
        Distance from left of the figure to the left of the plot gridspec

              ----------------(1, 1)
             |      ----      |
             |  dx |    |     |
             |<--->|    |     |
             |     |    |     |
             |      ----      |
        (0, 0)----------------

        """
        return self.gridspec.bbox_relative.x0

    def x1(self, item: str) -> float:
        """
        Lower x-coordinate in figure space of the item
        """
        return self.to_figure_space(self.sum_upto(item))

    def x2(self, item: str) -> float:
        """
        Higher x-coordinate in figure space of the item
        """
        return self.to_figure_space(self.sum_incl(item))

    @property
    def items_left_relative(self):
        """
        Left (relative to the gridspec) of the cmp items in figure dimensions
        """
        return self.total

    @property
    def items_left(self):
        """
        Left of the composition items in figure space
        """
        return self.to_figure_space(self.items_left_relative)

    @property
    def composition_left(self):
        """
        Distance up to the left-most artist in figure space
        """
        return self.x2("plot_margin")

    @property
    def composition_panel_left(self):
        """
        Left of the panels in figure space
        """
        # TODO: Fixme. Workout the actual panel left
        return self.composition_left


class composition_right_space(_composition_side_space):
    """
    Space for annotations to the right of the actual composition

    Ordered from the edge of the figure and going inwards
    """

    plot_margin: float = 0

    def _calculate(self):
        theme = self.items.cmp.theme
        self.plot_margin = theme.getp("plot_margin_right")

    @property
    def offset(self):
        """
        Distance from right of the figure to the right of the plot gridspec

              ---------------(1, 1)
             |     ----      |
             |    |    | -dx |
             |    |    |<--->|
             |    |    |     |
             |     ----      |
        (0, 0)---------------

        """
        return self.gridspec.bbox_relative.x1 - 1

    def x1(self, item: str) -> float:
        """
        Lower x-coordinate in figure space of the item
        """
        return self.to_figure_space(1 - self.sum_incl(item))

    def x2(self, item: str) -> float:
        """
        Higher x-coordinate in figure space of the item
        """
        return self.to_figure_space(1 - self.sum_upto(item))

    @property
    def items_right_relative(self):
        """
        Right (relative to the gridspec) of the panels in figure dimensions
        """
        return 1 - self.total

    @property
    def items_right(self):
        """
        Right of the panels in figure space
        """
        return self.to_figure_space(self.items_right_relative)

    @property
    def composition_right(self):
        """
        Distance up to the right-most artist in figure space
        """
        return self.x1("plot_margin")

    @property
    def composition_panel_right(self):
        """
        Right of the panels in figure space
        """
        # TODO: Fixme. Workout the actual panel right
        return self.composition_right


class composition_top_space(_composition_side_space):
    """
    Space for annotations above the actual composition

    Ordered from the edge of the figure and going inwards
    """

    plot_margin: float = 0
    plot_title_margin_top: float = 0
    plot_title: float = 0
    plot_title_margin_bottom: float = 0
    plot_subtitle_margin_top: float = 0
    plot_subtitle: float = 0
    plot_subtitle_margin_bottom: float = 0

    def _calculate(self):
        items = self.items
        theme = self.items.cmp.theme
        geometry = self.items.geometry
        W, H = theme.getp("figure_size")
        F = W / H

        self.plot_margin = theme.getp("plot_margin_top") * F

        if items.plot_title:
            m = theme.get_margin("plot_title").fig
            self.plot_title_margin_top = m.t * F
            self.plot_title = geometry.height(items.plot_title)
            self.plot_title_margin_bottom = m.b * F

        if items.plot_subtitle:
            m = theme.get_margin("plot_subtitle").fig
            self.plot_subtitle_margin_top = m.t * F
            self.plot_subtitle = geometry.height(items.plot_subtitle)
            self.plot_subtitle_margin_bottom = m.b * F

    @property
    def offset(self) -> float:
        """
        Distance from top of the figure to the top of the composition gridspec

              ----------------(1, 1)
             |       ^        |
             |       |-dy     |
             |       v        |
             |      ----      |
             |     |    |     |
             |     |    |     |
             |     |    |     |
             |      ----      |
             |                |
        (0, 0)----------------
        """
        return self.gridspec.bbox_relative.y1 - 1

    def y1(self, item: str) -> float:
        """
        Lower y-coordinate in figure space of the item
        """
        return self.to_figure_space(1 - self.sum_incl(item))

    def y2(self, item: str) -> float:
        """
        Higher y-coordinate in figure space of the item
        """
        return self.to_figure_space(1 - self.sum_upto(item))

    @property
    def items_top_relative(self):
        """
        Top (relative to the gridspec) of the panels in figure dimensions
        """
        return 1 - self.total

    @property
    def items_top(self):
        """
        Top of the composition items in figure space
        """
        return self.to_figure_space(self.items_top_relative)

    @property
    def composition_top(self):
        """
        Distance up to the top-most artist in figure space
        """
        return self.y2("plot_margin")

    @property
    def composition_panel_top(self):
        """
        Top of the panels in figure space
        """
        # TODO: Fixme. Workout the actual panel top
        return self.composition_top


class composition_bottom_space(_composition_side_space):
    """
    Space in the figure for artists below the panel area

    Ordered from the edge of the figure and going inwards
    """

    plot_margin: float = 0
    plot_caption_margin_bottom: float = 0
    plot_caption: float = 0
    plot_caption_margin_top: float = 0

    def _calculate(self):
        items = self.items
        theme = self.items.cmp.theme
        geometry = self.items.geometry
        W, H = theme.getp("figure_size")
        F = W / H

        self.plot_margin = theme.getp("plot_margin_bottom") * F

        if items.plot_caption:
            m = theme.get_margin("plot_caption").fig
            self.plot_caption_margin_bottom = m.b * F
            self.plot_caption = geometry.height(items.plot_caption)
            self.plot_caption_margin_top = m.t * F

    @property
    def offset(self) -> float:
        """
        Distance from bottom of the figure to the composition gridspec

              ----------------(1, 1)
             |                |
             |      ----      |
             |     |    |     |
             |     |    |     |
             |     |    |     |
             |      ----      |
             |       ^        |
             |       |dy      |
             |       v        |
        (0, 0)----------------
        """
        return self.gridspec.bbox_relative.y0

    def y1(self, item: str) -> float:
        """
        Lower y-coordinate in figure space of the item
        """
        return self.to_figure_space(self.sum_upto(item))

    def y2(self, item: str) -> float:
        """
        Higher y-coordinate in figure space of the item
        """
        return self.to_figure_space(self.sum_incl(item))

    @property
    def items_bottom_relative(self):
        """
        Bottom (relative to the gridspec) of the panels in figure dimensions
        """
        return self.total

    @property
    def items_bottom(self):
        """
        Bottom of the panels in figure space
        """
        return self.to_figure_space(self.items_bottom_relative)

    @property
    def composition_bottom(self):
        """
        Distance up to the bottom-most artist in figure space
        """
        return self.y1("plot_margin")

    @property
    def composition_panel_bottom(self):
        """
        Bottom of the panels in figure space
        """
        # TODO: Fixme. Workout the actual panel bottom
        return self.composition_bottom


class CompositionSideSpaces:
    gsparams: GridSpecParams
    """Grid spacing btn panels w.r.t figure"""

    def __init__(self, cmp: Compose):
        self.cmp = cmp
        self.items = CompositionLayoutItems(cmp)

        self.l = composition_left_space(self.items)
        """All subspaces to the left of the panels"""

        self.r = composition_right_space(self.items)
        """All subspaces to the right of the panels"""

        self.t = composition_top_space(self.items)
        """All subspaces above the top of the panels"""

        self.b = composition_bottom_space(self.items)
        """All subspaces below the bottom of the panels"""

    def get_gridspec_params(self) -> GridSpecParams:
        self.gsparams = GridSpecParams(
            self.l.items_left_relative,
            self.r.items_right_relative,
            self.t.items_top_relative,
            self.b.items_bottom_relative,
            0,
            0,
        )
        return self.gsparams

    @property
    def horizontal_space(self) -> float:
        """
        Horizontal non-panel space [figure dimensions]
        """
        return self.l.total + self.r.total

    @property
    def vertical_space(self) -> float:
        """
        Vertical non-panel space [figure dimensions]
        """
        return self.t.total + self.b.total

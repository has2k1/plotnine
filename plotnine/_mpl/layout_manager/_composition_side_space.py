from __future__ import annotations

from typing import TYPE_CHECKING

from plotnine._mpl.layout_manager._layout_tree import LayoutTree
from plotnine._mpl.layout_manager._plot_side_space import PlotSideSpaces

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


class CompositionSideSpaces:
    """
    Compute the spaces required to layout the composition

    This is meant for the top-most composition
    """

    def __init__(self, cmp: Compose):
        self.cmp = cmp
        self.gridspec = cmp._gridspec
        self.sub_gridspec = cmp._sub_gridspec
        self.items = CompositionLayoutItems(cmp)

        self.l = composition_left_space(self.items)
        """All subspaces to the left of the panels"""

        self.r = composition_right_space(self.items)
        """All subspaces to the right of the panels"""

        self.t = composition_top_space(self.items)
        """All subspaces above the top of the panels"""

        self.b = composition_bottom_space(self.items)
        """All subspaces below the bottom of the panels"""

        self._create_plot_sidespaces()
        self.tree = LayoutTree.create(cmp)

    def arrange(self):
        """
        Resize composition and place artists in final positions
        """
        # We first resize the compositions gridspec so that the tree
        # algorithms can work with the final position and total area.
        self.resize_gridspec()
        self.tree.arrange_layout()
        self.items._move_artists(self)
        self._arrange_plots()

    def _arrange_plots(self):
        """
        Arrange all the plots in the composition
        """
        for plot in self.cmp.iter_plots_all():
            plot._sidespaces.arrange()

    def _create_plot_sidespaces(self):
        """
        Create sidespaces for all the plots in the composition
        """
        for plot in self.cmp.iter_plots_all():
            plot._sidespaces = PlotSideSpaces(plot)

    def resize_gridspec(self):
        """
        Apply the space calculations to the sub_gridspec

        After calling this method, the sub_gridspec will be appropriately
        sized to accomodate the content of the annotations.
        """
        gsparams = self.calculate_gridspec_params()
        gsparams.validate()
        self.sub_gridspec.update_params_and_artists(gsparams)

    def calculate_gridspec_params(self) -> GridSpecParams:
        """
        Grid spacing between compositions w.r.t figure
        """
        return GridSpecParams(
            self.l.items_left_relative,
            self.r.items_right_relative,
            self.t.items_top_relative,
            self.b.items_bottom_relative,
            0,
            0,
        )

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

    @property
    def plot_left(self) -> float:
        """
        Distance up to left most artist in the composition
        """
        try:
            return min([l.plot_left for l in self.tree.left_most_spaces])
        except ValueError:
            return self.sub_gridspec.bbox_relative.x0

    @property
    def plot_right(self) -> float:
        """
        Distance up to right most artist in the composition
        """
        try:
            return max([r.plot_right for r in self.tree.right_most_spaces])
        except ValueError:
            # When the user asks for more columns than there are
            # plots/compositions to fill the columns, we get one or
            # more empty columns on the right. i.e. max([])
            # In that case, act as if there is an invisible plot
            # whose right edge is along that of the gridspec.
            return self.sub_gridspec.bbox_relative.x1

    @property
    def plot_bottom(self) -> float:
        """
        Distance up to bottom most artist in the composition
        """
        try:
            return min([b.plot_bottom for b in self.tree.bottom_most_spaces])
        except ValueError:
            return self.sub_gridspec.bbox_relative.y0

    @property
    def plot_top(self) -> float:
        """
        Distance upto top most artist in the composition
        """
        try:
            return max([t.plot_top for t in self.tree.top_most_spaces])
        except ValueError:
            return self.sub_gridspec.bbox_relative.y1

    @property
    def panel_left(self) -> float:
        """
        Distance up to left most artist in the composition
        """
        try:
            return min([l.panel_left for l in self.tree.left_most_spaces])
        except ValueError:
            return self.sub_gridspec.bbox_relative.x0

    @property
    def panel_right(self) -> float:
        """
        Distance up to right most artist in the composition
        """
        try:
            return max([r.panel_right for r in self.tree.right_most_spaces])
        except ValueError:
            return self.sub_gridspec.bbox_relative.x1

    @property
    def panel_bottom(self) -> float:
        """
        Distance up to bottom most artist in the composition
        """
        try:
            return min([b.panel_bottom for b in self.tree.bottom_most_spaces])
        except ValueError:
            return self.sub_gridspec.bbox_relative.y0

    @property
    def panel_top(self) -> float:
        """
        Distance upto top most artist in the composition
        """
        try:
            return max([t.panel_top for t in self.tree.top_most_spaces])
        except ValueError:
            return self.sub_gridspec.bbox_relative.y1

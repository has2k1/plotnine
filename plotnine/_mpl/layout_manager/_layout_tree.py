from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING, Iterator, cast

import numpy as np

from ._grid import Grid
from ._plot_side_space import PlotSideSpaces

if TYPE_CHECKING:
    from typing import Any, Callable, Literal, Sequence, TypeAlias

    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine._mpl.layout_manager._plot_side_space import (
        bottom_space,
        left_space,
        right_space,
        top_space,
    )
    from plotnine.composition import Compose

    Node: TypeAlias = "PlotSideSpaces | LayoutTree"


@dataclass
class LayoutTree:
    """
    A Tree representation of the composition

    The purpose of this class (and its subclasses) is to align and
    and resize plots in a composition. For example,

    This composition:

        (p1 | p2) | (p3 / p4)

    where p1, p2, p3 & p4 are ggplot objects would look like this;

         -----------------------------
        |         |         |         |
        |         |         |         |
        |         |         |         |
        |         |         |         |
        |         |         |---------|
        |         |         |         |
        |         |         |         |
        |         |         |         |
        |         |         |         |
         -----------------------------

    and the tree would have this structure;


                         LayoutTree (.nrow=1, .ncol=3)
                             |
               ----------------------------
              |              |             |
        LayoutSpaces    LayoutSpaces   LayoutTree (.nrow=2, .ncol=1)
                                           |
                                      -------------
                                     |             |
                               LayoutSpaces  LayoutSpaces

    This composition:

        (p1 + p2 + p4 + p5 + p6) + plot_layout(ncol=3)

    would look like this:

         -----------------------------
        |         |         |         |
        |         |         |         |
        |    p1   |    p2   |    p3   |
        |         |         |         |
        |---------|---------|---------|
        |         |         |         |
        |    p4   |    p5   |         |
        |         |         |         |
        |         |         |         |
         -----------------------------

    and have this structure


                                    LayoutTree (.nrow=3, .ncol=2)
                                          |
               -------------------------------------------------------
              |             |             |             |             |
        LayoutSpaces  LayoutSpaces  LayoutSpaces  LayoutSpaces  LayoutSpaces

    Each composition is a tree or subtree

    ## How it works

    Initially (and if the composition does not have annotation texts), the
    sub_gridspec occupies all the space available to it with the contained
    items (ggplot / Compose) having equal sizes.

    But if the full plot / composition occupy the same space, their panels
    may have different sizes because they have to share that space with the
    texts (title, subtitle, caption, axis title, axis text, tag), legends
    and plot margins that surround the panels.

    We align the panels, axis titles and tags by adding *_alignment margins;
    and resize the panels by

    Taking the sizes of these elements into account, we align the panels
    in the composition by changing the width and/or height of the gridspec.

    The information about the size (width & height) of the panels is in the
    LayoutSpaces.
    """

    cmp: Compose
    """
    Composition that this tree represents
    """

    nodes: list[PlotSideSpaces | LayoutTree]
    """
    The spaces or tree of spaces in the composition that the tree
    represents.
    """

    sub_gridspec: p9GridSpec = field(init=False, repr=False)
    """
    Gridspec (nxn) that contains the composed items
    """

    def __post_init__(self):
        self.sub_gridspec = self.cmp._sub_gridspec
        self.grid = Grid["Node"](
            self.nrow,
            self.ncol,
            self.nodes,
            order="row_major" if self.cmp.layout.byrow else "col_major",
        )

    @property
    def ncol(self) -> int:
        """
        Number of columns
        """
        return cast("int", self.cmp.layout.ncol)

    @property
    def nrow(self) -> int:
        """
        Number of rows
        """
        return cast("int", self.cmp.layout.nrow)

    @staticmethod
    def create(cmp: Compose) -> LayoutTree:
        """
        Create a LayoutTree for this composition

        Parameters
        ----------
        cmp :
            Composition
        """
        from plotnine import ggplot

        # Create subtree
        nodes: list[PlotSideSpaces | LayoutTree] = []
        for item in cmp:
            if isinstance(item, ggplot):
                nodes.append(item._sidespaces)
            else:
                nodes.append(LayoutTree.create(item))

        return LayoutTree(cmp, nodes)

    @cached_property
    def sub_compositions(self) -> list[LayoutTree]:
        """
        LayoutTrees of the direct sub compositions of this one
        """
        return [item for item in self.nodes if isinstance(item, LayoutTree)]

    def arrange_layout(self):
        """
        Align and resize plots in composition to look good

        Aligning changes the *_alignment attributes of the side_spaces.
        Resizing, changes the parameters of the sub_gridspec.

        Note that we expect that this method will be called only on the
        tree for the top-level composition, and it is called for its
        side-effects.
        """
        self.align_axis_titles()
        self.align()
        self.resize()

    def align(self):
        """
        Align all the edges in this composition & contained compositions

        This function mutates the layout spaces, specifically the
        margin_alignments along the sides of the plot.
        """
        self.align_tags()
        self.align_panels()
        self.align_sub_compositions()

    def resize(self):
        """
        Resize panels and the entire plots

        This function mutates the composition gridspecs; specifically the
        width_ratios and height_ratios.
        """
        self.resize_widths()
        self.resize_heights()
        self.resize_sub_compositions()

    def align_sub_compositions(self):
        """
        Align the compositions contained in this one
        """
        # Recurse into the contained compositions
        for tree in self.sub_compositions:
            tree.align()

    def resize_sub_compositions(self):
        """
        Resize panels in the compositions contained in this one
        """
        for tree in self.sub_compositions:
            tree.resize()

    @cached_property
    def bottom_most_spaces(self) -> list[bottom_space]:
        """
        Bottom spaces of items in the last row
        """
        return [s for s in self.bottom_spaces_in_row(self.nrow - 1)]

    @cached_property
    def top_most_spaces(self) -> list[top_space]:
        """
        Top spaces of items in the top row
        """
        return [s for s in self.top_spaces_in_row(0)]

    @cached_property
    def left_most_spaces(self) -> list[left_space]:
        """
        Left spaces of items in the last column
        """
        return [s for s in self.left_spaces_in_col(0)]

    @cached_property
    def right_most_spaces(self) -> list[right_space]:
        """
        Right spaces of items the last column
        """
        return [s for s in self.right_spaces_in_col(self.ncol - 1)]

    @property
    def panel_width(self) -> float:
        """
        A width of all panels in this composition
        """
        return sum(self.panel_widths)

    @property
    def panel_height(self) -> float:
        """
        A height of all panels in this composition
        """
        return sum(self.panel_heights)

    @property
    def plot_width(self) -> float:
        """
        A width of all plots in this tree/composition
        """
        return self.sub_gridspec.width

    @property
    def plot_height(self) -> float:
        """
        A height of all plots in this tree/composition
        """
        return self.sub_gridspec.height

    @property
    def horizontal_space(self) -> float:
        """
        Horizontal non-panel space in this composition
        """
        return sum(self.horizontal_spaces)

    @property
    def vertical_space(self) -> float:
        """
        Vertical non-panel space in this composition
        """
        return sum(self.vertical_spaces)

    @property
    def horizontal_spaces(self) -> Sequence[float]:
        """
        Horizontal non-panel space by column

        For each column, the representative number for the horizontal
        space to left & right of the widest panel.
        """
        return list(np.array(self.plot_widths) - self.panel_widths)

    @property
    def vertical_spaces(self) -> Sequence[float]:
        """
        Vertical non-panel space by row

        For each row, the representative number for the vertical
        space is above & below the tallest panel.
        """
        return list(np.array(self.plot_heights) - self.panel_heights)

    @property
    def panel_widths(self) -> Sequence[float]:
        """
        Widths [figure space] of panels by column

        For each column, the representative number for the panel width
        is the maximum width among all panels in the column.
        """
        # This method is used after aligning the panels. Therefore, the
        # wides panel_width (i.e. max()) is the good representative width
        # of the column.
        w = self.plot_width / self.ncol
        return [
            max(node.panel_width for node in col if node) if any(col) else w
            for col in self.grid.iter_cols()
        ]

    @property
    def panel_heights(self) -> Sequence[float]:
        """
        Heights [figure space] of panels by row

        For each row, the representative number for the panel height
        is the maximum height among all panels in the row.
        """
        h = self.plot_height / self.nrow
        return [
            max([node.panel_height for node in row if node]) if any(row) else h
            for row in self.grid.iter_rows()
        ]

    @property
    def plot_widths(self) -> Sequence[float]:
        """
        Widths [figure space] of the plots by column

        For each column, the representative number is the width of
        the widest plot.
        """
        w = self.sub_gridspec.width / self.ncol
        return [
            max([node.plot_width if node else w for node in col])
            for col in self.grid.iter_cols()
        ]

    @property
    def plot_heights(self) -> Sequence[float]:
        """
        Heights [figure space] of the plots along vertical dimension

        For each row, the representative number is the height of
        the tallest plot.
        """
        h = self.sub_gridspec.height / self.nrow
        return [
            max([node.plot_height if node else h for node in row])
            for row in self.grid.iter_rows()
        ]

    @property
    def panel_width_ratios(self) -> Sequence[float]:
        """
        The relative widths of the panels in the composition

        These are normalised to have a mean = 1.
        """
        return cast("Sequence[float]", self.cmp._layout.widths)

    @property
    def panel_height_ratios(self) -> Sequence[float]:
        """
        The relative heights of the panels in the composition

        These are normalised to have a mean = 1.
        """
        return cast("Sequence[float]", self.cmp._layout.heights)

    def bottom_spaces_in_row(self, r: int) -> list[bottom_space]:
        """
        The bottom_spaces of plots in a given row

        If an item in the row is a compositions, then it is the
        bottom_spaces in the bottom row of that composition.
        """
        spaces: list[bottom_space] = []
        for node in self.grid[r, :]:
            if isinstance(node, PlotSideSpaces):
                spaces.append(node.b)
            elif isinstance(node, LayoutTree):
                spaces.extend(node.bottom_most_spaces)
        return spaces

    def top_spaces_in_row(self, r: int) -> list[top_space]:
        """
        The top_spaces of plots in a given row

        If an item in the row is a compositions, then it is the
        top_spaces in the top row of that composition.
        """
        spaces: list[top_space] = []
        for node in self.grid[r, :]:
            if isinstance(node, PlotSideSpaces):
                spaces.append(node.t)
            elif isinstance(node, LayoutTree):
                spaces.extend(node.top_most_spaces)
        return spaces

    def left_spaces_in_col(self, c: int) -> list[left_space]:
        """
        The left_spaces plots in a given column

        If an item in the column is a compositions, then it is the
        left_spaces in the left most column of that composition.
        """
        spaces: list[left_space] = []
        for node in self.grid[:, c]:
            if isinstance(node, PlotSideSpaces):
                spaces.append(node.l)
            elif isinstance(node, LayoutTree):
                spaces.extend(node.left_most_spaces)
        return spaces

    def right_spaces_in_col(self, c: int) -> list[right_space]:
        """
        The right_spaces of plots in a given column

        If an item in the column is a compositions, then it is the
        right_spaces in the right most column of that composition.
        """
        spaces: list[right_space] = []
        for node in self.grid[:, c]:
            if isinstance(node, PlotSideSpaces):
                spaces.append(node.r)
            elif isinstance(node, LayoutTree):
                spaces.extend(node.right_most_spaces)
        return spaces

    @property
    def left_spaces(self) -> Iterator[list[left_space]]:
        """
        Left spaces for each non-empty column

        Will not return an empty list.
        """
        for c in range(self.ncol):
            spaces = self.left_spaces_in_col(c)
            if spaces:
                yield spaces

    @property
    def right_spaces(self) -> Iterator[list[right_space]]:
        """
        Right spaces for each non-empty column

        Will not return an empty list.
        """
        for c in range(self.ncol):
            spaces = self.right_spaces_in_col(c)
            if spaces:
                yield spaces

    @property
    def bottom_spaces(self) -> Iterator[list[bottom_space]]:
        """
        Bottom spaces for each non-empty row

        Will not return an empty list.
        """
        for r in range(self.nrow):
            spaces = self.bottom_spaces_in_row(r)
            if spaces:
                yield spaces

    @property
    def top_spaces(self) -> Iterator[list[top_space]]:
        """
        Top spaces for each non-empty row

        Will not return an empty list.
        """
        for r in range(self.nrow):
            spaces = self.top_spaces_in_row(r)
            if spaces:
                yield spaces

    def align_panels(self):
        """
        Align the edges of the panels in the composition
        """
        align_args = [
            (self.bottom_spaces, lambda s: s.panel_bottom, "max"),
            (self.top_spaces, lambda s: s.panel_top, "min"),
            (self.left_spaces, lambda s: s.panel_left, "max"),
            (self.right_spaces, lambda s: s.panel_right, "min"),
        ]
        for spaces, measure, how in align_args:
            _align(spaces, measure, "margin_alignment", how)

    def align_tags(self):
        """
        Align the tags in the composition
        """
        align_args = [
            (self.bottom_spaces, lambda s: s.tag_height + s.tag_alignment),
            (self.top_spaces, lambda s: s.tag_height + s.tag_alignment),
            (self.left_spaces, lambda s: s.tag_width + s.tag_alignment),
            (self.right_spaces, lambda s: s.tag_width + s.tag_alignment),
        ]
        for spaces, measure in align_args:
            _align(spaces, measure, "tag_alignment")

    def align_axis_titles(self):
        """
        Align the axis titles along the composing dimension

        Since the alignment value used to for this purpose is one of
        the fields in the _side_space, it affects the space created
        for the panel.

        We could align the titles within self.align but we would have
        to store the value outside the _side_space and pick it up when
        setting the position of the texts!
        """

        def axis_title_clearance(s):
            return s.axis_title_clearance

        for spaces in [self.bottom_spaces, self.left_spaces]:
            _align(spaces, axis_title_clearance, "axis_title_alignment")

        for tree in self.sub_compositions:
            tree.align_axis_titles()

    def resize_widths(self):
        """
        Resize the widths of the plots & panels in the composition
        """
        # The scaling calculation to get the new panel width is
        # straight-forward because the ratios have a mean of 1.
        # So the multiplication preserves the total panel width.
        new_panel_widths = np.mean(self.panel_widths) * np.array(
            self.panel_width_ratios
        )
        new_plot_widths = new_panel_widths + self.horizontal_spaces
        width_ratios = new_plot_widths / new_plot_widths.max()
        self.sub_gridspec.set_width_ratios(width_ratios)

    def resize_heights(self):
        """
        Resize the heights of the plots & panels in the composition
        """
        new_panel_heights = np.mean(self.panel_heights) * np.array(
            self.panel_height_ratios
        )
        new_plot_heights = new_panel_heights + self.vertical_spaces
        height_ratios = new_plot_heights / new_plot_heights.max()
        self.sub_gridspec.set_height_ratios(height_ratios)


def _align(
    spaces_iter: Iterator[Sequence[Any]],
    measure: Callable[[Any], float],
    attr: str,
    how: Literal["max", "min"] = "max",
):
    """
    Align spaces by adjusting an attribute

    For each group of spaces yielded by the iterator, find the extreme
    value (max or min) of the measurement, then add the difference to
    each space's alignment attribute so that all spaces in the group end
    up with the same measurement.

    Parameters
    ----------
    spaces_iter
        Iterator yielding groups of side spaces to equalize.
        Each group is a sequence of spaces along the same row or column of
        the composition.
    measure
        Function that extracts the value to equalize from a side space.
    attr
        Name of the alignment attribute on the side space to adjust.
        The difference is added to the current value.
    how
        Whether to equalize to the maximum or minimum value in each group.
        For "max", spaces with smaller measurements get extra alignment to
        match the largest.
        For "min", spaces with larger measurements get extra alignment to
        match the smallest.
    """
    for spaces in spaces_iter:
        values = [measure(s) for s in spaces]
        if how == "max":
            target = max(values)
            diffs = [target - v for v in values]
        else:
            target = min(values)
            diffs = [v - target for v in values]
        for space, diff in zip(spaces, diffs):
            setattr(space, attr, getattr(space, attr) + diff)


# For debugging
def _draw_gridspecs(tree: LayoutTree):
    from ..utils import draw_bbox

    def draw(t):
        draw_bbox(
            t.cmp._gridspec.bbox_relative,
            t.cmp._gridspec.figure,
        )
        for subtree in t.sub_compositions:
            draw(subtree)

    draw(tree)


def _draw_sub_gridspecs(tree: LayoutTree):
    from ..utils import draw_bbox

    def draw(t):
        draw_bbox(
            t.sub_gridspec.bbox_relative,
            t.sub_gridspec.figure,
        )
        for subtree in t.sub_compositions:
            draw(subtree)

    draw(tree)

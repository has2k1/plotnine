from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING, Iterator, cast

import numpy as np

from ._grid import Grid
from ._spaces import (
    LayoutSpaces,
    bottom_spaces,
    left_spaces,
    right_spaces,
    top_spaces,
)

if TYPE_CHECKING:
    from typing import Sequence, TypeAlias

    from plotnine import ggplot
    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine._mpl.layout_manager._spaces import (
        bottom_spaces,
        left_spaces,
        right_spaces,
        top_spaces,
    )
    from plotnine.composition import Compose

    Node: TypeAlias = "LayoutSpaces | LayoutTree"


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
    """

    cmp: Compose
    """
    Composition that this tree represents
    """

    nodes: list[LayoutSpaces | LayoutTree]
    """
    The spaces or tree of spaces in the composition that the tree
    represents.
    """

    gridspec: p9GridSpec = field(init=False, repr=False)
    """
    Gridspec of the composition

    Originally this gridspec occupies all the space available to it so the
    subplots are of equal sizes. As each subplot contains full ggplot,
    differences in texts and legend sizes may make the panels (panel area)
    have unequal sizes. We can resize the panels, by changing the height
    and width ratios of this (composition) gridspec.

    The information about the size (width & height) of the panels is in the
    LayoutSpaces.
    """

    def __post_init__(self):
        self.gridspec = self.cmp.gridspec
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
    def create(
        cmp: Compose,
        lookup_spaces: dict[ggplot, LayoutSpaces],
    ) -> LayoutTree:
        """
        Create a LayoutTree for this composition

        Parameters
        ----------
        cmp :
            Composition
        lookup_spaces :
            A table to lookup the LayoutSpaces for each plot.

        Notes
        -----
        LayoutTree works by modifying the `.gridspec` of the compositions,
        and the `LayoutSpaces` of the plots.
        """
        from plotnine import ggplot

        # Create subtree
        nodes: list[LayoutSpaces | LayoutTree] = []
        for item in cmp:
            if isinstance(item, ggplot):
                nodes.append(lookup_spaces[item])
            else:
                nodes.append(LayoutTree.create(item, lookup_spaces))

        return LayoutTree(cmp, nodes)

    @cached_property
    def sub_compositions(self) -> list[LayoutTree]:
        """
        LayoutTrees of the direct sub compositions of this one
        """
        return [item for item in self.nodes if isinstance(item, LayoutTree)]

    def harmonise(self):
        """
        Align and resize plots in composition to look good
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
    def bottom_most_spaces(self) -> list[bottom_spaces]:
        """
        Bottom spaces of items in the last row
        """
        return [s for s in self.bottom_spaces_in_row(self.nrow - 1)]

    @cached_property
    def top_most_spaces(self) -> list[top_spaces]:
        """
        Top spaces of items in the top row
        """
        return [s for s in self.top_spaces_in_row(0)]

    @cached_property
    def left_most_spaces(self) -> list[left_spaces]:
        """
        Left spaces of items in the last column
        """
        return [s for s in self.left_spaces_in_col(0)]

    @cached_property
    def right_most_spaces(self) -> list[right_spaces]:
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
        return self.gridspec.width

    @property
    def plot_height(self) -> float:
        """
        A height of all plots in this tree/composition
        """
        return self.gridspec.height

    @property
    def panel_widths(self) -> Sequence[float]:
        """
        Widths [figure space] of the panels along horizontal dimension
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
        Heights [figure space] of the panels along vertical dimension
        """
        h = self.plot_height / self.nrow
        return [
            max([node.panel_height for node in row if node]) if any(row) else h
            for row in self.grid.iter_rows()
        ]

    @property
    def plot_widths(self) -> Sequence[float]:
        """
        Widths [figure space] of the plots along horizontal dimension

        For each column, the representative width is that of the widest plot.
        """
        w = self.gridspec.width / self.ncol
        return [
            max([node.plot_width if node else w for node in col])
            for col in self.grid.iter_cols()
        ]

    @property
    def plot_heights(self) -> Sequence[float]:
        """
        Heights [figure space] of the plots along vertical dimension

        For each row, the representative height is that of the tallest plot.
        """
        h = self.gridspec.height / self.nrow
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

    def bottom_spaces_in_row(self, r: int) -> list[bottom_spaces]:
        spaces: list[bottom_spaces] = []
        for node in self.grid[r, :]:
            if isinstance(node, LayoutSpaces):
                spaces.append(node.b)
            elif isinstance(node, LayoutTree):
                spaces.extend(node.bottom_most_spaces)
        return spaces

    def top_spaces_in_row(self, r: int) -> list[top_spaces]:
        spaces: list[top_spaces] = []
        for node in self.grid[r, :]:
            if isinstance(node, LayoutSpaces):
                spaces.append(node.t)
            elif isinstance(node, LayoutTree):
                spaces.extend(node.top_most_spaces)
        return spaces

    def left_spaces_in_col(self, c: int) -> list[left_spaces]:
        spaces: list[left_spaces] = []
        for node in self.grid[:, c]:
            if isinstance(node, LayoutSpaces):
                spaces.append(node.l)
            elif isinstance(node, LayoutTree):
                spaces.extend(node.left_most_spaces)
        return spaces

    def right_spaces_in_col(self, c: int) -> list[right_spaces]:
        spaces: list[right_spaces] = []
        for node in self.grid[:, c]:
            if isinstance(node, LayoutSpaces):
                spaces.append(node.r)
            elif isinstance(node, LayoutTree):
                spaces.extend(node.right_most_spaces)
        return spaces

    def iter_left_spaces(self) -> Iterator[list[left_spaces]]:
        """
        Left spaces for each non-empty column

        Will not return an empty list.
        """
        for c in range(self.ncol):
            spaces = self.left_spaces_in_col(c)
            if spaces:
                yield spaces

    def iter_right_spaces(self) -> Iterator[list[right_spaces]]:
        """
        Right spaces for each non-empty column

        Will not return an empty list.
        """
        for c in range(self.ncol):
            spaces = self.right_spaces_in_col(c)
            if spaces:
                yield spaces

    def iter_bottom_spaces(self) -> Iterator[list[bottom_spaces]]:
        """
        Bottom spaces for each non-empty row
        """
        for r in range(self.nrow):
            spaces = self.bottom_spaces_in_row(r)
            if spaces:
                yield spaces

    def iter_top_spaces(self) -> Iterator[list[top_spaces]]:
        """
        Top spaces for each non-empty row
        """
        for r in range(self.nrow):
            spaces = self.top_spaces_in_row(r)
            if spaces:
                yield spaces

    def align_panels(self):
        for spaces in self.iter_bottom_spaces():
            bottoms = [space.panel_bottom for space in spaces]
            high = max(bottoms)
            diffs = [high - b for b in bottoms]
            for space, diff in zip(spaces, diffs):
                space.margin_alignment += diff

        for spaces in self.iter_top_spaces():
            tops = [space.panel_top for space in spaces]
            low = min(tops)
            diffs = [b - low for b in tops]
            for space, diff in zip(spaces, diffs):
                space.margin_alignment += diff

        for spaces in self.iter_left_spaces():
            lefts = [space.panel_left for space in spaces]
            high = max(lefts)
            diffs = [high - l for l in lefts]
            for space, diff in zip(spaces, diffs):
                space.margin_alignment += diff

        for spaces in self.iter_right_spaces():
            rights = [space.panel_right for space in spaces]
            low = min(rights)
            diffs = [r - low for r in rights]
            for space, diff in zip(spaces, diffs):
                space.margin_alignment += diff

    def align_tags(self):
        for spaces in self.iter_bottom_spaces():
            heights = [
                space.tag_height + space.tag_alignment for space in spaces
            ]
            high = max(heights)
            diffs = [high - h for h in heights]
            for space, diff in zip(spaces, diffs):
                space.tag_alignment += diff

        for spaces in self.iter_top_spaces():
            heights = [
                space.tag_height + space.tag_alignment for space in spaces
            ]
            high = max(heights)
            diffs = [high - h for h in heights]
            for space, diff in zip(spaces, diffs):
                space.tag_alignment += diff

        for spaces in self.iter_left_spaces():
            widths = [
                space.tag_width + space.tag_alignment for space in spaces
            ]
            high = max(widths)
            diffs = [high - w for w in widths]
            for space, diff in zip(spaces, diffs):
                space.tag_alignment += diff

        for spaces in self.iter_right_spaces():
            widths = [
                space.tag_width + space.tag_alignment for space in spaces
            ]
            high = max(widths)
            diffs = [high - w for w in widths]
            for space, diff in zip(spaces, diffs):
                space.tag_alignment += diff

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

        for spaces in self.iter_bottom_spaces():
            clearances = [space.axis_title_clearance for space in spaces]
            high = max(clearances)
            diffs = [high - b for b in clearances]
            for space, diff in zip(spaces, diffs):
                space.axis_title_alignment += diff

        for spaces in self.iter_left_spaces():
            clearances = [space.axis_title_clearance for space in spaces]
            high = max(clearances)
            diffs = [high - l for l in clearances]
            for space, diff in zip(spaces, diffs):
                space.axis_title_alignment += diff

        for tree in self.sub_compositions:
            tree.align_axis_titles()

    def resize_widths(self):
        # The scaling calcuation to get the new panel width is
        # straight-forward because the ratios have a mean of 1.
        # So the multiplication preserves the total panel width.
        new_panel_widths = np.mean(self.panel_widths) * np.array(
            self.panel_width_ratios
        )
        non_panel_space = np.array(self.plot_widths) - self.panel_widths
        new_plot_widths = new_panel_widths + non_panel_space
        width_ratios = new_plot_widths / new_plot_widths.max()
        self.gridspec.set_width_ratios(width_ratios)

    def resize_heights(self):
        new_panel_heights = np.mean(self.panel_heights) * np.array(
            self.panel_height_ratios
        )
        non_panel_space = np.array(self.plot_heights) - self.panel_heights
        new_plot_heights = new_panel_heights + non_panel_space
        height_ratios = new_plot_heights / new_plot_heights.max()
        self.gridspec.set_height_ratios(height_ratios)

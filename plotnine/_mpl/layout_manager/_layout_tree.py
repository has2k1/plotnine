from __future__ import annotations

import abc
from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING, Iterator

import numpy as np

from plotnine.composition import Beside
from plotnine.composition._stack import Stack

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
    and resize plots in a composition.

    For example, this composition;

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

                         ColumnsTree
                             |
               ----------------------------
              |              |             |
        LayoutSpaces    LayoutSpaces   RowsTree
                                           |
                                      -------------
                                     |             |
                               LayoutSpaces  LayoutSpaces

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

    gridspec: p9GridSpec = field(init=False)
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

        # Create root
        if isinstance(cmp, Beside):
            return ColumnsTree(cmp, nodes)
        elif isinstance(cmp, Stack):
            return RowsTree(cmp, nodes)
        else:
            return GridTree(cmp, nodes)

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

    @abc.abstractmethod
    def align(self):
        """
        Align all the edges in this composition & contained compositions

        This function mutates the layout spaces, specifically the
        margin_alignments along the sides of the plot.
        """

    @abc.abstractmethod
    def resize(self):
        """
        Resize panels and the entire plots

        This function mutates the composition gridspecs; specifically the
        width_ratios and height_ratios.
        """

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
    @abc.abstractmethod
    def bottom_spaces_to_align(self) -> list[bottom_spaces]:
        """
        Bottom spaces to align in this composition
        """

    @cached_property
    @abc.abstractmethod
    def top_spaces_to_align(self) -> list[top_spaces]:
        """
        Top spaces to align in this composition
        """

    @cached_property
    @abc.abstractmethod
    def left_spaces_to_align(self) -> list[left_spaces]:
        """
        Left spaces to align in this composition
        """

    @cached_property
    @abc.abstractmethod
    def right_spaces_to_align(self) -> list[right_spaces]:
        """
        Right spaces to align in this composition
        """

    @abc.abstractmethod
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

    @property
    @abc.abstractmethod
    def panel_width(self) -> float:
        """
        A representative width for panels of the nodes
        """

    @property
    @abc.abstractmethod
    def panel_height(self) -> float:
        """
        A representative height for panels of the nodes
        """

    @property
    @abc.abstractmethod
    def plot_width(self) -> float:
        """
        A representative width for plots of the nodes
        """

    @property
    @abc.abstractmethod
    def plot_height(self) -> float:
        """
        A representative for height for plots of the nodes
        """

    @property
    def panel_widths(self) -> Sequence[float]:
        """
        Widths [figure space] of the panels in this tree
        """
        return [node.panel_width for node in self.nodes]

    @property
    def panel_heights(self) -> Sequence[float]:
        """
        Heights [figure space] of the panels in this tree
        """
        return [node.panel_height for node in self.nodes]

    @property
    def plot_widths(self) -> Sequence[float]:
        """
        Widths [figure space] of nodes in this tree
        """
        return [node.plot_width for node in self.nodes]

    @property
    def plot_heights(self) -> Sequence[float]:
        """
        Heights [figure space] of nodes in this tree
        """
        return [node.plot_height for node in self.nodes]

    @property
    def total_panel_width(self) -> float:
        return sum(self.panel_widths)

    @property
    def total_panel_height(self) -> float:
        return sum(self.panel_heights)


@dataclass
class ColumnsTree(LayoutTree):
    """
    Tree with columns at the outermost level

    e.g. p1 | (p2 / p3)


         -------------------
        |         |         |
        |         |         |
        |         |         |
        |         |         |
        |         |---------|
        |         |         |
        |         |         |
        |         |         |
        |         |         |
         -------------------
    """

    def align(self):
        self.align_top_tags()
        self.align_bottom_tags()
        self.align_panel_bottoms()
        self.align_panel_tops()
        self.align_sub_compositions()

    def align_axis_titles(self):
        self.align_bottom_axis_titles()
        for tree in self.sub_compositions:
            tree.align_axis_titles()

    def resize(self):
        """
        Resize the widths of gridspec so that panels have equal widths
        """
        # The new width of each panel is the total panel area scaled
        # by the factor given in plot_layout.
        # The new width of the plot includes the space not taken up
        # by the panels.
        n = len(self.panel_widths)
        factors = np.array(self.cmp._plot_layout.widths)
        _totals = np.ones(n) * self.total_panel_width
        scaled_panel_widths = _totals * factors
        non_panel_space = np.array(self.plot_widths) - self.panel_widths
        new_plot_widths = scaled_panel_widths + non_panel_space
        width_ratios = new_plot_widths / new_plot_widths.max()
        self.gridspec.set_width_ratios(width_ratios)
        self.resize_sub_compositions()

    @cached_property
    def bottom_spaces_to_align(self):
        spaces: list[bottom_spaces] = []
        for node in self.nodes:
            if isinstance(node, LayoutSpaces):
                spaces.append(node.b)
            else:
                spaces.extend(node.bottom_spaces_to_align)
        return spaces

    @cached_property
    def top_spaces_to_align(self):
        spaces: list[top_spaces] = []
        for node in self.nodes:
            if isinstance(node, LayoutSpaces):
                spaces.append(node.t)
            else:
                spaces.extend(node.top_spaces_to_align)
        return spaces

    @cached_property
    def left_spaces_to_align(self):
        left_node = self.nodes[0]
        if isinstance(left_node, LayoutSpaces):
            return [left_node.l]
        else:
            return left_node.left_spaces_to_align

    @cached_property
    def right_spaces_to_align(self):
        right_node = self.nodes[-1]
        if isinstance(right_node, LayoutSpaces):
            return [right_node.r]
        else:
            return right_node.right_spaces_to_align

    def align_panel_bottoms(self):
        """
        Align the bottom edges

         -----------        -----------
        |     |     |      |     |     |
        |     |     |      |     |     |
        |     |     |  ->  |     |     |
        |     |#####|      |#####|#####|
        |#####|     |      |     |     |
         -----------        -----------
        """
        spaces = self.bottom_spaces_to_align
        bottoms = [space.panel_bottom for space in spaces]
        high = max(bottoms)
        diffs = [high - b for b in bottoms]
        for space, diff in zip(spaces, diffs):
            space.margin_alignment += diff

    def align_panel_tops(self):
        spaces = self.top_spaces_to_align
        """
        Align the top edges

         -----------        -----------
        |#####|     |      |     |     |
        |     |#####|      |#####|#####|
        |     |     |  ->  |     |     |
        |     |     |      |     |     |
        |     |     |      |     |     |
         -----------        -----------
        """
        tops = [space.panel_top for space in spaces]
        low = min(tops)
        diffs = [b - low for b in tops]
        for space, diff in zip(spaces, diffs):
            space.margin_alignment += diff

    def align_bottom_axis_titles(self):
        spaces = self.bottom_spaces_to_align
        clearances = [space.axis_title_clearance for space in spaces]
        high = max(clearances)
        diffs = [high - b for b in clearances]
        for space, diff in zip(spaces, diffs):
            space.axis_title_alignment += diff

    def align_bottom_tags(self):
        spaces = self.bottom_spaces_to_align
        heights = [space.tag_height + space.tag_alignment for space in spaces]
        high = max(heights)
        diffs = [high - h for h in heights]
        for space, diff in zip(spaces, diffs):
            space.tag_alignment += diff

    def align_top_tags(self):
        spaces = self.top_spaces_to_align
        heights = [space.tag_height + space.tag_alignment for space in spaces]
        high = max(heights)
        diffs = [high - h for h in heights]
        for space, diff in zip(spaces, diffs):
            space.tag_alignment += diff

    @property
    def panel_width(self) -> float:
        return sum(self.panel_widths)

    @property
    def panel_height(self) -> float:
        return float(np.mean(self.panel_heights))

    @property
    def plot_width(self) -> float:
        return sum(self.plot_widths)

    @property
    def plot_height(self) -> float:
        return max(self.plot_heights)


@dataclass
class RowsTree(LayoutTree):
    """
    Tree with rows at the outermost level

    e.g. p1 / (p2 | p3)

         -------------------
        |                   |
        |                   |
        |                   |
        |-------------------|
        |         |         |
        |         |         |
        |         |         |
         -------------------
    """

    def align(self):
        self.align_left_tags()
        self.align_right_tags()
        self.align_panel_lefts()
        self.align_panel_rights()
        self.align_sub_compositions()

    def align_axis_titles(self):
        self.align_left_axis_titles()
        for tree in self.sub_compositions:
            tree.align_axis_titles()

    def resize(self):
        """
        Resize the heights of gridspec so that panels have equal heights

        This method resizes (recursively) the contained compositions
        """
        # The new height of each panel is the total panel area scaled
        # by the factor given in plot_layout.
        # The new height of the plot includes the space not taken up
        # by the panels.
        n = len(self.panel_heights)
        factors = np.array(self.cmp._plot_layout.heights)
        _totals = np.ones(n) * self.total_panel_height
        scaled_panel_heights = _totals * factors
        non_panel_space = np.array(self.plot_heights) - self.panel_heights
        new_plot_heights = scaled_panel_heights + non_panel_space
        height_ratios = new_plot_heights / new_plot_heights.max()
        self.gridspec.set_height_ratios(height_ratios)
        self.resize_sub_compositions()

    @cached_property
    def bottom_spaces_to_align(self):
        bottom_node = self.nodes[-1]
        if isinstance(bottom_node, LayoutSpaces):
            return [bottom_node.b]
        else:
            return bottom_node.bottom_spaces_to_align

    @cached_property
    def top_spaces_to_align(self):
        top_node = self.nodes[0]
        if isinstance(top_node, LayoutSpaces):
            return [top_node.t]
        else:
            return top_node.top_spaces_to_align

    @cached_property
    def left_spaces_to_align(self):
        spaces: list[left_spaces] = []
        for node in self.nodes:
            if isinstance(node, LayoutSpaces):
                spaces.append(node.l)
            else:
                spaces.extend(node.left_spaces_to_align)
        return spaces

    @cached_property
    def right_spaces_to_align(self):
        spaces: list[right_spaces] = []
        for node in self.nodes:
            if isinstance(node, LayoutSpaces):
                spaces.append(node.r)
            else:
                spaces.extend(node.right_spaces_to_align)
        return spaces

    def align_panel_lefts(self):
        """
        Align the left edges

         -----------        -----------
        |#          |      |  #        |
        |#          |      |  #        |
        |#          |      |  #        |
        |-----------|  ->  |-----------|
        |  #        |      |  #        |
        |  #        |      |  #        |
        |  #        |      |  #        |
         -----------        -----------
        """
        spaces = self.left_spaces_to_align
        lefts = [space.panel_left for space in spaces]
        high = max(lefts)
        diffs = [high - l for l in lefts]
        for space, diff in zip(spaces, diffs):
            space.margin_alignment += diff

    def align_panel_rights(self):
        """
        Align the right edges

         -----------        -----------
        |        #  |      |        #  |
        |        #  |      |        #  |
        |        #  |      |        #  |
        |-----------|  ->  |-----------|
        |          #|      |        #  |
        |          #|      |        #  |
        |          #|      |        #  |
         -----------        -----------
        """
        spaces = self.right_spaces_to_align
        rights = [space.panel_right for space in spaces]
        low = min(rights)
        diffs = [r - low for r in rights]
        for space, diff in zip(spaces, diffs):
            space.margin_alignment += diff

    def align_left_axis_titles(self):
        spaces = self.left_spaces_to_align
        clearances = [space.axis_title_clearance for space in spaces]
        high = max(clearances)
        diffs = [high - l for l in clearances]
        for space, diff in zip(spaces, diffs):
            space.axis_title_alignment += diff

    def align_left_tags(self):
        spaces = self.left_spaces_to_align
        widths = [space.tag_width + space.tag_alignment for space in spaces]
        high = max(widths)
        diffs = [high - w for w in widths]
        for space, diff in zip(spaces, diffs):
            space.tag_alignment += diff

    def align_right_tags(self):
        spaces = self.right_spaces_to_align
        widths = [space.tag_width + space.tag_alignment for space in spaces]
        high = max(widths)
        diffs = [high - w for w in widths]
        for space, diff in zip(spaces, diffs):
            space.tag_alignment += diff

    @property
    def panel_width(self) -> float:
        return float(np.mean(self.panel_widths))

    @property
    def panel_height(self) -> float:
        return sum(self.panel_heights)

    @property
    def plot_width(self) -> float:
        return max(self.plot_widths)

    @property
    def plot_height(self) -> float:
        return sum(self.plot_heights)


@dataclass
class GridTree(LayoutTree):
    """
    Tree with a grid of at the top level

    e.g. p1 + p2 + p3 + p4 + p5

         --------------------------
        |        |        |        |
        |   p1   |   p2   |   p3   |
        |        |        |        |
        |--------------------------|
        |        |        |        |
        |   p4   |   p5   |        |
        |        |        |        |
         --------------------------

    More accurately this is a grid of trees.
    """

    def __post_init__(self):
        super().__post_init__()
        self.ncol = self.cmp.ncol
        self.nrow = self.cmp.nrow
        self.grid = Grid["Node"](self.nrow, self.ncol, self.nodes)

    def align(self):
        self.align_tags()
        self.align_panels()
        self.align_sub_compositions()

    def resize(self):
        """
        Resize all squares of the grid
        """
        self.resize_widths()
        self.resize_heights()
        self.resize_sub_compositions()

    @property
    def panel_width(self) -> float:
        return sum(self.panel_widths)

    @property
    def panel_height(self) -> float:
        return sum(self.panel_heights)

    @property
    def plot_width(self) -> float:
        return sum(self.plot_widths)

    @property
    def plot_height(self) -> float:
        return sum(self.plot_heights)

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

    @cached_property
    def bottom_spaces_to_align(self) -> list[bottom_spaces]:
        """
        Bottom spaces of items in the last row
        """
        return [s for s in self.bottom_spaces_in_row(self.nrow - 1)]

    @cached_property
    def top_spaces_to_align(self) -> list[top_spaces]:
        """
        Top spaces of items in the top row
        """
        return [s for s in self.top_spaces_in_row(0)]

    @cached_property
    def left_spaces_to_align(self) -> list[left_spaces]:
        """
        Left spaces of items in the last column
        """
        return [s for s in self.left_spaces_in_col(0)]

    @cached_property
    def right_spaces_to_align(self) -> list[right_spaces]:
        """
        Right spaces of items the last column
        """
        return [s for s in self.right_spaces_in_col(self.ncol - 1)]

    def bottom_spaces_in_row(self, r: int) -> list[bottom_spaces]:
        spaces: list[bottom_spaces] = []
        for node in self.grid[r, :]:
            if isinstance(node, LayoutSpaces):
                spaces.append(node.b)
            elif isinstance(node, LayoutTree):
                spaces.extend(node.bottom_spaces_to_align)
        return spaces

    def top_spaces_in_row(self, r: int) -> list[top_spaces]:
        spaces: list[top_spaces] = []
        for node in self.grid[r, :]:
            if isinstance(node, LayoutSpaces):
                spaces.append(node.t)
            elif isinstance(node, LayoutTree):
                spaces.extend(node.top_spaces_to_align)
        return spaces

    def left_spaces_in_col(self, c: int) -> list[left_spaces]:
        spaces: list[left_spaces] = []
        for node in self.grid[:, c]:
            if isinstance(node, LayoutSpaces):
                spaces.append(node.l)
            elif isinstance(node, LayoutTree):
                spaces.extend(node.left_spaces_to_align)
        return spaces

    def right_spaces_in_col(self, c: int) -> list[right_spaces]:
        spaces: list[right_spaces] = []
        for node in self.grid[:, c]:
            if isinstance(node, LayoutSpaces):
                spaces.append(node.r)
            elif isinstance(node, LayoutTree):
                spaces.extend(node.right_spaces_to_align)
        return spaces

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
        n = self.ncol
        panel_widths = np.array(
            [
                max([node.panel_width if node else 0 for node in col])
                for col in self.grid.iter_cols()
            ]
        )
        plot_widths = np.ones(n) * 1 / n
        total_panel_width = sum(panel_widths)
        factors = np.array(self.cmp._plot_layout.widths)
        _totals = np.ones(n) * total_panel_width
        scaled_panel_widths = _totals * factors
        non_panel_space = plot_widths - panel_widths
        new_plot_widths = scaled_panel_widths + non_panel_space
        width_ratios = new_plot_widths / new_plot_widths.max()
        self.gridspec.set_width_ratios(width_ratios)

    def resize_heights(self):
        n = self.nrow
        panel_heights = np.array(
            [
                max([node.panel_height if node else 0 for node in col])
                for col in self.grid.iter_rows()
            ]
        )
        plot_heights = np.ones(n) * 1 / n
        total_panel_height = sum(panel_heights)
        factors = np.array(self.cmp._plot_layout.heights)
        _totals = np.ones(n) * total_panel_height
        scaled_panel_heights = _totals * factors
        non_panel_space = plot_heights - panel_heights
        new_plot_heights = scaled_panel_heights + non_panel_space
        height_ratios = new_plot_heights / new_plot_heights.max()
        self.gridspec.set_height_ratios(height_ratios)

from __future__ import annotations

import abc
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

import numpy as np

from plotnine.composition import Beside

from ._spaces import (
    LayoutSpaces,
    bottom_spaces,
    left_spaces,
    right_spaces,
    top_spaces,
)

if TYPE_CHECKING:
    from typing import Sequence

    from plotnine import ggplot
    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine._mpl.layout_manager._spaces import (
        bottom_spaces,
        left_spaces,
        right_spaces,
        top_spaces,
    )
    from plotnine.composition import Compose


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

    gridspec: p9GridSpec
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

    nodes: list[LayoutSpaces | LayoutTree]
    """
    The spaces or tree of spaces in the composition that the tree
    represents.
    """

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

        nodes: list[LayoutSpaces | LayoutTree] = []
        for item in cmp:
            if isinstance(item, ggplot):
                nodes.append(lookup_spaces[item])
            else:
                nodes.append(LayoutTree.create(item, lookup_spaces))

        if isinstance(cmp, Beside):
            return ColumnsTree(cmp.gridspec, nodes)
        else:
            return RowsTree(cmp.gridspec, nodes)

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
        # The new width of each panel is the average width of all
        # the panels plus all the space to the left and right
        # of the panels.
        plot_widths = np.array(self.plot_widths)
        panel_widths = np.array(self.panel_widths)
        non_panel_space = plot_widths - panel_widths
        new_plot_widths = panel_widths.mean() + non_panel_space
        width_ratios = new_plot_widths / new_plot_widths.min()
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
        # The new height of each panel is the average width of all
        # the panels plus all the space above and below the panels.
        plot_heights = np.array(self.plot_heights)
        panel_heights = np.array(self.panel_heights)
        non_panel_space = plot_heights - panel_heights
        new_plot_heights = panel_heights.mean() + non_panel_space
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

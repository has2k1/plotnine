from __future__ import annotations

import abc
from contextlib import suppress
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

import numpy as np

from plotnine.plot_composition import OR

from ._spaces import LayoutSpaces

if TYPE_CHECKING:
    from typing import Sequence

    from plotnine import ggplot
    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine.plot_composition import Compose


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

    @cached_property
    @abc.abstractmethod
    def lefts(self) -> Sequence[float]:
        """
        Left values [figure space] of nodes in this tree
        """

    @abc.abstractmethod
    def set_left_alignment_margin(self, value: float):
        """
        Set a margin to align the left of the panels in this composition

        In figure dimenstions
        """

    @cached_property
    @abc.abstractmethod
    def bottoms(self) -> Sequence[float]:
        """
        Bottom values [figure space] of nodes in this tree
        """

    @abc.abstractmethod
    def set_bottom_alignment_margin(self, value: float):
        """
        Set a margin to align the bottom of the panels in this composition

        In figure dimenstions
        """

    @cached_property
    @abc.abstractmethod
    def tops(self) -> Sequence[float]:
        """
        Top values [figure space] of nodes in this tree
        """

    @abc.abstractmethod
    def set_top_alignment_margin(self, value: float):
        """
        Set a margin to align the top of the panels in this composition

        In figure dimenstions
        """

    @cached_property
    @abc.abstractmethod
    def rights(self) -> Sequence[float]:
        """
        Right values [figure space] of nodes in this tree
        """

    @abc.abstractmethod
    def set_right_alignment_margin(self, value: float):
        """
        Set a margin to align the right of the panels in this composition

        In figure dimenstions
        """

    def align_lefts(self):
        """
        Align the immediate left edges in this composition

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

    def align_bottoms(self):
        """
        Align the immediate bottom edges this composition

         -----------        -----------
        |     |     |      |     |     |
        |     |     |      |     |     |
        |     |     |  ->  |     |     |
        |     |#####|      |#####|#####|
        |#####|     |      |     |     |
         -----------        -----------
        """

    def align_rights(self):
        """
        Align the immediate right edges in this composition

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

    def align_tops(self):
        """
        Align the immediate top edges in this composition

         -----------        -----------
        |#####|     |      |     |     |
        |     |#####|      |#####|#####|
        |     |     |  ->  |     |     |
        |     |     |      |     |     |
        |     |     |      |     |     |
         -----------        -----------
        """

    def align(self):
        """
        Align all the edges in this composition & contained compositions

        This function mutates the layout spaces, specifically the
        alignment_margins along the sides of the plot.
        """
        self.align_lefts()
        self.align_bottoms()
        self.align_rights()
        self.align_tops()

        for item in self.nodes:
            if isinstance(item, LayoutTree):
                item.align()

        with suppress(AttributeError):
            del self.lefts

        with suppress(AttributeError):
            del self.bottoms

        with suppress(AttributeError):
            del self.rights

        with suppress(AttributeError):
            del self.tops

    @property
    @abc.abstractmethod
    def panel_width(self) -> float:
        """
        A representative for width for panels of the nodes
        """

    @property
    @abc.abstractmethod
    def panel_height(self) -> float:
        """
        A representative for height for panels of the nodes
        """

    @property
    @abc.abstractmethod
    def plot_width(self) -> float:
        """
        A representative for width for plots of the nodes
        """

    @property
    @abc.abstractmethod
    def plot_height(self) -> float:
        """
        A representative for height for plots of the nodes
        """

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

    def resize(self):
        """
        Resize panels and the entire plots

        This function mutates the composition gridspecs; specifically the
        width_ratios and height_ratios.
        """
        self.resize_widths()
        self.resize_heights()

        for item in self.nodes:
            if isinstance(item, LayoutTree):
                item.resize()

    def resize_widths(self):
        """
        Resize the widths of gridspec so that panels have equal widths
        """

    def resize_heights(self):
        """
        Resize the heights of gridspec so that panels have equal heights
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

        if isinstance(cmp, OR):
            return ColumnsTree(cmp.gridspec, nodes)
        else:
            return RowsTree(cmp.gridspec, nodes)

    def harmonise(self):
        """
        Align and resize plots in composition to look good
        """
        self.align()
        self.resize()


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

    @cached_property
    def lefts(self):
        left_item = self.nodes[0]
        if isinstance(left_item, LayoutSpaces):
            return [left_item.l.left]
        else:
            return left_item.lefts

    def set_left_alignment_margin(self, value: float):
        left_item = self.nodes[0]
        if isinstance(left_item, LayoutSpaces):
            left_item.l.alignment_margin = value
        else:
            left_item.set_left_alignment_margin(value)

    def align_bottoms(self):
        values = max(self.bottoms) - np.array(self.bottoms)
        for item, value in zip(self.nodes, values):
            if isinstance(item, LayoutSpaces):
                item.b.alignment_margin = value
            else:
                item.set_bottom_alignment_margin(value)

    @cached_property
    def bottoms(self):
        values = []
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                values.append(item.b.bottom)
            else:
                values.append(max(item.bottoms))
        return values

    def set_bottom_alignment_margin(self, value: float):
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                item.b.alignment_margin = value
            else:
                item.set_bottom_alignment_margin(value)

    @cached_property
    def rights(self):
        right_item = self.nodes[-1]
        if isinstance(right_item, LayoutSpaces):
            return [right_item.r.right]
        else:
            return right_item.rights

    def set_right_alignment_margin(self, value: float):
        right_item = self.nodes[-1]
        if isinstance(right_item, LayoutSpaces):
            right_item.r.alignment_margin = value
        else:
            right_item.set_right_alignment_margin(value)

    def align_tops(self):
        values = np.array(self.tops) - min(self.tops)
        for item, value in zip(self.nodes, values):
            if isinstance(item, LayoutSpaces):
                item.t.alignment_margin = value
            else:
                item.set_top_alignment_margin(value)

    @cached_property
    def tops(self):
        values = []
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                values.append(item.t.top)
            else:
                values.append(min(item.tops))
        return values

    def set_top_alignment_margin(self, value: float):
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                item.t.alignment_margin = value
            else:
                item.set_top_alignment_margin(value)

    @property
    def panel_width(self) -> float:
        """
        A representative for width for panels of the nodes
        """
        return sum(self.panel_widths)

    @property
    def panel_height(self) -> float:
        """
        A representative for height for panels of the nodes
        """
        return float(np.mean(self.panel_heights))

    @property
    def plot_width(self) -> float:
        """
        A representative for width for plots of the nodes
        """
        return sum(self.plot_widths)

    @property
    def plot_height(self) -> float:
        """
        A representative for height for plots of the nodes
        """
        return max(self.plot_heights)

    def resize_widths(self):
        # The new width of each panel is the average width of all
        # the panels plus all the space to the left and right
        # of the panels.
        plot_widths = np.array(self.plot_widths)
        panel_widths = np.array(self.panel_widths)
        non_panel_space = plot_widths - panel_widths
        new_plot_widths = panel_widths.mean() + non_panel_space
        width_ratios = new_plot_widths / new_plot_widths.min()
        self.gridspec.set_width_ratios(width_ratios)


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

    def align_lefts(self):
        values = max(self.lefts) - np.array(self.lefts)
        for item, value in zip(self.nodes, values):
            if isinstance(item, LayoutSpaces):
                item.l.alignment_margin = value
            else:
                item.set_left_alignment_margin(value)

    @cached_property
    def lefts(self):
        values = []
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                values.append(item.l.left)
            else:
                values.append(max(item.lefts))
        return values

    def set_left_alignment_margin(self, value: float):
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                item.l.alignment_margin = value
            else:
                item.set_left_alignment_margin(value)

    @cached_property
    def bottoms(self):
        bottom_item = self.nodes[-1]
        if isinstance(bottom_item, LayoutSpaces):
            return [bottom_item.b.bottom]
        else:
            return bottom_item.bottoms

    def set_bottom_alignment_margin(self, value: float):
        bottom_item = self.nodes[-1]
        if isinstance(bottom_item, LayoutSpaces):
            bottom_item.b.alignment_margin = value
        else:
            bottom_item.set_bottom_alignment_margin(value)

    def align_rights(self):
        values = np.array(self.rights) - min(self.rights)
        for item, value in zip(self.nodes, values):
            if isinstance(item, LayoutSpaces):
                item.r.alignment_margin = value
            else:
                item.set_right_alignment_margin(value)

    @cached_property
    def rights(self):
        values = []
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                values.append(item.r.right)
            else:
                values.append(min(item.rights))
        return values

    def set_right_alignment_margin(self, value: float):
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                item.r.alignment_margin = value
            else:
                item.set_right_alignment_margin(value)

    @cached_property
    def tops(self):
        top_item = self.nodes[0]
        if isinstance(top_item, LayoutSpaces):
            return [top_item.t.top]
        else:
            return top_item.tops

    def set_top_alignment_margin(self, value: float):
        top_item = self.nodes[0]
        if isinstance(top_item, LayoutSpaces):
            top_item.t.alignment_margin = value
        else:
            top_item.set_top_alignment_margin(value)

    @property
    def panel_width(self) -> float:
        """
        A representative for width for panels of the nodes
        """
        return float(np.mean(self.panel_widths))

    @property
    def panel_height(self) -> float:
        """
        A representative for height for panels of the nodes
        """
        return sum(self.panel_heights)

    @property
    def plot_width(self) -> float:
        """
        A representative for width for plots of the nodes
        """
        return max(self.plot_widths)

    @property
    def plot_height(self) -> float:
        """
        A representative for height for plots of the nodes
        """
        return sum(self.plot_heights)

    def resize_heights(self):
        # The new width of each panel is the average width of all
        # the panels plus all the space above and below the panels.
        plot_heights = np.array(self.plot_heights)
        panel_heights = np.array(self.panel_heights)
        non_panel_space = plot_heights - panel_heights
        new_plot_heights = panel_heights.mean() + non_panel_space
        height_ratios = new_plot_heights / new_plot_heights.max()
        self.gridspec.set_height_ratios(height_ratios)

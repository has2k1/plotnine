from __future__ import annotations

import abc
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, cast

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
    def sub_compositions(self) -> list[LayoutTree]:
        """
        LayoutTrees of the direct sub compositions of this one
        """
        return [item for item in self.nodes if isinstance(item, LayoutTree)]

    @cached_property
    @abc.abstractmethod
    def lefts(self) -> Sequence[float]:
        """
        Left values [figure space] of nodes in this tree
        """

    @cached_property
    @abc.abstractmethod
    def rights(self) -> Sequence[float]:
        """
        Right values [figure space] of nodes in this tree
        """

    @cached_property
    @abc.abstractmethod
    def bottoms(self) -> Sequence[float]:
        """
        Bottom values [figure space] of nodes in this tree
        """

    @cached_property
    @abc.abstractmethod
    def tops(self) -> Sequence[float]:
        """
        Top values [figure space] of nodes in this tree
        """

    @property
    def lefts_align(self) -> bool:
        """
        Return True if panel lefts for the nodes are aligned
        """
        arr = np.array(self.lefts)
        return all(arr == arr[0])

    @property
    def rights_align(self) -> bool:
        """
        Return True if panel rights for the nodes are aligned
        """
        arr = np.array(self.rights)
        return all(arr == arr[0])

    @property
    def bottoms_align(self) -> bool:
        """
        Return True if panel bottoms for the nodes are aligned
        """
        arr = np.array(self.bottoms)
        return all(arr == arr[0])

    @property
    def tops_align(self) -> bool:
        """
        Return True if panel tops for the nodes are aligned
        """
        arr = np.array(self.tops)
        return all(arr == arr[0])

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

    @cached_property
    @abc.abstractmethod
    def left_tag_width(self) -> float:
        """
        A representative width [figure space] for the left tags of the nodes
        """

    @cached_property
    @abc.abstractmethod
    def right_tag_width(self) -> float:
        """
        A representative width [figure space] for the right tags of the nodes
        """

    @cached_property
    @abc.abstractmethod
    def bottom_tag_height(self) -> float:
        """
        A representative height [figure space] for the top tags of the nodes
        """

    @cached_property
    @abc.abstractmethod
    def top_tag_height(self) -> float:
        """
        A representative height [figure space] for the top tags of the nodes
        """

    @cached_property
    def left_tag_widths(self) -> list[float]:
        """
        The widths of the left tags in this tree
        """
        return [node.left_tag_width for node in self.nodes]

    @cached_property
    def right_tag_widths(self) -> list[float]:
        """
        The widths of the right tags in this tree
        """
        return [node.right_tag_width for node in self.nodes]

    @cached_property
    def bottom_tag_heights(self) -> list[float]:
        """
        The heights of the bottom tags in this tree
        """
        return [node.bottom_tag_height for node in self.nodes]

    @cached_property
    def top_tag_heights(self) -> list[float]:
        """
        The heights of the top tags in this tree
        """
        return [node.top_tag_height for node in self.nodes]

    @property
    def left_tags_align(self) -> bool:
        """
        Return True if the left tags for the nodes are aligned
        """
        arr = np.array(self.left_tag_widths)
        return all(arr == arr[0])

    @property
    def right_tags_align(self) -> bool:
        """
        Return True if the right tags for the nodes are aligned
        """
        arr = np.array(self.right_tag_widths)
        return all(arr == arr[0])

    @property
    def bottom_tags_align(self) -> bool:
        """
        Return True if the bottom tags for the nodes are aligned
        """
        arr = np.array(self.bottom_tag_heights)
        return all(arr == arr[0])

    @property
    def top_tags_align(self) -> bool:
        """
        Return True if the top tags for the nodes are aligned
        """
        arr = np.array(self.top_tag_heights)
        return all(arr == arr[0])

    @abc.abstractmethod
    def set_left_margin_alignment(self, value: float):
        """
        Set a margin to align the left of the panels in this composition

        In figure dimenstions
        """

    @abc.abstractmethod
    def set_right_margin_alignment(self, value: float):
        """
        Set a margin to align the right of the panels in this composition

        In figure dimenstions
        """

    @abc.abstractmethod
    def set_bottom_margin_alignment(self, value: float):
        """
        Set a margin to align the bottom of the panels in this composition

        In figure dimenstions
        """

    @abc.abstractmethod
    def set_top_margin_alignment(self, value: float):
        """
        Set a margin to align the top of the panels in this composition

        In figure dimenstions
        """

    @abc.abstractmethod
    def set_left_tag_alignment(self, value: float):
        """
        Set the space to align the left tags in this composition

        In figure dimenstions
        """

    @abc.abstractmethod
    def set_right_tag_alignment(self, value: float):
        """
        Set the space to align the right tags in this composition

        In figure dimenstions
        """

    @abc.abstractmethod
    def set_bottom_tag_alignment(self, value: float):
        """
        Set the space to align the bottom tags in this composition

        In figure dimenstions
        """

    @abc.abstractmethod
    def set_top_tag_alignment(self, value: float):
        """
        Set the space to align the top tags in this composition

        In figure dimenstions
        """


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
        self.align_tops()
        self.align_bottoms()
        self.align_sub_compositions()

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
        # If panels are aligned and have a non-zero margin_alignment,
        # aligning them again will set that value to zero and undoes
        # the alignment.
        if self.bottoms_align:
            return

        values = max(self.bottoms) - np.array(self.bottoms)
        for item, value in zip(self.nodes, values):
            if isinstance(item, LayoutSpaces):
                item.b.margin_alignment = value
            else:
                item.set_bottom_margin_alignment(value)

        del self.bottoms

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
        if self.tops_align:
            return

        values = np.array(self.tops) - min(self.tops)
        for item, value in zip(self.nodes, values):
            if isinstance(item, LayoutSpaces):
                item.t.margin_alignment = value
            else:
                item.set_top_margin_alignment(value)

        del self.tops

    def align_bottom_tags(self):
        if self.bottom_tags_align:
            return

        values = cast(
            "Sequence[float]",
            max(self.bottom_tag_heights) - np.array(self.bottom_tag_heights),
        )
        for item, value in zip(self.nodes, values):
            if isinstance(item, LayoutSpaces):
                item.l.tag_alignment = value
            else:
                item.set_bottom_tag_alignment(value)

    def align_top_tags(self):
        if self.top_tags_align:
            return

        values = cast(
            "Sequence[float]",
            max(self.top_tag_heights) - np.array(self.top_tag_heights),
        )
        for item, value in zip(self.nodes, values):
            if isinstance(item, LayoutSpaces):
                item.t.tag_alignment = value
            else:
                item.set_top_tag_alignment(value)

    @cached_property
    def lefts(self):
        left_item = self.nodes[0]
        if isinstance(left_item, LayoutSpaces):
            return [left_item.l.left]
        else:
            return left_item.lefts

    @cached_property
    def rights(self):
        right_item = self.nodes[-1]
        if isinstance(right_item, LayoutSpaces):
            return [right_item.r.right]
        else:
            return right_item.rights

    @cached_property
    def bottoms(self):
        values = []
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                values.append(item.b.bottom)
            else:
                values.append(max(item.bottoms))
        return values

    @cached_property
    def tops(self):
        values = []
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                values.append(item.t.top)
            else:
                values.append(min(item.tops))
        return values

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

    @cached_property
    def left_tag_width(self) -> float:
        return self.left_tag_widths[0]

    @cached_property
    def right_tag_width(self) -> float:
        return self.right_tag_widths[-1]

    @cached_property
    def bottom_tag_height(self) -> float:
        return max(self.bottom_tag_heights)

    @cached_property
    def top_tag_height(self) -> float:
        return max(self.top_tag_heights)

    def set_left_margin_alignment(self, value: float):
        left_item = self.nodes[0]
        if isinstance(left_item, LayoutSpaces):
            left_item.l.margin_alignment = value
        else:
            left_item.set_left_margin_alignment(value)

    def set_right_margin_alignment(self, value: float):
        right_item = self.nodes[-1]
        if isinstance(right_item, LayoutSpaces):
            right_item.r.margin_alignment = value
        else:
            right_item.set_right_margin_alignment(value)

    def set_bottom_margin_alignment(self, value: float):
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                item.b.margin_alignment = value
            else:
                item.set_bottom_margin_alignment(value)

    def set_top_margin_alignment(self, value: float):
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                item.t.margin_alignment = value
            else:
                item.set_top_margin_alignment(value)

    def set_bottom_tag_alignment(self, value: float):
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                item.l.tag_alignment = value
            else:
                item.set_bottom_tag_alignment(value)

    def set_top_tag_alignment(self, value: float):
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                item.t.tag_alignment = value
            else:
                item.set_top_tag_alignment(value)


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
        self.align_lefts()
        self.align_rights()
        self.align_sub_compositions()

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
        if self.lefts_align:
            return

        values = max(self.lefts) - np.array(self.lefts)
        for item, value in zip(self.nodes, values):
            if isinstance(item, LayoutSpaces):
                item.l.margin_alignment = value
            else:
                item.set_left_margin_alignment(value)

        del self.lefts

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
        if self.rights_align:
            return

        values = np.array(self.rights) - min(self.rights)
        for item, value in zip(self.nodes, values):
            if isinstance(item, LayoutSpaces):
                item.r.margin_alignment = value
            else:
                item.set_right_margin_alignment(value)

        del self.rights

    def align_left_tags(self):
        """
        Make all the left tags takeup the same amount of space


        Given

                      V
         ------------------------------------
        | plot_margin | tag | artists        |
        |------------------------------------|
        | plot_margin | A long tag | artists |
         ------------------------------------

                      V
         ------------------------------------
        | plot_margin | #######tag | artists |
        |------------------------------------|
        | plot_margin | A long tag | artists |
         ------------------------------------
        """
        if self.left_tags_align:
            return

        values = cast(
            "Sequence[float]",
            max(self.left_tag_widths) - np.array(self.left_tag_widths),
        )
        for item, value in zip(self.nodes, values):
            if isinstance(item, LayoutSpaces):
                item.l.tag_alignment = value
            else:
                item.set_left_tag_alignment(value)

    def align_right_tags(self):
        if self.right_tags_align:
            return

        values = cast(
            "Sequence[float]",
            max(self.right_tag_widths) - np.array(self.right_tag_widths),
        )
        for item, value in zip(self.nodes, values):
            if isinstance(item, LayoutSpaces):
                item.r.tag_alignment = value
            else:
                item.set_right_tag_alignment(value)

    @cached_property
    def lefts(self):
        values = []
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                values.append(item.l.left)
            else:
                values.append(max(item.lefts))
        return values

    @cached_property
    def rights(self):
        values = []
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                values.append(item.r.right)
            else:
                values.append(min(item.rights))
        return values

    @cached_property
    def bottoms(self):
        bottom_item = self.nodes[-1]
        if isinstance(bottom_item, LayoutSpaces):
            return [bottom_item.b.bottom]
        else:
            return bottom_item.bottoms

    @cached_property
    def tops(self):
        top_item = self.nodes[0]
        if isinstance(top_item, LayoutSpaces):
            return [top_item.t.top]
        else:
            return top_item.tops

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

    @cached_property
    def left_tag_width(self) -> float:
        return max(self.left_tag_widths)

    @cached_property
    def right_tag_width(self) -> float:
        return max(self.right_tag_widths)

    @cached_property
    def top_tag_height(self) -> float:
        return self.top_tag_heights[0]

    @cached_property
    def bottom_tag_height(self) -> float:
        return self.bottom_tag_heights[-1]

    def set_left_margin_alignment(self, value: float):
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                item.l.margin_alignment = value
            else:
                item.set_left_margin_alignment(value)

    def set_right_margin_alignment(self, value: float):
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                item.r.margin_alignment = value
            else:
                item.set_right_margin_alignment(value)

    def set_bottom_margin_alignment(self, value: float):
        bottom_item = self.nodes[-1]
        if isinstance(bottom_item, LayoutSpaces):
            bottom_item.b.margin_alignment = value
        else:
            bottom_item.set_bottom_margin_alignment(value)

    def set_top_margin_alignment(self, value: float):
        top_item = self.nodes[0]
        if isinstance(top_item, LayoutSpaces):
            top_item.t.margin_alignment = value
        else:
            top_item.set_top_margin_alignment(value)

    def set_left_tag_alignment(self, value: float):
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                item.l.tag_alignment = value
            else:
                item.set_left_tag_alignment(value)

    def set_right_tag_alignment(self, value: float):
        for item in self.nodes:
            if isinstance(item, LayoutSpaces):
                item.r.tag_alignment = value
            else:
                item.set_right_tag_alignment(value)

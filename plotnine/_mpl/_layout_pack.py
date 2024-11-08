from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import TYPE_CHECKING, cast

from matplotlib._tight_layout import get_subplotspec_list
from matplotlib.backend_bases import RendererBase
from matplotlib.text import Text

from .utils import Calc

if TYPE_CHECKING:
    from typing import (
        Any,
        Iterator,
        Literal,
        TypeAlias,
    )

    from matplotlib.axes import Axes
    from matplotlib.axis import Tick

    from plotnine import ggplot
    from plotnine._mpl.text import StripText
    from plotnine.iapi import legend_artists
    from plotnine.typing import StripPosition

    AxesLocation: TypeAlias = Literal[
        "all", "first_row", "last_row", "first_col", "last_col"
    ]


@dataclass
class LayoutPack:
    """
    Objects required to compute the layout
    """

    plot: ggplot

    def __post_init__(self):
        def get(name: str) -> Any:
            """
            Return themeable target or None
            """
            if self.theme.T.is_blank(name):
                return None
            else:
                t = getattr(self.theme.targets, name)
                if isinstance(t, Text) and t.get_text() == "":
                    return None
                return t

        self.axs = self.plot.axs
        self.theme = self.plot.theme
        self.figure = self.plot.figure
        self.facet = self.plot.facet
        self.renderer = cast(RendererBase, self.plot.figure._get_renderer())  # pyright: ignore
        self.calc = Calc(self.figure, self.renderer)

        self.axis_title_x: Text | None = get("axis_title_x")
        self.axis_title_y: Text | None = get("axis_title_y")

        # # The legends references the structure that contains the
        # # AnchoredOffsetboxes (groups of legends)
        self.legends: legend_artists | None = get("legends")
        self.plot_caption: Text | None = get("plot_caption")
        self.plot_subtitle: Text | None = get("plot_subtitle")
        self.plot_title: Text | None = get("plot_title")
        self.strip_text_x: list[StripText] | None = get("strip_text_x")
        self.strip_text_y: list[StripText] | None = get("strip_text_y")

    def _is_blank(self, name: str) -> bool:
        return self.theme.T.is_blank(name)

    def _filter_axes(self, location: AxesLocation = "all") -> list[Axes]:
        """
        Return subset of axes
        """
        if location == "all":
            return self.axs

        # e.g. is_first_row, is_last_row, ..
        pred_method = f"is_{location}"
        return [
            ax
            for spec, ax in zip(get_subplotspec_list(self.axs), self.axs)
            if getattr(spec, pred_method)()
        ]

    def axis_labels_x(self, ax: Axes) -> Iterator[Text]:
        """
        Return all x-axis labels for an axes that will be shown
        """
        major, minor = [], []

        if not self._is_blank("axis_text_x"):
            major = ax.xaxis.get_major_ticks()
            minor = ax.xaxis.get_minor_ticks()

        return (
            tick.label1
            for tick in chain(major, minor)
            if _text_is_visible(tick.label1)
        )

    def axis_labels_y(self, ax: Axes) -> Iterator[Text]:
        """
        Return all y-axis labels for an axes that will be shown
        """
        major, minor = [], []

        if not self._is_blank("axis_text_y"):
            major = ax.yaxis.get_major_ticks()
            minor = ax.yaxis.get_minor_ticks()

        return (
            tick.label1
            for tick in chain(major, minor)
            if _text_is_visible(tick.label1)
        )

    def axis_ticks_x(self, ax: Axes) -> Iterator[Tick]:
        """
        Return all XTicks that will be shown
        """
        major, minor = [], []

        if not self._is_blank("axis_ticks_major_x"):
            major = ax.xaxis.get_major_ticks()

        if not self._is_blank("axis_ticks_minor_x"):
            minor = ax.xaxis.get_minor_ticks()

        return chain(major, minor)

    def axis_ticks_y(self, ax: Axes) -> Iterator[Tick]:
        """
        Return all YTicks that will be shown
        """
        major, minor = [], []

        if not self._is_blank("axis_ticks_major_y"):
            major = ax.yaxis.get_major_ticks()

        if not self._is_blank("axis_ticks_minor_y"):
            minor = ax.yaxis.get_minor_ticks()

        return chain(major, minor)

    def axis_ticks_pad_x(self, ax: Axes) -> Iterator[float]:
        """
        Return XTicks paddings
        """
        # In plotnine tick padding are specified as a margin to the
        # the axis_text.
        major, minor = [], []
        if not self._is_blank("axis_text_x"):
            h = self.figure.get_figheight() * 72
            major = [
                (t.get_pad() or 0) / h for t in ax.xaxis.get_major_ticks()
            ]
            minor = [
                (t.get_pad() or 0) / h for t in ax.xaxis.get_minor_ticks()
            ]
        return chain(major, minor)

    def axis_ticks_pad_y(self, ax: Axes) -> Iterator[float]:
        """
        Return YTicks paddings
        """
        # In plotnine tick padding are specified as a margin to the
        # the axis_text.
        major, minor = [], []
        if not self._is_blank("axis_text_y"):
            w = self.figure.get_figwidth() * 72
            major = [
                (t.get_pad() or 0) / w for t in ax.yaxis.get_major_ticks()
            ]
            minor = [
                (t.get_pad() or 0) / w for t in ax.yaxis.get_minor_ticks()
            ]
        return chain(major, minor)

    def strip_text_x_height(self, position: StripPosition) -> float:
        """
        Height taken up by the top strips
        """
        if not self.strip_text_x:
            return 0

        artists = [
            st.patch if st.patch.get_visible() else st
            for st in self.strip_text_x
            if st.patch.position == position
        ]
        return self.calc.max_height(artists)

    def strip_text_y_width(self, position: StripPosition) -> float:
        """
        Width taken up by the right strips
        """
        if not self.strip_text_y:
            return 0

        artists = [
            st.patch if st.patch.get_visible() else st
            for st in self.strip_text_y
            if st.patch.position == position
        ]
        return self.calc.max_width(artists)

    def axis_ticks_x_max_height(self, location: AxesLocation) -> float:
        """
        Return maximum height[inches] of x ticks
        """
        heights = [
            self.calc.tight_height(tick.tick1line)
            for ax in self._filter_axes(location)
            for tick in self.axis_ticks_x(ax)
        ]
        return max(heights) if len(heights) else 0

    def axis_text_x_max_height(self, location: AxesLocation) -> float:
        """
        Return maximum height[inches] of x tick labels
        """
        heights = [
            self.calc.tight_height(label) + pad
            for ax in self._filter_axes(location)
            for label, pad in zip(
                self.axis_labels_x(ax), self.axis_ticks_pad_x(ax)
            )
        ]
        return max(heights) if len(heights) else 0

    def axis_ticks_y_max_width(self, location: AxesLocation) -> float:
        """
        Return maximum width[inches] of y ticks
        """
        widths = [
            self.calc.tight_width(tick.tick1line)
            for ax in self._filter_axes(location)
            for tick in self.axis_ticks_y(ax)
        ]
        return max(widths) if len(widths) else 0

    def axis_text_y_max_width(self, location: AxesLocation) -> float:
        """
        Return maximum width[inches] of y tick labels
        """
        widths = [
            self.calc.tight_width(label) + pad
            for ax in self._filter_axes(location)
            for label, pad in zip(
                self.axis_labels_y(ax), self.axis_ticks_pad_y(ax)
            )
        ]
        return max(widths) if len(widths) else 0

    def axis_text_y_top_protrusion(self, location: AxesLocation) -> float:
        """
        Return maximum height[inches] above the axes of y tick labels
        """
        extras = []
        for ax in self._filter_axes(location):
            ax_top_y = self.calc.top_y(ax)
            for label in self.axis_labels_y(ax):
                label_top_y = self.calc.top_y(label)
                extras.append(max(0, label_top_y - ax_top_y))

        return max(extras) if len(extras) else 0

    def axis_text_y_bottom_protrusion(self, location: AxesLocation) -> float:
        """
        Return maximum height[inches] below the axes of y tick labels
        """
        extras = []
        for ax in self._filter_axes(location):
            ax_bottom_y = self.calc.bottom_y(ax)
            for label in self.axis_labels_y(ax):
                label_bottom_y = self.calc.bottom_y(label)
                protrusion = abs(min(label_bottom_y - ax_bottom_y, 0))
                extras.append(protrusion)

        return max(extras) if len(extras) else 0

    def axis_text_x_left_protrusion(self, location: AxesLocation) -> float:
        """
        Return maximum width[inches] of x tick labels to the left of the axes
        """
        extras = []
        for ax in self._filter_axes(location):
            ax_left_x = self.calc.left_x(ax)
            for label in self.axis_labels_x(ax):
                label_left_x = self.calc.left_x(label)
                protrusion = abs(min(label_left_x - ax_left_x, 0))
                extras.append(protrusion)

        return max(extras) if len(extras) else 0

    def axis_text_x_right_protrusion(self, location: AxesLocation) -> float:
        """
        Return maximum width[inches] of x tick labels to the right of the axes
        """
        extras = []
        for ax in self._filter_axes(location):
            ax_right_x = self.calc.right_x(ax)
            for label in self.axis_labels_x(ax):
                label_right_x = self.calc.right_x(label)
                extras.append(max(0, label_right_x - ax_right_x))

        return max(extras) if len(extras) else 0


def _text_is_visible(text: Text) -> bool:
    """
    Return True if text is visible and is not empty
    """
    return text.get_visible() and text._text  # type: ignore

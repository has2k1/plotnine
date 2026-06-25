from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..iapi import strip_label_details

if TYPE_CHECKING:
    from typing import Sequence

    from matplotlib.axes import Axes
    from typing_extensions import Self

    from plotnine import theme
    from plotnine.facets.facet import facet
    from plotnine.facets.layout import Layout
    from plotnine.iapi import layout_details
    from plotnine.typing import StripPosition


class strip:
    """
    A strip

    This class exists to have in one place all that is required to draw
    strip text onto an axes. As Matplotlib does not have a layout manager
    that makes it easy to adorn an axes with artists, we have to compute
    the space required for the text and the background strip on which it
    is drawn. This is very finicky and fails once the facets become
    complicated.
    """

    position: StripPosition
    label_info: strip_label_details

    def __init__(
        self,
        vars: Sequence[str],
        layout_info: layout_details,
        facet: facet,
        ax: Axes,
        position: StripPosition,
    ):
        self.vars = vars
        self.ax = ax
        self.position = position
        self.facet = facet
        self.figure = facet.figure
        self.theme = facet.theme
        self.layout_info = layout_info
        label_info = strip_label_details.make(layout_info, vars, position)
        self.label_info = facet.labeller(label_info)

    def draw(self):
        """
        Create a background patch and put a label on it
        """

        from .._mpl.text import StripText

        targets = self.theme.targets
        position = self.position

        text = StripText(self.ax, position, self.label_info.text())
        rect = text.patch

        figure = self.facet.plot.figure
        figure.add_artist(rect)
        figure.add_artist(text)

        # x-axis strips sit on top/bottom, y-axis strips on left/right.
        # Background is tracked per axis, text per side.
        g = "y" if position in ("left", "right") else "x"
        getattr(targets, f"strip_background_{g}").append(rect)
        getattr(targets, f"strip_text_{g}_{position}").append(text)


class Strips(List[strip]):
    """
    List of strips for a plot
    """

    facet: facet

    @staticmethod
    def from_facet(facet: facet) -> Strips:
        new = Strips()
        new.facet = facet
        new.setup()
        return new

    @property
    def axs(self) -> list[Axes]:
        return self.facet.axs

    @property
    def layout(self) -> Layout:
        return self.facet.layout

    @property
    def theme(self) -> theme:
        return self.facet.theme

    @property
    def top_strips(self) -> Strips:
        return Strips([s for s in self if s.position == "top"])

    @property
    def right_strips(self) -> Strips:
        return Strips([s for s in self if s.position == "right"])

    def draw(self):
        for s in self:
            s.draw()

    def setup(self) -> Self:
        """
        Calculate the box information for all strips

        It is stored in self.strip_info
        """
        for layout_info in self.layout.get_details():
            ax = self.axs[layout_info.panel_index]
            lst = self.facet.make_strips(layout_info, ax)
            self.extend(lst)
        return self

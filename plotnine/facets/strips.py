from __future__ import annotations

import typing
from contextlib import suppress
from typing import List

from ..iapi import strip_draw_info, strip_label_details

if typing.TYPE_CHECKING:
    from plotnine.iapi import layout_details
    from plotnine.typing import (
        Axes,
        Facet,
        Layout,
        StripPosition,
        Theme,
    )


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
        vars: list[str],
        layout_info: layout_details,
        facet: Facet,
        ax: Axes,
        position: StripPosition,
    ):
        self.vars = vars
        self.ax = ax
        self.position = position
        self.facet = facet
        self.figure = facet.figure
        self.theme = facet.theme
        label_info = strip_label_details.make(layout_info, vars, position)
        self.label_info = facet.labeller(label_info)
        self.draw_info = self.get_draw_info()

    def get_draw_info(self) -> strip_draw_info:
        """
        Get information required to draw strips

        Returns
        -------
        out :
            A structure with all the coordinates (x, y) required
            to draw the strip text and the background box
            (box_x, box_y, box_width, box_height).
        """
        _property = self.theme.themeables.property
        position = self.position
        if position == "top":
            # The x & y values are just starting locations
            # The final location is determined by the layout manager.
            x, y = 0, 1
            ha, va = "center", "bottom"
            rotation = _property("strip_text_x", "rotation")
            box_width = 1
            box_height = 0  # Determined by the text size
            # TODO: Allow two unique paddings for either side.
            # Requires implementing an mpl.patches.boxstyle that recognises
            # two padding values.
            strip_text_margin = _property("strip_text_x", "margin").get_as(
                "b", "lines"
            )
            strip_align = _property("strip_align_x")

            # x & width properties of the background slide and
            # shrink the strip horizontally.
            with suppress(KeyError):
                x = _property("strip_text_x", "x")
            with suppress(KeyError):
                box_width = _property("strip_background_x", "width")

        elif position == "right":
            # The x & y values are just starting locations
            # The final location is determined by the layout manager.
            x, y = 1, 0
            ha, va = "left", "center"
            rotation = _property("strip_text_y", "rotation")
            box_width = 0  # Determine by the text height
            box_height = 1
            # TODO: Allow two unique paddings for either side.
            # Requires implementing an mpl.patches.boxstyle that recognises
            # two padding values.
            strip_text_margin = _property("strip_text_y", "margin").get_as(
                "r", "lines"
            )
            strip_align = _property("strip_align_y")

            # y & height properties of the background slide and
            # shrink the strip vertically.
            with suppress(KeyError):
                y = _property("strip_text_y", "y")
            with suppress(KeyError):
                box_height = _property("strip_background_y", "height")
        else:
            raise ValueError(f"Unknown position for strip text: {position!r}")

        return strip_draw_info(
            x=x,
            y=y,
            ha=ha,
            va=va,
            box_width=box_width,
            box_height=box_height,
            strip_text_margin=strip_text_margin,
            strip_align=strip_align,
            position=position,
            label=self.label_info.text(),
            ax=self.ax,
            rotation=rotation,
        )

    def draw(self):
        """
        Create a background patch and put a label on it
        """

        from .._mpl.text import SText

        _targets = self.theme._targets
        text = SText(self.draw_info)
        rect = text.spatch

        self.ax.add_artist(text)
        self.ax.add_artist(rect)

        for key in (
            "strip_text_x",
            "strip_text_y",
            "strip_background_x",
            "strip_background_y",
        ):
            if key not in _targets:
                _targets[key] = []

        if self.draw_info.position == "right":
            _targets["strip_background_y"].append(rect)
            _targets["strip_text_y"].append(text)
        else:
            _targets["strip_background_x"].append(rect)
            _targets["strip_text_x"].append(text)


class Strips(List[strip]):
    """
    List of strips for a plot
    """

    facet: Facet

    @staticmethod
    def from_facet(facet: Facet) -> Strips:
        new = Strips()
        new.facet = facet
        return new

    @property
    def axs(self) -> list[Axes]:
        return self.facet.axs

    @property
    def layout(self) -> Layout:
        return self.facet.layout

    @property
    def theme(self) -> Theme:
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

    def generate(self):
        """
        Calculate the box information for all strips

        It is stored in self.strip_info
        """
        for layout_info in self.layout.get_details():
            ax = self.axs[layout_info.panel_index]
            lst = self.facet.make_ax_strips(layout_info, ax)
            self.extend(lst)

"""
Theme elements used to decorate the graph.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .element_base import element_base

if TYPE_CHECKING:
    from typing import Any, Optional, Sequence


class element_rect(element_base):
    """
    Theme element: Rectangle

    Used for backgrounds and borders

    Parameters
    ----------
    fill : str | tuple
        Rectangle background color
    color : str | tuple
        Line color
    colour : str | tuple
        Alias of color
    size : float
        Line thickness
    kwargs : dict
        Parameters recognised by
        [](`~matplotlib.patches.Rectangle`).
        In some cases you can use the fancy parameters from
        [](`~matplotlib.patches.FancyBboxPatch`).
    """

    def __init__(
        self,
        fill: Optional[
            str
            | tuple[float, float, float]
            | tuple[float, float, float, float]
        ] = None,
        color: Optional[
            str
            | tuple[float, float, float]
            | tuple[float, float, float, float]
        ] = None,
        size: Optional[float] = None,
        linetype: Optional[str | Sequence[int]] = None,
        colour: Optional[
            str
            | tuple[float, float, float]
            | tuple[float, float, float, float]
        ] = None,
        **kwargs: Any,
    ):
        super().__init__()
        self.properties.update(**kwargs)

        color = color if color else colour
        if fill:
            self.properties["facecolor"] = fill
        if color:
            self.properties["edgecolor"] = color
        if size is not None:
            self.properties["linewidth"] = size
        if linetype:
            self.properties["linestyle"] = linetype

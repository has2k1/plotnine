from __future__ import annotations

from typing import TYPE_CHECKING

from .element_base import element_base

if TYPE_CHECKING:
    from typing import Any, Literal, Optional, Sequence


class element_line(element_base):
    """
    theme element: line

    used for backgrounds and borders

    parameters
    ----------
    color : str | tuple
        line color
    colour : str | tuple
        alias of color
    linetype : str | tuple
        line style. if a string, it should be one of *solid*, *dashed*,
        *dashdot* or *dotted*. you can create interesting dashed patterns
        using tuples, see [](`~matplotlib.lines.line2D.set_linestyle`).
    size : float
        line thickness
    kwargs : dict
        Parameters recognised by [](`~matplotlib.lines.line2d`).
    """

    def __init__(
        self,
        *,
        color: Optional[
            str
            | tuple[float, float, float]
            | tuple[float, float, float, float]
        ] = None,
        size: Optional[float] = None,
        linetype: Optional[str | Sequence[int]] = None,
        lineend: Optional[Literal["butt", "projecting", "round"]] = None,
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
        if color:
            self.properties["color"] = color
        if size:
            self.properties["linewidth"] = size
        if linetype:
            self.properties["linestyle"] = linetype

        if linetype in ("solid", "-") and lineend:
            self.properties["solid_capstyle"] = lineend
        elif linetype and lineend:
            self.properties["dash_capstyle"] = lineend

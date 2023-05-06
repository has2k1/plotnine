"""
Theme elements used to decorate the graph.
"""
from __future__ import annotations

import typing
from contextlib import suppress
from dataclasses import dataclass

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Literal, Optional, Sequence

    from plotnine.typing import Theme, TupleFloat3, TupleFloat4


class element_base:
    """
    Base class for all theme elements
    """

    properties: dict[str, Any]  # dict of the properties

    def __init__(self):
        self.properties = {"visible": True}

    def __repr__(self) -> str:
        """
        Element representation
        """
        return f"{self.__class__.__name__}({self})"

    def __str__(self) -> str:
        """
        Element as string
        """
        d = self.properties.copy()
        del d["visible"]
        return f"{d}"

    def setup(self, theme: Theme):
        """
        Setup the theme_element before drawing
        """
        pass


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
        using tuples, see :meth:`matplotlib.lines.line2D.set_linestyle`.
    size : float
        line thickness
    kwargs : dict
        parameters recognised by
        :class:`matplotlib.lines.line2d`.
    """

    def __init__(
        self,
        *,
        color: Optional[str | TupleFloat3 | TupleFloat4] = None,
        size: Optional[float] = None,
        linetype: Optional[str | Sequence[int]] = None,
        lineend: Optional[Literal["butt", "projecting", "round"]] = None,
        colour: Optional[str | TupleFloat3 | TupleFloat4] = None,
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
        :class:`matplotlib.patches.Rectangle`. In some cases
        you can use the fancy parameters from
        :class:`matplotlib.patches.FancyBboxPatch`.
    """

    def __init__(
        self,
        fill: Optional[str | TupleFloat3 | TupleFloat4] = None,
        color: Optional[str | TupleFloat3 | TupleFloat4] = None,
        size: Optional[float] = None,
        linetype: Optional[str | Sequence[int]] = None,
        colour: Optional[str | TupleFloat3 | TupleFloat4] = None,
        **kwargs: Any,
    ):
        super().__init__()
        self.properties.update(**kwargs)

        color = color if color else colour
        if fill:
            self.properties["facecolor"] = fill
        if color:
            self.properties["edgecolor"] = color
        if size:
            self.properties["linewidth"] = size
        if linetype:
            self.properties["linestyle"] = linetype


class element_text(element_base):
    """
    Theme element: Text

    Parameters
    ----------
    family : str
        Font family. See :meth:`matplotlib.text.Text.set_family`
        for supported values.
    style : str in ``['normal', 'italic', 'oblique']``
        Font style
    color : str | tuple
        Text color
    weight : str
        Should be one of *normal*, *bold*, *heavy*, *light*,
        *ultrabold* or *ultralight*.
    size : float
        text size
    ha : str in ``['center', 'left', 'right']``
        Horizontal Alignment.
    va : str in ``['center' , 'top', 'bottom', 'baseline']``
        Vertical alignment.
    rotation : float
        Rotation angle in the range [0, 360]
    linespacing : float
        Line spacing
    backgroundcolor : str | tuple
        Background color
    margin : dict
        Margin around the text. The keys are one of
        ``['t', 'b', 'l', 'r']`` and ``units``. The units are
        one of ``['pt', 'lines', 'in']``. The *units* default
        to ``pt`` and the other keys to ``0``. Not all text
        themeables support margin parameters and other than the
        ``units``, only some of the other keys may apply.
    kwargs : dict
        Parameters recognised by :class:`matplotlib.text.Text`

    Notes
    -----
    :class:`element_text` will accept parameters that conform to the
    **ggplot2** *element_text* API, but it is preferable the
    **Matplotlib** based API described above.
    """

    def __init__(
        self,
        family: Optional[str | list[str]] = None,
        style: Optional[str] = None,
        weight: Optional[int | str] = None,
        color: Optional[str | TupleFloat3 | TupleFloat4] = None,
        size: Optional[float] = None,
        ha: Optional[Literal["center", "left", "right"]] = None,
        va: Optional[Literal["center", "top", "bottom", "baseline"]] = None,
        rotation: Optional[float] = None,
        linespacing: Optional[float] = None,
        backgroundcolor: Optional[str | TupleFloat3 | TupleFloat4] = None,
        margin: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ):
        # ggplot2 translation
        with suppress(KeyError):
            linespacing = kwargs.pop("lineheight")
        with suppress(KeyError):
            color = color or kwargs.pop("colour")
        with suppress(KeyError):
            _face = kwargs.pop("face")
            if _face == "plain":
                style = "normal"
            elif _face == "italic":
                style = "italic"
            elif _face == "bold":
                weight = "bold"
            elif _face == "bold.italic":
                style = "italic"
                weight = "bold"
        with suppress(KeyError):
            ha = self._translate_hjust(kwargs.pop("hjust"))
        with suppress(KeyError):
            va = self._translate_vjust(kwargs.pop("vjust"))
        with suppress(KeyError):
            rotation = kwargs.pop("angle")

        super().__init__()
        self.properties.update(**kwargs)

        if margin is not None:
            margin = Margin(self, **margin)  # type: ignore

        # Use the parameters that have been set
        names = (
            "backgroundcolor",
            "color",
            "family",
            "ha",
            "linespacing",
            "rotation",
            "size",
            "style",
            "va",
            "weight",
            "margin",
        )
        variables = locals()
        for name in names:
            if variables[name] is not None:
                self.properties[name] = variables[name]

    def setup(self, theme: Theme):
        """
        Setup the theme_element before drawing
        """
        if "margin" in self.properties:
            self.properties["margin"].theme = theme

    def _translate_hjust(
        self, just: float
    ) -> Literal["left", "right", "center"]:
        """
        Translate ggplot2 justification from [0, 1] to left, right, center.
        """
        if just == 0:
            return "left"
        elif just == 1:
            return "right"
        else:
            return "center"

    def _translate_vjust(
        self, just: float
    ) -> Literal["top", "bottom", "center"]:
        """
        Translate ggplot2 justification from [0, 1] to top, bottom, center.
        """
        if just == 0:
            return "bottom"
        elif just == 1:
            return "top"
        else:
            return "center"


class element_blank(element_base):
    """
    Theme element: Blank
    """

    def __init__(self):
        self.properties = {"visible": False}


@dataclass
class Margin:
    element: element_base
    theme: Optional[Theme] = None
    t: float = 0
    b: float = 0
    l: float = 0
    r: float = 0
    units: Literal["pt", "in", "lines", "fig"] = "pt"

    def __post_init__(self):
        if self.units in ("pts", "points", "px", "pixels"):
            self.units = "pt"
        elif self.units in ("in", "inch", "inches"):
            self.units = "in"
        elif self.units in ("line", "lines"):
            self.units = "lines"

    def __eq__(self, other: Any) -> bool:
        core = ("t", "b", "l", "r", "units")
        if self is other:
            return True

        if type(self) is not type(other):
            return False

        for attr in core:
            if getattr(self, attr) != getattr(other, attr):
                return False

        s_size = self.element.properties.get("size")
        o_size = other.element.properties.get("size")
        return s_size == o_size

    def get_as(
        self,
        loc: Literal["t", "b", "l", "r"],
        units: Literal["pt", "in", "lines", "fig"] = "pt",
    ) -> float:
        """
        Return key in given units
        """
        assert self.theme is not None
        dpi = 72
        # TODO: Get the inherited size. We need to consider the
        # themeables mro
        size: float = self.element.properties.get("size", 11)
        from_units = self.units
        to_units = units
        W: float
        H: float
        W, H = self.theme.themeables.property("figure_size")  # inches
        L = (W * dpi) if loc in "tb" else (H * dpi)  # pts

        functions: dict[str, Callable[[float], float]] = {
            "fig-in": lambda x: x * L / dpi,
            "fig-lines": lambda x: x * L / size,
            "fig-pt": lambda x: x * L,
            "in-fig": lambda x: x * dpi / L,
            "in-lines": lambda x: x * dpi / size,
            "in-pt": lambda x: x * dpi,
            "lines-fig": lambda x: x * size / L,
            "lines-in": lambda x: x * size / dpi,
            "lines-pt": lambda x: x * size,
            "pt-fig": lambda x: x / L,
            "pt-in": lambda x: x / dpi,
            "pt-lines": lambda x: x / size,
        }

        value: float = getattr(self, loc)
        if from_units != to_units:
            conversion = f"{self.units}-{units}"
            try:
                value = functions[conversion](value)
            except ZeroDivisionError:
                value = 0
        return value

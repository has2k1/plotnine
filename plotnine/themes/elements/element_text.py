"""
Theme elements used to decorate the graph.
"""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from .element_base import element_base
from .margin import Margin

if TYPE_CHECKING:
    from typing import Any, Literal, Optional, Sequence

    from plotnine import theme


class element_text(element_base):
    """
    Theme element: Text

    Parameters
    ----------
    family :
        Font family. See [](`~matplotlib.text.Text.set_family`)
        for supported values.
    style :
        Font style
    color :
        Text color
    weight :
        Should be one of `normal`, `bold`, `heavy`, `light`,
        `ultrabold` or `ultralight`.
    size :
        text size
    ha :
        Horizontal Alignment.
    va :
        Vertical alignment.
    ma :
        Horizontal Alignment for multiline text.
    rotation :
        Rotation angle in the range [0, 360]. The `rotation` is affected
        by the `rotation_mode`.
    rotation_mode :
        How to do the rotation. If `None` or `"default"`, first rotate
        the text then align the bounding box of the rotated text.
        If `"anchor"`, first align the unrotated text then rotate the
        text around the point of alignment.
    linespacing : float
        Line spacing
    backgroundcolor :
        Background color
    margin :
        Margin around the text. The keys are
        `t`, `b`, `l`, `r` and `units`.
        The `tblr` keys are floats.
        The `units` is one of `pt`, `lines` or `in`.
        Not all text themeables support margin parameters and other
        than the `units`, only some of the other keys may apply.
    kwargs :
        Parameters recognised by [](`~matplotlib.text.Text`)

    Notes
    -----
    [](`~plotnine.themes.element_text`) will accept parameters that
    conform to the **ggplot2** *element_text* API, but it is preferable
    the **Matplotlib** based API described above.
    """

    def __init__(
        self,
        family: Optional[str | list[str]] = None,
        style: Optional[str | Sequence[str]] = None,
        weight: Optional[int | str | Sequence[int | str]] = None,
        color: Optional[
            str
            | tuple[float, float, float]
            | tuple[float, float, float, float]
            | Sequence[
                str
                | tuple[float, float, float]
                | tuple[float, float, float, float]
            ]
        ] = None,
        size: Optional[float | Sequence[float]] = None,
        ha: Optional[Literal["center", "left", "right"] | float] = None,
        va: Optional[
            Literal["center", "top", "bottom", "baseline", "center_baseline"]
            | float
        ] = None,
        ma: Optional[Literal["center", "left", "right"] | float] = None,
        rotation: Optional[
            Literal["vertical", "horizontal"]
            | float
            | Sequence[Literal["vertical", "horizontal"]]
            | Sequence[float]
        ] = None,
        linespacing: Optional[float] = None,
        backgroundcolor: Optional[
            str
            | tuple[float, float, float]
            | tuple[float, float, float, float]
            | Sequence[
                str
                | tuple[float, float, float]
                | tuple[float, float, float, float]
            ]
        ] = None,
        margin: Optional[
            dict[Literal["t", "b", "l", "r", "units"], Any]
        ] = None,
        rotation_mode: Literal["default", "anchor"] | None = None,
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
            self.properties["margin"] = Margin(self, **margin)

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
            "rotation_mode",
        )
        variables = locals()
        for name in names:
            if variables[name] is not None:
                self.properties[name] = variables[name]

    def setup(self, theme: theme, themeable_name: str):
        """
        Setup the theme_element before drawing
        """
        if m := self.properties.get("margin"):
            m.theme = theme
            m.themeable_name = themeable_name

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

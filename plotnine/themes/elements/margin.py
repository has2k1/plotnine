"""
Margin
"""

from __future__ import annotations

from copy import copy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ...exceptions import PlotnineError

if TYPE_CHECKING:
    from typing import Callable, Literal

    from plotnine import theme


@dataclass
class margin:
    """
    Margin around a themeable

    Holds four edge values (top, right, bottom, left) in one of
    several coordinate spaces selected by the `unit` attribute.

    Notes
    -----
    Supported units:

    - `"pt"`: typographic points (1/72 in).
    - `"in"`: inches.
    - `"lines"`: multiples of the element's font size, applied
      uniformly to all four edges. One line equals `fontsize/72`
      inches of space on every edge — roughly a CSS em horizontally
      and fontsize-tall vertically, not a line-height-with-leading
      as the name may suggest.
    - `"fig"`: figure-fraction, interpreted per edge: top and bottom
      as a fraction of figure height, left and right as a fraction
      of figure width.

    For `pt`, `in`, and `lines`, equal edge values produce equal
    physical distances regardless of figure aspect ratio. For `fig`,
    top/bottom and left/right are fractions of different dimensions
    by design.
    """

    t: float = 0
    """
    Top margin
    """

    r: float = 0
    """
    Right margin
    """

    b: float = 0
    """
    Bottom margin
    """

    l: float = 0
    """
    Left Margin
    """

    unit: Literal["pt", "in", "lines", "fig"] = "pt"
    """
    Coordinate space of the edge values. See the class docstring
    for the meaning of each option.
    """

    # These are set by the themeable when it is applied
    fontsize: float = field(init=False, default=0)
    """
    Font size of text that this margin applies to
    """

    figure_size: tuple[float, float] = field(init=False, default=(0, 0))
    """
    Size of the figure in inches
    """

    _is_setup: bool = field(
        init=False, default=False, repr=False, compare=False
    )

    def setup(self, theme: theme, themeable_name: str):
        """
        Setup the margin to be used in the layout

        For the margin's values to be useful, we need to be able to
        convert them to different units as is required. Here we get
        all the parameters that we shall need to do the conversions.
        """
        self.fontsize = theme.getp((themeable_name, "size"), 11)
        self.figure_size = theme.getp("figure_size")
        self._is_setup = True

    @property
    def pt(self) -> margin:
        """
        Return margin in points

        These are the units of the display coordinate system
        """
        return self.to("pt")

    @property
    def inch(self) -> margin:
        """
        Return margin in inches

        These are the units of the figure-inches coordinate system
        """
        return self.to("in")

    @property
    def lines(self) -> margin:
        """
        Return margin in lines units
        """
        return self.to("lines")

    @property
    def fig(self) -> margin:
        """
        Return margin in figure units

        These are the units of the figure coordinate system
        """
        return self.to("fig")

    def to(self, unit: Literal["pt", "in", "lines", "fig"]) -> margin:
        """
        Return margin in request unit
        """
        if not self._is_setup:
            raise PlotnineError(
                "Cannot convert a margin that has not been set up. "
                "Call margin.setup() (or attach the margin to a "
                "themeable in a theme) first."
            )

        m = copy(self)
        if self.unit == unit:
            return m

        conversion = f"{self.unit}-{unit}"
        W, H = self.figure_size
        m.t = self._convert(conversion, H, self.t)
        m.r = self._convert(conversion, W, self.r)
        m.b = self._convert(conversion, H, self.b)
        m.l = self._convert(conversion, W, self.l)
        m.unit = unit
        return m

    def _convert(self, conversion: str, D: float, value: float) -> float:
        dpi = 72
        L = D * dpi  # pts

        functions: dict[str, Callable[[float], float]] = {
            "fig-in": lambda x: x * L / dpi,
            "fig-lines": lambda x: x * L / self.fontsize,
            "fig-pt": lambda x: x * L,
            "in-fig": lambda x: x * dpi / L,
            "in-lines": lambda x: x * dpi / self.fontsize,
            "in-pt": lambda x: x * dpi,
            "lines-fig": lambda x: x * self.fontsize / L,
            "lines-in": lambda x: x * self.fontsize / dpi,
            "lines-pt": lambda x: x * self.fontsize,
            "pt-fig": lambda x: x / L,
            "pt-in": lambda x: x / dpi,
            "pt-lines": lambda x: x / self.fontsize,
        }

        return functions[conversion](value)


def margin_auto(
    t: float = 0.0,
    r: float | None = None,
    b: float | None = None,
    l: float | None = None,
    unit: Literal["pt", "in", "lines", "fig"] = "pt",
) -> margin:
    """
    Create margin with minimal arguments
    """
    if r is None:
        r = t
    if b is None:
        b = t
    if l is None:
        l = r
    return margin(t, r, b, l, unit)

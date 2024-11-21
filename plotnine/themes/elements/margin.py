"""
Theme elements used to decorate the graph.
"""

from __future__ import annotations

from contextlib import suppress
from copy import copy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Literal

    from plotnine import theme


@dataclass
class margin:
    t: float = 0
    r: float = 0
    b: float = 0
    l: float = 0
    unit: Literal["pt", "in", "lines", "fig"] = "pt"

    # These are set by the themeable when it is applied
    fontsize: float = field(init=False, default=0)
    figure_size: tuple[float, float] = field(init=False, default=(0, 0))

    def setup(self, theme: theme, themeable_name: str):
        self.fontsize = theme.getp((themeable_name, "size"), 11)
        self.figure_size = theme.getp("figure_size")

    @property
    def pt(self) -> margin:
        """
        Return margin in points
        """
        return self.to("pt")

    @property
    def inch(self) -> margin:
        """
        Return margin in inches
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
        """
        return self.to("fig")

    def to(self, unit: Literal["pt", "in", "lines", "fig"]) -> margin:
        """
        Return margin in request unit
        """
        m = copy(self)
        if self.unit == unit:
            return m

        conversion = f"{self.unit}-{unit}"
        W, H = self.figure_size

        with suppress(ZeroDivisionError):
            m.t = self._convert(conversion, H, self.t)
        with suppress(ZeroDivisionError):
            m.r = self._convert(conversion, W, self.r)
        with suppress(ZeroDivisionError):
            m.b = self._convert(conversion, H, self.b)
        with suppress(ZeroDivisionError):
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

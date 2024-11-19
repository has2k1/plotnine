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

    def to(self, unit: Literal["pt", "in", "lines", "fig"]) -> margin:
        """
        Return margin in request unit
        """
        if self.unit == unit:
            return copy(self)

        conversion = f"{self.unit}-{unit}"
        W, H = self.figure_size

        t, r, b, l = 0, 0, 0, 0
        with suppress(ZeroDivisionError):
            t = self.convert(conversion, W, self.t)
        with suppress(ZeroDivisionError):
            r = self.convert(conversion, H, self.r)
        with suppress(ZeroDivisionError):
            b = self.convert(conversion, W, self.b)
        with suppress(ZeroDivisionError):
            l = self.convert(conversion, H, self.l)

        return margin(t, r, b, l, unit)

    def convert(self, conversion: str, D: float, value: float) -> float:
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

    def get_as(
        self,
        loc: Literal["t", "b", "l", "r"],
        units: Literal["pt", "in", "lines", "fig"] = "pt",
    ) -> float:
        """
        Return key in given units
        """
        dpi = 72
        size: float = self.fontsize
        from_units = self.unit
        to_units = units
        W: float
        H: float
        W, H = self.figure_size  # inches
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
            conversion = f"{from_units}-{to_units}"
            try:
                value = functions[conversion](value)
            except ZeroDivisionError:
                value = 0
        return value

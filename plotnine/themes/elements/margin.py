"""
Theme elements used to decorate the graph.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Literal

    from plotnine import theme

    from .element_base import element_base


@dataclass
class Margin:
    element: element_base
    t: float = 0
    b: float = 0
    l: float = 0
    r: float = 0
    units: Literal["pt", "in", "lines", "fig"] = "pt"

    def __post_init__(self):
        self.theme: theme
        self.themeable_name: str

        if self.units in ("pts", "points", "px", "pixels"):
            self.units = "pt"
        elif self.units in ("in", "inch", "inches"):
            self.units = "in"
        elif self.units in ("line", "lines"):
            self.units = "lines"

    def __eq__(self, other: object) -> bool:
        def _size(m: Margin):
            return m.element.properties.get("size")

        return other is self or (
            isinstance(other, type(self))
            and other.t == self.t
            and other.b == self.b
            and other.l == self.l
            and other.r == self.r
            and other.units == self.units
            and _size(other) == _size(self)
        )

    def get_as(
        self,
        loc: Literal["t", "b", "l", "r"],
        units: Literal["pt", "in", "lines", "fig"] = "pt",
    ) -> float:
        """
        Return key in given units
        """
        dpi = 72
        size: float = self.theme.getp((self.themeable_name, "size"), 11)
        from_units = self.units
        to_units = units
        W: float
        H: float
        W, H = self.theme.getp("figure_size")  # inches
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

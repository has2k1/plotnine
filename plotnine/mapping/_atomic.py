from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from typing import (
    Any,
    Generic,
    Literal,
    Sequence,
    TypeAlias,
    TypeVar,
)

import numpy as np
from mizani._colors.utils import is_color_tuple

# NOTE:For now we shall use these class privately and not list them
# in documentation. We can't deal with assigning Sequence[ae_value]
# to an aesthetic.

__all__ = (
    "linetype",
    "color",
    "colour",
    "fill",
    "shape",
)

T = TypeVar("T")

ShapeType: TypeAlias = (
    str | tuple[int, Literal[0, 1, 2], float] | Sequence[tuple[float, float]]
)


@dataclass
class ae_value(Generic[T]):
    """
    Atomic aesthetic value

    The goal of this base class is simplify working with the more complex
    aesthetic values. e.g. if a value is a tuple, we don't want it to be
    seen as a sequence of values when assigning it to a dataframe column.
    The subclasses should be able to recognise valid aesthetic values and
    repeat (using multiplication) the value any number of times.
    """

    value: T

    def __mul__(self, n: int) -> Sequence[T]:
        """
        Repeat value n times
        """
        return [self.value] * n


@dataclass
class linetype(ae_value[str | tuple]):
    """
    A single linetype value
    """

    def __post_init__(self):
        value = self.value
        named = {
            " ",
            "",
            "-",
            "--",
            "-.",
            ":",
            "None",
            "none",
            "dashdot",
            "dashed",
            "dotted",
            "solid",
        }
        if self.value in named:
            return

        # tuple of the form (offset, (on, off, on, off, ...))
        # e.g (0, (1, 2))
        if (
            isinstance(value, tuple)
            and isinstance(value[0], int)
            and isinstance(value[1], tuple)
            and len(value[1]) % 2 == 0
            and all(isinstance(x, int) for x in value[1])
        ):
            return

        raise ValueError(f"{value} is not a known linetype.")


@dataclass
class color(ae_value[str | tuple]):
    """
    A single color value
    """

    def __post_init__(self):
        if isinstance(self.value, str):
            return
        elif is_color_tuple(self.value):
            self.value = tuple(self.value)
            return

        raise ValueError(f"{self.value} is not a known color.")


colour = color


@dataclass
class fill(color):
    """
    A single color value
    """


@dataclass
class shape(ae_value[ShapeType]):
    """
    A single shape value
    """

    def __post_init__(self):
        from matplotlib.path import Path

        from ..scales.scale_shape import FILLED_SHAPES, UNFILLED_SHAPES

        value = self.value

        with suppress(TypeError):
            if value in (FILLED_SHAPES | UNFILLED_SHAPES):
                return

        if isinstance(value, Path):
            return

        # tuple of the form (numsides, style, angle)
        # where style is in the range [0, 3]
        # e.g (4, 1, 45)
        if (
            isinstance(value, tuple)
            and len(value) == 3
            and isinstance(value[0], int)
            and value[1] in (0, 1, 2)
            and isinstance(value[2], (float, int))
        ):
            return

        if is_shape_points(value):
            self.value = tuple(value)  # pyright: ignore[reportAttributeAccessIssue]
            return

        raise ValueError(f"{value} is not a known shape.")


def is_shape_points(obj: Any) -> bool:
    """
    Return True if obj is like Sequence[tuple[float, float]]
    """

    def is_numeric(obj) -> bool:
        """
        Return True if obj is a python or numpy float or integer
        """
        return isinstance(obj, (float, int, np.floating, np.integer))

    if not iter(obj):
        return False

    try:
        return all(is_numeric(a) and is_numeric(b) for a, b in obj)
    except (ValueError, TypeError):
        return False

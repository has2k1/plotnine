from __future__ import annotations

from dataclasses import KW_ONLY, InitVar, dataclass
from typing import Any, Sequence
from warnings import warn

from .._utils.registry import alias
from ..exceptions import PlotnineWarning
from .scale_discrete import scale_discrete


@dataclass
class _scale_manual(scale_discrete):
    """
    Abstract class for manual scales
    """

    values: InitVar[Sequence[Any] | dict[Any, Any]]
    """
    Exact values the scale should map to.
    """

    def __post_init__(self, values):
        from collections.abc import Sized

        super().__post_init__()

        if isinstance(self.breaks, Sized) and len(self.breaks) == len(values):
            values = dict(zip(self.breaks, values))

        def palette(n):
            max_n = len(values)
            if n > max_n:
                msg = (
                    f"The palette of {self.__class__.__name__} can return "
                    f"a maximum of {max_n} values. {n} were requested "
                    f"from it."
                )
                warn(msg, PlotnineWarning)
            return values

        # manual scales have a unique palette that return
        self.palette = palette  # type: ignore


@dataclass
class scale_color_manual(_scale_manual):
    """
    Custom discrete color scale
    """

    _aesthetics = ["color"]
    values: InitVar[Sequence[Any] | dict[Any, Any]]
    """
    Colors that make up the palette. The values will be matched with
    the `limits` of the scale or the `breaks` if provided.
    If it is a dict then it should map data values to colors.
    """
    _: KW_ONLY
    na_value: str = "#7F7F7F"


@dataclass
class scale_fill_manual(scale_color_manual):
    """
    Custom discrete fill scale
    """

    _aesthetics = ["fill"]


@dataclass
class scale_shape_manual(_scale_manual):
    """
    Custom discrete shape scale

    See Also
    --------
    [](`matplotlib.markers`)
    """

    _aesthetics = ["shape"]
    values: InitVar[Sequence[Any] | dict[Any, Any]]
    """
    Shapes that make up the palette. See [](`matplotlib.markers`) for list
    of all possible shapes. The values will be matched with the `limits`
    of the scale or the `breaks` if provided. If it is a dict then it
    should map data values to shapes.
    """


@dataclass
class scale_linetype_manual(_scale_manual):
    """
    Custom discrete linetype scale

    See Also
    --------
    [](`matplotlib.markers`)
    """

    values: InitVar[Sequence[Any] | dict[Any, Any]]
    """
    Linetypes that make up the palette. Possible values of the list are:

    1. Strings like

    ```python
    'solid'                # solid line
    'dashed'               # dashed line
    'dashdot'              # dash-dotted line
    'dotted'               # dotted line
    'None' or ' ' or ''    # draw nothing
    ```

    2. Tuples of the form (offset, (on, off, on, off, ....))
       e.g. (0, (1, 1)), (1, (2, 2)), (2, (5, 3, 1, 3))

    The values will be matched with the `limits` of the scale or the
    `breaks` if provided. If it is a dict then it should map data
    values to linetypes.
    """

    _aesthetics = ["linetype"]

    def map(self, x, limits=None):
        result = super().map(x, limits)
        # Ensure that custom linetypes are tuples, so that they can
        # be properly inserted and extracted from the dataframe
        if len(result) and hasattr(result[0], "__hash__"):
            result = [x if isinstance(x, str) else tuple(x) for x in result]
        return result


@dataclass
class scale_alpha_manual(_scale_manual):
    """
    Custom discrete alpha scale
    """

    _aesthetics = ["alpha"]
    values: InitVar[Sequence[Any] | dict[Any, Any]]
    """
    Alpha values (in the [0, 1] range) that make up the palette.
    The values will be matched with the `limits` of the scale or
    the `breaks` if provided. If it is a dict then it should map
    data values to alpha values.
    """


@dataclass
class scale_size_manual(_scale_manual):
    """
    Custom discrete size scale
    """

    _aesthetics = ["size"]
    values: InitVar[Sequence[Any] | dict[Any, Any]]
    """
    Sizes that make up the palette. The values will be matched
    with the `limits` of the scale or the `breaks` if provided.
    If it is a dict then it should map data values to sizes.
    """


# American to British spelling
@alias
class scale_colour_manual(scale_color_manual):
    pass

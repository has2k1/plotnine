from __future__ import annotations

import typing
from warnings import warn

from .._utils.registry import alias
from ..doctools import document
from ..exceptions import PlotnineWarning
from .scale_discrete import scale_discrete

if typing.TYPE_CHECKING:
    from plotnine.typing import ScaleBreaksRaw


@document
class _scale_manual(scale_discrete):
    """
    Abstract class for manual scales

    Parameters
    ----------
    {superclass_parameters}
    """

    def __init__(self, values, **kwargs):
        # Match the values of the scale with the breaks (if given)
        if "breaks" in kwargs:
            from collections.abc import Sized

            breaks: ScaleBreaksRaw = kwargs["breaks"]
            if isinstance(breaks, Sized) and len(breaks) == len(values):
                values = dict(zip(breaks, values))

        self._values = values
        scale_discrete.__init__(self, **kwargs)

    def palette(self, value):
        max_n = len(self._values)
        if value > max_n:
            msg = (
                f"The palette of {self.__class__.__name__} can return a "
                f"maximum of {max_n} values. {value} were requested from it."
            )
            warn(msg, PlotnineWarning)
        return self._values


@document
class scale_color_manual(_scale_manual):
    """
    Custom discrete color scale

    Parameters
    ----------
    values : array_like | dict
        Colors that make up the palette. The values will be matched with
        the `limits` of the scale or the `breaks` if provided.
        If it is a dict then it should map data values to colors.

    {superclass_parameters}
    """

    _aesthetics = ["color"]
    na_value = "#7F7F7F"


@document
class scale_fill_manual(_scale_manual):
    """
    Custom discrete fill scale

    Parameters
    ----------
    values : array_like | dict
        Colors that make up the palette. The values will be matched with
        the `limits` of the scale or the `breaks` if provided.
        If it is a dict then it should map data values to colors.
    {superclass_parameters}
    """

    _aesthetics = ["fill"]
    na_value = "#7F7F7F"


@document
class scale_shape_manual(_scale_manual):
    """
    Custom discrete shape scale

    Parameters
    ----------
    values : array_like | dict
        Shapes that make up the palette. See
        :mod:`matplotlib.markers.` for list of all possible
        shapes. The values will be matched with the `limits`
        of the scale or the `breaks` if provided.
        If it is a dict then it should map data values to shapes.
    {superclass_parameters}

    See Also
    --------
    :mod:`matplotlib.markers`
    """

    _aesthetics = ["shape"]


@document
class scale_linetype_manual(_scale_manual):
    """
    Custom discrete linetype scale

    Parameters
    ----------
    values : list | dict
        Linetypes that make up the palette.
        Possible values of the list are:

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

        The values will be matched with the `limits` of the scale
        or the `breaks` if provided.
        If it is a dict then it should map data values to linetypes.
    {superclass_parameters}

    See Also
    --------
    :mod:`matplotlib.markers`
    """

    _aesthetics = ["linetype"]

    def map(self, x, limits=None):
        result = super().map(x, limits)
        # Ensure that custom linetypes are tuples, so that they can
        # be properly inserted and extracted from the dataframe
        if len(result) and hasattr(result[0], "__hash__"):
            result = [x if isinstance(x, str) else tuple(x) for x in result]
        return result


@document
class scale_alpha_manual(_scale_manual):
    """
    Custom discrete alpha scale

    Parameters
    ----------
    values : array_like | dict
        Alpha values (in the [0, 1] range) that make up
        the palette. The values will be matched with the
        `limits` of the scale or the `breaks` if provided.
        If it is a dict then it should map data values to alpha
        values.
    {superclass_parameters}
    """

    _aesthetics = ["alpha"]


@document
class scale_size_manual(_scale_manual):
    """
    Custom discrete size scale

    Parameters
    ----------
    values : array_like | dict
        Sizes that make up the palette. The values will be matched
        with the `limits` of the scale or the `breaks` if provided.
        If it is a dict then it should map data values to sizes.
    {superclass_parameters}
    """

    _aesthetics = ["size"]


# American to British spelling
class scale_colour_manual(scale_color_manual, alias):
    pass

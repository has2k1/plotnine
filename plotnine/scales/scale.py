from __future__ import annotations

import typing
from abc import ABC
from copy import copy, deepcopy
from warnings import warn

import numpy as np
from mizani.palettes import identity_pal

from .._utils.registry import Register
from ..exceptions import PlotnineError, PlotnineWarning
from ..mapping.aes import is_position_aes, rename_aesthetics
from .range import Range

if typing.TYPE_CHECKING:
    from typing import Any, Literal, Optional

    import pandas as pd
    from numpy.typing import NDArray

    from plotnine.typing import (
        ScaleBreaks,
        ScaledAestheticsName,
        ScaleLabels,
        ScaleLabelsRaw,
        ScaleLimits,
        TupleFloat2,
        TupleFloat4,
    )

    from ..iapi import range_view, scale_view


class scale(ABC, metaclass=Register):
    """
    Base class for all scales

    Parameters
    ----------
    breaks : bool | list | callable, default=True
        List of major break points. Or a callable that
        takes a tuple of limits and returns a list of breaks.
        If `True`, automatically calculate the breaks.
    expand : tuple, default=None
        Multiplicative and additive expansion constants
        that determine how the scale is expanded. If
        specified must be of length 2 or 4. Specifically the
        values are in this order:

        ```
        (mul, add)
        (mul_low, add_low, mul_high, add_high)
        ```

        For example,

        - `(0, 0)` - Do not expand.
        - `(0, 1)` - Expand lower and upper limits by 1 unit.
        - `(1, 0)` - Expand lower and upper limits by 100%.
        - `(0, 0, 0, 0)` - Do not expand, as `(0, 0)`.
        - `(0, 0, 0, 1)` - Expand upper limit by 1 unit.
        - `(0, 1, 0.1, 0)` - Expand lower limit by 1 unit and
          upper limit by 10%.
        - `(0, 0, 0.1, 2)` - Expand upper limit by 10% plus
          2 units.

        If not specified, suitable defaults are chosen.
    name : str, default=None
        Name used as the label of the scale. This is what
        shows up as the axis label or legend title. Suitable
        defaults are chosen depending on the type of scale.
    labels : bool | list | callable, default=True
        List of [](`str`). Labels at the `breaks`.
        Alternatively, a callable that takes an array_like of
        break points as input and returns a list of strings.
    limits : array_like, default=None
        Limits of the scale. Most commonly, these are the
        min & max values for the scales. For scales that
        deal with categoricals, these may be a subset or
        superset of the categories.
    na_value : scalar, default=float("nan")
        What value to assign to missing values. Default
        is to assign `np.nan`.
    palette : callable, default=None
        Function to map data points onto the scale. Most
        scales define their own palettes.
    aesthetics : list | str, default=None
        list of [](`str`). Aesthetics covered by the
        scale. These are defined by each scale and the
        user should probably not change them. Have fun.
    """

    # major breaks
    breaks = True

    # aesthetics affected by this scale
    _aesthetics: list[ScaledAestheticsName] = []

    # What to do with the NA values
    na_value: Any = np.nan

    # used as the axis label or legend title
    name: str | None = None

    # labels at the breaks
    labels: ScaleLabelsRaw = True

    # legend or any other guide
    guide: Optional[Literal["legend", "colorbar"]] = "legend"

    # (min, max) - set by user
    _limits = None

    # multiplicative and additive expansion constants
    expand: Optional[TupleFloat2 | TupleFloat4] = None

    # range class for the aesthetic
    _range_class: type[Range] = Range

    # Default palette
    _palette = identity_pal()

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                msg = "{} could not recognise parameter `{}`"
                warn(msg.format(self.__class__.__name__, k), PlotnineWarning)

        self.range = self._range_class()

        if (
            np.iterable(self.breaks)
            and np.iterable(self.labels)
            and len(self.breaks) != len(self.labels)  # type: ignore
        ):
            raise PlotnineError("Breaks and labels have unequal lengths")

        if (
            self.breaks is None
            and not is_position_aes(self.aesthetics)
            and self.guide is not None
        ):
            self.guide = None

    @property
    def aesthetics(self):
        return self._aesthetics

    @aesthetics.setter
    def aesthetics(self, value):
        if isinstance(value, str):
            value = [value]
        # TODO: Find a way to make the type checking work
        self._aesthetics = rename_aesthetics(value)  # pyright: ignore

    def __radd__(self, plot):
        """
        Add this scale to ggplot object
        """
        plot.scales.append(copy(self))
        return plot

    def palette(self, value):
        """
        Aesthetic mapping function

        Note that not all scales need to implement/provide a palette.
        For example identity & position scales do not use a palette.
        """
        return self._palette(value)  # type: ignore

    def map(self, x, limits=None):
        """
        Map every element of x

        The palette should do the real work, this should
        make sure that sensible values are sent and
        return from the palette.
        """
        raise NotImplementedError

    def train(self, x: pd.Series | NDArray):
        """
        Train scale

        Parameters
        ----------
        x :
            A column of data to train over
        """
        raise NotImplementedError

    def dimension(self, expand=None, limits=None):
        """
        Get the phyical size of the scale.
        """
        raise NotImplementedError

    def expand_limits(
        self,
        limits,  # : ScaleLimits
        expand,  # : TupleFloat2 | TupleFloat4
        coord_limits,  # : CoordRange | None
        trans,  # : Trans | Type[Trans]
    ) -> range_view:
        """
        Exand the limits of the scale
        """
        raise NotImplementedError

    def transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform dataframe
        """
        raise NotImplementedError

    def transform(self, x):
        """
        Transform array|series x
        """
        raise NotImplementedError

    def inverse_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Inverse transform dataframe
        """
        raise NotImplementedError

    def inverse(self, x):
        """
        Inverse transform array|series x
        """
        raise NotImplementedError

    def view(
        self,
        limits=None,  # : Optional[ScaleLimits]
        range=None,  # : Optional[CoordRange] = None
    ) -> scale_view:
        """
        Information about the trained scale
        """
        raise NotImplementedError

    def default_expansion(
        self,
        mult: float | TupleFloat2 = 0,
        add: float | TupleFloat2 = 0,
        expand=True,
    ) -> TupleFloat4:
        """
        Get default expansion for this scale
        """
        if not expand:
            return (0, 0, 0, 0)

        if self.expand:
            if len(self.expand) == 2:
                mult, add = self.expand
            else:
                # n == 4:
                mult = self.expand[0], self.expand[2]
                add = self.expand[1], self.expand[3]

        if isinstance(mult, (float, int)):
            mult = (mult, mult)

        if isinstance(add, (float, int)):
            add = (add, add)

        if len(mult) != 2:
            raise ValueError(
                "The scale expansion multiplication factor should "
                "either be a single float, or a tuple of two floats. "
            )

        if len(add) != 2:
            raise ValueError(
                "The scale expansion addition constant should "
                "either be a single float, or a tuple of two floats. "
            )

        return (mult[0], add[0], mult[1], add[1])

    def clone(self):
        return deepcopy(self)

    def reset(self):
        """
        Set the range of the scale to None.

        i.e Forget all the training
        """
        self.range.reset()

    def is_empty(self) -> bool:
        """
        Whether the scale has size information
        """
        if not hasattr(self, "range"):
            return True
        return self.range.is_empty() and self._limits is None

    @property
    def limits(self) -> ScaleLimits:
        raise NotImplementedError

    @limits.setter
    def limits(
        self,
        value,  # : ScaleLimitsRaw
    ):
        raise NotImplementedError

    def train_df(self, df: pd.DataFrame):
        """
        Train scale from a dataframe
        """
        aesthetics = sorted(set(self.aesthetics) & set(df.columns))
        for ae in aesthetics:
            self.train(df[ae])

    def map_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Map df
        """
        if len(df) == 0:
            return df

        aesthetics = set(self.aesthetics) & set(df.columns)
        for ae in aesthetics:
            df[ae] = self.map(df[ae])

        return df

    def get_labels(
        self,
        breaks=None,  # : Optional[ScaleBreaks]
    ) -> ScaleLabels:
        """
        Get labels, calculating them if required
        """
        raise NotImplementedError

    def get_breaks(
        self,
        limits=None,  # : Optional[ScaleLimits]
    ) -> ScaleBreaks:
        """
        Get Breaks
        """
        raise NotImplementedError

    def get_bounded_breaks(
        self,
        limits=None,  # : Optional[ScaleLimits]
    ) -> ScaleBreaks:
        """
        Return Breaks that are within the limits
        """
        raise NotImplementedError

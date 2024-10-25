from __future__ import annotations

from abc import ABC
from copy import copy, deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Generic, cast

import numpy as np

from .._utils.registry import Register
from ..exceptions import PlotnineError
from ..mapping.aes import is_position_aes, rename_aesthetics
from ._runtime_typing import (
    BreaksUserT,
    GuideTypeT,
    LimitsUserT,
    RangeT,
    ScaleLabelsUser,
)

if TYPE_CHECKING:
    from typing import Any, Sequence

    import pandas as pd
    from numpy.typing import NDArray

    from plotnine.typing import ScaledAestheticsName

    from ..iapi import range_view, scale_view


@dataclass(kw_only=True)
class scale(
    Generic[RangeT, BreaksUserT, LimitsUserT, GuideTypeT],
    ABC,
    metaclass=Register,
):
    """
    Base class for all scales
    """

    name: str | None = None
    """
    The name of the scale. It is used as the label of the axis or the
    title of the guide. Suitable defaults are chosen depending on
    the type of scale.
    """

    # # major breaks
    breaks: BreaksUserT
    """
    List of major break points. Or a callable that takes a tuple of limits
    and returns a list of breaks. If `True`, automatically calculate the
    breaks.
    """

    limits: LimitsUserT
    """
    Limits of the scale. Most commonly, these are the min & max values
    for the scales. For scales that deal with categoricals, these may be a
    subset or superset of the categories.
    """

    # labels at the breaks
    labels: ScaleLabelsUser = True
    """
    Labels at the `breaks`. Alternatively, a callable that takes an
    array_like of break points as input and returns a list of strings.
    """

    # multiplicative and additive expansion constants
    # fmt: off
    expand: (
        tuple[float, float]
        | tuple[float, float, float, float]
        | None
    ) = None
    # fmt: on

    """
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
    """

    # legend or any other guide
    guide: GuideTypeT
    """
    Whether to include a legend
    """

    # What to do with the NA values
    na_value: Any = np.nan
    """
    What value to assign to missing values. Default
    is to assign `np.nan`.
    """

    aesthetics: Sequence[ScaledAestheticsName] = ()
    """
    Aesthetics affected by this scale. These are defined by each scale
    and the user should probably not change them. Have fun.
    """

    _range: RangeT = field(init=False, repr=False)

    # Defined aesthetics for the scale
    _aesthetics: Sequence[ScaledAestheticsName] = field(init=False, repr=False)

    def __post_init__(self):
        breaks = getattr(self, "breaks")

        if (
            np.iterable(breaks)
            and np.iterable(self.labels)
            and len(self.breaks) != len(self.labels)  # type: ignore
        ):
            raise PlotnineError("Breaks and labels have unequal lengths")

        if (
            breaks is None
            and not is_position_aes(self.aesthetics)
            and self.guide is not None
        ):
            self.guide = None  # pyright: ignore

        self.aesthetics = rename_aesthetics(
            self.aesthetics if self.aesthetics else self._aesthetics
        )

    def __radd__(self, plot):
        """
        Add this scale to ggplot object
        """
        plot.scales.append(copy(self))
        return plot

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
        expand,  # : tuple[float, float] | tuple[float, float, float, float]
        coord_limits,  # : CoordRange | None
        trans,  # : Trans | Type[Trans]
    ) -> range_view:
        """
        Expand the limits of the scale
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
        mult: float | tuple[float, float] = 0,
        add: Any | tuple[Any, Any] = 0,
        expand=True,
    ) -> tuple[float, float, float, float]:
        """
        Get default expansion for this scale
        """
        if not expand:
            return (0, 0, 0, 0)

        if not (exp := self.expand):
            m1, m2 = mult if isinstance(mult, (tuple, list)) else (mult, mult)
            a1, a2 = cast(
                tuple[float, float],
                (add if isinstance(add, (tuple, list)) else (add, add)),
            )
            exp = (m1, a1, m2, a2)
        elif len(exp) == 2:
            exp = (*exp, *exp)

        return exp

    def clone(self):
        return deepcopy(self)

    def reset(self):
        """
        Set the range of the scale to None.

        i.e Forget all the training
        """
        self._range.reset()

    def is_empty(self) -> bool:
        """
        Whether the scale has size information
        """
        if not hasattr(self, "_range"):
            return True
        return self._range.is_empty() and self.limits is None

    @property
    def final_limits(self) -> Any:
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

    def get_labels(self, breaks=None) -> Sequence[str]:
        """
        Get labels, calculating them if required
        """
        raise NotImplementedError

    def get_breaks(self, limits=None):
        """
        Get Breaks
        """
        raise NotImplementedError

    def get_bounded_breaks(self, limits=None):
        """
        Return Breaks that are within the limits
        """
        raise NotImplementedError

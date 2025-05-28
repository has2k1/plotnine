from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from .._utils import array_kind, match
from .._utils.registry import alias
from ..exceptions import PlotnineError
from ..iapi import range_view
from ._expand import expand_range
from ._runtime_typing import TransUser  # noqa: TCH001
from .range import RangeContinuous
from .scale_continuous import scale_continuous
from .scale_datetime import scale_datetime
from .scale_discrete import scale_discrete

if TYPE_CHECKING:
    from typing import Sequence

    from mizani.transforms import trans


# positions scales have a couple of differences (quirks) that
# make necessary to override some of the scale_discrete and
# scale_continuous methods
#
# scale_position_discrete and scale_position_continuous
# are intermediate base classes where the required overriding
# is done
@dataclass(kw_only=True)
class scale_position_discrete(scale_discrete):
    """
    Base class for discrete position scales
    """

    def __post_init__(self):
        super().__post_init__()
        # Keeps two ranges, range and range_c
        self._range_c = RangeContinuous()
        if isinstance(self.limits, tuple):
            self.limits = list(self.limits)

        # All positions have no guide
        self.guide = None

    def reset(self):
        # Can't reset discrete scale because
        # no way to recover values
        self._range_c.reset()

    def is_empty(self) -> bool:
        return super().is_empty() and self._range_c.is_empty()

    def train(self, x, drop=False):
        # The discrete position scale is capable of doing
        # training for continuous data.
        # This complicates training and mapping, but makes it
        # possible to place objects at non-integer positions,
        # as is necessary for jittering etc.
        if array_kind.continuous(x):
            self._range_c.train(x)
        else:
            self._range.train(x, drop=self.drop)

    def map(self, x, limits=None):
        # Discrete values are converted into integers starting
        # at 1
        if limits is None:
            limits = self.final_limits
        if array_kind.discrete(x):
            # TODO: Rewrite without using numpy
            seq = np.arange(1, len(limits) + 1)
            idx = np.asarray(match(x, limits, nomatch=len(x)))
            if not len(idx):
                return []
            try:
                seq = seq[idx]
            except IndexError:
                # Deal with missing data
                # - Insert NaN where there is no match
                seq = np.hstack((seq.astype(float), np.nan))
                idx = np.clip(idx, 0, len(seq) - 1)
                seq = seq[idx]
            return list(seq)
        return list(x)

    @property
    def final_limits(self):
        if self.is_empty():
            return (0, 1)
        elif self.limits is not None and not callable(self.limits):
            return self.limits
        elif self.limits is None:
            # discrete range
            return self._range.range
        elif callable(self.limits):
            limits = self.limits(self._range.range)
            # Functions that return iterators e.g. reversed
            if iter(limits) is limits:
                limits = list(limits)
            return limits
        else:
            raise PlotnineError("Lost, do not know what the limits are.")

    def dimension(self, expand=(0, 0, 0, 0), limits=None):
        """
        Get the phyical size of the scale

        Unlike limits, this always returns a numeric vector of length 2
        """
        from mizani.bounds import expand_range_distinct

        if limits is None:
            limits = self.final_limits

        if self.is_empty():
            return (0, 1)

        if self._range.is_empty():  # only continuous
            return expand_range_distinct(self._range_c.range, expand)
        elif self._range_c.is_empty():  # only discrete
            # FIXME: I think this branch should not exist
            return expand_range_distinct((1, len(self.final_limits)), expand)
        else:  # both
            # e.g categorical bar plot have discrete items, but
            # are plot on a continuous x scale
            a = np.hstack(
                [
                    self._range_c.range,
                    expand_range_distinct((1, len(self._range.range)), expand),
                ]
            )
            return a.min(), a.max()

    def expand_limits(
        self,
        limits: Sequence[str],
        expand: tuple[float, float] | tuple[float, float, float, float],
        coord_limits: tuple[float, float],
        trans: trans,
    ) -> range_view:
        # Turn discrete limits into a tuple of continuous limits
        if self.is_empty():
            climits = (0, 1)
        else:
            climits = (1, len(limits))
            self._range_c.range

        if coord_limits is not None:
            # - Override None in coord_limits
            # - Expand limits in coordinate space
            # - Remove any computed infinite values &
            c0, c1 = coord_limits
            climits = (
                climits[0] if c0 is None else c0,
                climits[1] if c1 is None else c1,
            )

        # Expand discrete range
        rv_d = expand_range(climits, expand, trans)

        if self._range_c.is_empty():
            return rv_d

        # Expand continuous range
        no_expand = self.default_expansion(0, 0)
        rv_c = expand_range(self._range_c.range, no_expand, trans)

        # Merge the ranges
        rv = range_view(
            range=(
                min(chain(rv_d.range, rv_c.range)),
                max(chain(rv_d.range, rv_c.range)),
            ),
            range_coord=(
                min(chain(rv_d.range_coord, rv_c.range_coord)),
                max(chain(rv_d.range_coord, rv_c.range_coord)),
            ),
        )
        rv.range = min(rv.range), max(rv.range)
        rv.range_coord = min(rv.range_coord), max(rv.range_coord)
        return rv


@dataclass(kw_only=True)
class scale_position_continuous(scale_continuous[None]):
    """
    Base class for continuous position scales
    """

    guide: None = None

    def map(self, x, limits=None):
        # Position aesthetics don't map, because the coordinate
        # system takes care of it.
        # But the continuous scale has to deal with out of bound points
        if not len(x):
            return x
        if limits is None:
            limits = self.final_limits
        scaled = self.oob(x, limits)  # type: ignore
        scaled[pd.isna(scaled)] = self.na_value
        return scaled


@dataclass(kw_only=True)
class scale_x_discrete(scale_position_discrete):
    """
    Discrete x position
    """

    _aesthetics = ["x", "xmin", "xmax", "xend", "xintercept"]


@dataclass(kw_only=True)
class scale_y_discrete(scale_position_discrete):
    """
    Discrete y position
    """

    _aesthetics = ["y", "ymin", "ymax", "yend", "yintercept"]


# Not part of the user API
@alias
class scale_x_ordinal(scale_x_discrete):
    pass


@alias
class scale_y_ordinal(scale_y_discrete):
    pass


@dataclass(kw_only=True)
class scale_x_continuous(scale_position_continuous):
    """
    Continuous x position
    """

    _aesthetics = ["x", "xmin", "xmax", "xend", "xintercept"]


@dataclass(kw_only=True)
class scale_y_continuous(scale_position_continuous):
    """
    Continuous y position
    """

    _aesthetics = [
        "y",
        "ymin",
        "ymax",
        "yend",
        "yintercept",
        "ymin_final",
        "ymax_final",
        "lower",
        "middle",
        "upper",
    ]


# Transformed scales
@dataclass(kw_only=True)
class scale_x_datetime(scale_datetime, scale_x_continuous):  # pyright: ignore[reportIncompatibleVariableOverride]
    """
    Continuous x position for datetime data points
    """

    guide: None = None


@dataclass(kw_only=True)
class scale_y_datetime(scale_datetime, scale_y_continuous):  # pyright: ignore[reportIncompatibleVariableOverride]
    """
    Continuous y position for datetime data points
    """

    guide: None = None


@alias
class scale_x_date(scale_x_datetime):
    pass


@alias
class scale_y_date(scale_y_datetime):
    pass


@dataclass(kw_only=True)
class scale_x_timedelta(scale_x_continuous):
    """
    Continuous x position for timedelta data points
    """

    trans: TransUser = "pd_timedelta"


@dataclass(kw_only=True)
class scale_y_timedelta(scale_y_continuous):
    """
    Continuous y position for timedelta data points
    """

    trans: TransUser = "pd_timedelta"


@dataclass(kw_only=True)
class scale_x_sqrt(scale_x_continuous):
    """
    Continuous x position sqrt transformed scale
    """

    trans: TransUser = "sqrt"


@dataclass(kw_only=True)
class scale_y_sqrt(scale_y_continuous):
    """
    Continuous y position sqrt transformed scale
    """

    trans: TransUser = "sqrt"


@dataclass(kw_only=True)
class scale_x_log10(scale_x_continuous):
    """
    Continuous x position log10 transformed scale
    """

    trans: TransUser = "log10"


@dataclass(kw_only=True)
class scale_y_log10(scale_y_continuous):
    """
    Continuous y position log10 transformed scale
    """

    trans: TransUser = "log10"


@dataclass(kw_only=True)
class scale_x_reverse(scale_x_continuous):
    """
    Continuous x position reverse transformed scale
    """

    trans: TransUser = "reverse"


@dataclass(kw_only=True)
class scale_y_reverse(scale_y_continuous):
    """
    Continuous y position reverse transformed scale
    """

    trans: TransUser = "reverse"


@dataclass(kw_only=True)
class scale_x_symlog(scale_x_continuous):
    """
    Continuous x position symmetric logarithm transformed scale
    """

    trans: TransUser = "symlog"


@dataclass(kw_only=True)
class scale_y_symlog(scale_y_continuous):
    """
    Continuous y position symmetric logarithm transformed scale
    """

    trans: TransUser = "symlog"

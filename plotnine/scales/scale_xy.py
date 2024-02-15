from __future__ import annotations

import typing
from itertools import chain

import numpy as np
import pandas as pd

from .._utils import array_kind, match
from .._utils.registry import alias
from ..doctools import document
from ..exceptions import PlotnineError
from ..iapi import range_view
from ._expand import expand_range
from .range import RangeContinuous
from .scale_continuous import scale_continuous
from .scale_datetime import scale_datetime
from .scale_discrete import scale_discrete

if typing.TYPE_CHECKING:
    from typing import Sequence

    from mizani.transforms import trans

    from plotnine.typing import TupleFloat2, TupleFloat4


# positions scales have a couple of differences (quirks) that
# make necessary to override some of the scale_discrete and
# scale_continuous methods
#
# scale_position_discrete and scale_position_continuous
# are intermediate base classes where the required overriding
# is done
@document
class scale_position_discrete(scale_discrete):
    """
    Base class for discrete position scales

    Parameters
    ----------
    {superclass_parameters}
    limits : array_like, default=None
        Limits of the scale. For discrete scale, these are
        the categories (unique values) of the variable.
        For scales that deal with categoricals, these may
        be a subset or superset of the categories.
    """

    # All positions have no guide
    guide = None

    # Keeps two ranges, range and range_c
    range_c: RangeContinuous

    def __init__(self, *args, **kwargs):
        self.range_c = RangeContinuous()
        scale_discrete.__init__(self, *args, **kwargs)

    def reset(self):
        # Can't reset discrete scale because
        # no way to recover values
        self.range_c.reset()

    def is_empty(self) -> bool:
        return super().is_empty() and self.range_c.is_empty()

    def train(self, x, drop=False):
        # The discrete position scale is capable of doing
        # training for continuous data.
        # This complicates training and mapping, but makes it
        # possible to place objects at non-integer positions,
        # as is necessary for jittering etc.
        if array_kind.continuous(x):
            self.range_c.train(x)
        else:
            self.range.train(x, drop=self.drop)

    def map(self, x, limits=None):
        # Discrete values are converted into integers starting
        # at 1
        if limits is None:
            limits = self.limits
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
    def limits(self):
        if self.is_empty():
            return (0, 1)
        elif self._limits is not None and not callable(self._limits):
            return self._limits
        elif self._limits is None:
            # discrete range
            return self.range.range
        elif callable(self._limits):
            limits = self._limits(self.range.range)
            # Functions that return iterators e.g. reversed
            if iter(limits) is limits:
                limits = list(limits)
            return limits
        else:
            raise PlotnineError("Lost, do not know what the limits are.")

    @limits.setter
    def limits(self, value):
        if isinstance(value, tuple):
            value = list(value)
        self._limits = value

    def dimension(self, expand=(0, 0, 0, 0), limits=None):
        """
        Get the phyical size of the scale

        Unlike limits, this always returns a numeric vector of length 2
        """
        from mizani.bounds import expand_range_distinct

        if limits is None:
            limits = self.limits

        if self.is_empty():
            return (0, 1)

        if self.range.is_empty():  # only continuous
            return expand_range_distinct(self.range_c.range, expand)
        elif self.range_c.is_empty():  # only discrete
            # FIXME: I think this branch should not exist
            return expand_range_distinct((1, len(self.limits)), expand)
        else:  # both
            # e.g categorical bar plot have discrete items, but
            # are plot on a continuous x scale
            a = np.hstack(
                [
                    self.range_c.range,
                    expand_range_distinct((1, len(self.range.range)), expand),
                ]
            )
            return a.min(), a.max()

    def expand_limits(
        self,
        limits: Sequence[str],
        expand: TupleFloat2 | TupleFloat4,
        coord_limits: TupleFloat2,
        trans: trans,
    ) -> range_view:
        # Turn discrete limits into a tuple of continuous limits
        if self.is_empty():
            climits = (0, 1)
        else:
            climits = (1, len(limits))
            self.range_c.range

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

        if self.range_c.is_empty():
            return rv_d

        # Expand continuous range
        no_expand = self.default_expansion(0, 0)
        rv_c = expand_range(self.range_c.range, no_expand, trans)

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


@document
class scale_position_continuous(scale_continuous):
    """
    Base class for continuous position scales

    Parameters
    ----------
    {superclass_parameters}
    """

    # All positions have no guide
    guide = None

    def map(self, x, limits=None):
        # Position aesthetics don't map, because the coordinate
        # system takes care of it.
        # But the continuous scale has to deal with out of bound points
        if not len(x):
            return x
        if limits is None:
            limits = self.limits
        scaled = self.oob(x, limits)  # type: ignore
        scaled[pd.isna(scaled)] = self.na_value
        return scaled


@document
class scale_x_discrete(scale_position_discrete):
    """
    Discrete x position

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["x", "xmin", "xmax", "xend"]


@document
class scale_y_discrete(scale_position_discrete):
    """
    Discrete y position

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["y", "ymin", "ymax", "yend"]


# Not part of the user API
@alias
class scale_x_ordinal(scale_x_discrete):
    pass


@alias
class scale_y_ordinal(scale_y_discrete):
    pass


@document
class scale_x_continuous(scale_position_continuous):
    """
    Continuous x position

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["x", "xmin", "xmax", "xend", "xintercept"]


@document
class scale_y_continuous(scale_position_continuous):
    """
    Continuous y position

    Parameters
    ----------
    {superclass_parameters}
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
    ]  # pyright: ignore


# Transformed scales
@document
class scale_x_datetime(scale_datetime, scale_x_continuous):
    """
    Continuous x position for datetime data points

    Parameters
    ----------
    {superclass_parameters}
    """


@document
class scale_y_datetime(scale_datetime, scale_y_continuous):
    """
    Continuous y position for datetime data points

    Parameters
    ----------
    {superclass_parameters}
    """


@alias
class scale_x_date(scale_x_datetime):
    pass


@alias
class scale_y_date(scale_y_datetime):
    pass


@document
class scale_x_timedelta(scale_x_continuous):
    """
    Continuous x position for timedelta data points

    Parameters
    ----------
    {superclass_parameters}
    """

    _trans = "pd_timedelta"


@document
class scale_y_timedelta(scale_y_continuous):
    """
    Continuous y position for timedelta data points

    Parameters
    ----------
    {superclass_parameters}
    """

    _trans = "pd_timedelta"


@document
class scale_x_sqrt(scale_x_continuous):
    """
    Continuous x position sqrt transformed scale

    Parameters
    ----------
    {superclass_parameters}
    """

    _trans = "sqrt"


@document
class scale_y_sqrt(scale_y_continuous):
    """
    Continuous y position sqrt transformed scale

    Parameters
    ----------
    {superclass_parameters}
    """

    _trans = "sqrt"


@document
class scale_x_log10(scale_x_continuous):
    """
    Continuous x position log10 transformed scale

    Parameters
    ----------
    {superclass_parameters}
    """

    _trans = "log10"


@document
class scale_y_log10(scale_y_continuous):
    """
    Continuous y position log10 transformed scale

    Parameters
    ----------
    {superclass_parameters}
    """

    _trans = "log10"


@document
class scale_x_reverse(scale_x_continuous):
    """
    Continuous x position reverse transformed scale

    Parameters
    ----------
    {superclass_parameters}
    """

    _trans = "reverse"


@document
class scale_y_reverse(scale_y_continuous):
    """
    Continuous y position reverse transformed scale

    Parameters
    ----------
    {superclass_parameters}
    """

    _trans = "reverse"


@document
class scale_x_symlog(scale_x_continuous):
    """
    Continuous x position symmetric logarithm transformed scale

    Parameters
    ----------
    {superclass_parameters}
    """

    _trans = "symlog"


@document
class scale_y_symlog(scale_y_continuous):
    """
    Continuous y position symmetric logarithm transformed scale

    Parameters
    ----------
    {superclass_parameters}
    """

    _trans = "symlog"

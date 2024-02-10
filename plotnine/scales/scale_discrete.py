from __future__ import annotations

import typing

import numpy as np
import pandas as pd
from mizani.bounds import expand_range_distinct

from .._utils import match
from ..doctools import document
from ..iapi import range_view, scale_view
from ._expand import expand_range
from .range import RangeDiscrete
from .scale import scale

if typing.TYPE_CHECKING:
    from typing import Any, Optional, Sequence

    from mizani.transforms import trans

    from plotnine.typing import (
        AnyArrayLike,
        CoordRange,
        ScaleDiscreteBreaks,
        ScaleDiscreteBreaksRaw,
        ScaleDiscreteLimits,
        ScaleDiscreteLimitsRaw,
        ScaleLabels,
        TupleFloat2,
        TupleFloat4,
    )

# Range, RangeDiscrete, RangeContinuous
# ScaleBreaksRaw, ScaleDiscreteBreaksRaw, ScaleContinuousBreaksRaw
# ScaleLimitsRaw, ScaleDiscreteLimitsRaw, ScaleContinuousLimitsRaw


@document
class scale_discrete(scale):
    """
    Base class for all discrete scales

    Parameters
    ----------
    {superclass_parameters}
    limits : array_like, default=None
        Limits of the scale. For scales that deal with
        categoricals, these may be a subset or superset of
        the categories. Data values that are not in the limits
        will be treated as missing data and represented with
        the `na_value`.
    drop : bool, default=True
        Whether to drop unused categories from
        the scale
    na_translate : bool, default=True
        If `True` translate missing values and show them.
        If `False` remove missing values. Default value is
        `True`
    na_value : object
        If `na_translate=True`, what aesthetic value should be
        assigned to the missing values. This parameter does not
        apply to position scales where `nan` is always placed
        on the right.
    """

    _range_class = RangeDiscrete
    _limits: Optional[ScaleDiscreteLimitsRaw]
    range: RangeDiscrete
    breaks: ScaleDiscreteBreaksRaw
    drop: bool = True  # drop unused factor levels from the scale
    na_translate: bool = True

    @property
    def limits(self) -> ScaleDiscreteLimits:
        if self.is_empty():
            return ("0", "1")

        if self._limits is None:
            return tuple(self.range.range)
        elif callable(self._limits):
            return tuple(self._limits(self.range.range))
        else:
            return tuple(self._limits)

    @limits.setter
    def limits(self, value: ScaleDiscreteLimitsRaw):
        self._limits = value

    def palette(self, value: int) -> AnyArrayLike | dict[Any, Any]:
        """
        Aesthetic mapping function
        """
        return super().palette(value)

    def train(self, x: AnyArrayLike, drop=False):
        """
        Train scale

        Parameters
        ----------
        x:
            A column of data to train over
        drop :
            Whether to drop(not include) unused categories

        A discrete range is stored in a list
        """
        if not len(x):
            return

        na_rm = not self.na_translate
        self.range.train(x, drop, na_rm=na_rm)

    def dimension(self, expand=(0, 0, 0, 0), limits=None):
        """
        Get the phyical size of the scale

        Unlike limits, this always returns a numeric vector of length 2
        """
        if limits is None:
            limits = self.limits

        return expand_range_distinct((0, len(limits)), expand)

    def expand_limits(
        self,
        limits: ScaleDiscreteLimits,
        expand: TupleFloat2 | TupleFloat4,
        coord_limits: TupleFloat2,
        trans: trans,
    ) -> range_view:
        """
        Calculate the final range in coordinate space
        """
        # Turn discrete limits into a tuple of continuous limits
        is_empty = self.is_empty() or len(limits) == 0
        climits = (0, 1) if is_empty else (1, len(limits))
        if coord_limits is not None:
            # - Override None in coord_limits
            # - Expand limits in coordinate space
            # - Remove any computed infinite values &
            c0, c1 = coord_limits
            climits = (
                climits[0] if c0 is None else c0,
                climits[1] if c1 is None else c1,
            )
        return expand_range(climits, expand, trans)

    def view(
        self,
        limits: Optional[ScaleDiscreteLimits] = None,
        range: Optional[CoordRange] = None,
    ) -> scale_view:
        """
        Information about the trained scale
        """
        if limits is None:
            limits = self.limits

        if range is None:
            range = self.dimension(limits=limits)

        breaks_d = self.get_breaks(limits)
        breaks = self.map(pd.Categorical(breaks_d))
        minor_breaks = []
        labels = self.get_labels(breaks_d)

        sv = scale_view(
            scale=self,
            aesthetics=self.aesthetics,
            name=self.name,
            limits=limits,
            range=range,
            breaks=breaks,
            labels=labels,
            minor_breaks=minor_breaks,
        )
        return sv

    def default_expansion(self, mult=0, add=0.6, expand=True):
        """
        Get the default expansion for a discrete scale
        """
        return super().default_expansion(mult, add, expand)

    def map(
        self, x, limits: Optional[ScaleDiscreteLimits] = None
    ) -> Sequence[Any]:
        """
        Map values in x to a palette
        """
        if limits is None:
            limits = self.limits

        n = sum(~pd.isna(list(limits)))
        pal = self.palette(n)
        if isinstance(pal, dict):
            # manual palette with specific assignments
            pal_match = []
            for val in x:
                try:
                    pal_match.append(pal[val])
                except KeyError:
                    pal_match.append(self.na_value)
        else:
            if not isinstance(pal, np.ndarray):
                pal = np.asarray(pal, dtype=object)
            idx = np.asarray(match(x, limits))
            try:
                pal_match = [pal[i] if i >= 0 else None for i in idx]
            except IndexError:
                # Deal with missing data
                # - Insert NaN where there is no match
                pal = np.hstack((pal.astype(object), np.nan))
                idx = np.clip(idx, 0, len(pal) - 1)
                pal_match = list(pal[idx])

        if self.na_translate:
            bool_pal_match = pd.isna(pal_match)
            if len(bool_pal_match.shape) > 1:
                # linetypes take tuples, these return 2d
                bool_pal_match = bool_pal_match.any(axis=1)
            bool_idx = pd.isna(x) | bool_pal_match
            if bool_idx.any():
                pal_match = [
                    x if i else self.na_value
                    for x, i in zip(pal_match, ~bool_idx)
                ]

        return pal_match

    def get_breaks(
        self, limits: Optional[ScaleDiscreteLimits] = None
    ) -> ScaleDiscreteBreaks:
        """
        Return an ordered list of breaks

        The form is suitable for use by the guides e.g.
            ['fair', 'good', 'very good', 'premium', 'ideal']
        """
        if self.is_empty():
            return []

        if limits is None:
            limits = self.limits

        if self.breaks in (None, False):
            breaks = []
        elif self.breaks is True:
            breaks = list(limits)
        elif callable(self.breaks):
            breaks = self.breaks(limits)
        else:
            breaks = list(self.breaks)

        return breaks

    def get_bounded_breaks(
        self, limits: Optional[ScaleDiscreteLimits] = None
    ) -> ScaleDiscreteBreaks:
        """
        Return Breaks that are within limits
        """
        if limits is None:
            limits = self.limits

        lookup_limits = set(limits)
        return [b for b in self.get_breaks() if b in lookup_limits]

    def get_labels(
        self, breaks: Optional[ScaleDiscreteBreaks] = None
    ) -> ScaleLabels:
        """
        Generate labels for the legend/guide breaks
        """
        if self.is_empty():
            return []

        if breaks is None:
            breaks = self.get_breaks()

        # The labels depend on the breaks if the breaks.
        # No breaks, no labels
        if breaks in (None, False) or self.labels in (None, False):
            return []
        elif self.labels is True:
            return [str(b) for b in breaks]
        elif callable(self.labels):
            return self.labels(breaks)
        # if a dict is used to rename some labels
        elif isinstance(self.labels, dict):
            return [
                str(self.labels[b]) if b in self.labels else str(b)
                for b in breaks
            ]
        else:
            # Return the labels in the order that they match with
            # the breaks.
            label_lookup = dict(zip(self.get_breaks(), self.labels))
            return [label_lookup[b] for b in breaks]

    def transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform dataframe
        """
        # Discrete scales do not do transformations
        return df

    def transform(self, x):
        """
        Transform array|series x
        """
        # Discrete scales do not do transformations
        return x

    def inverse_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Inverse Transform dataframe
        """
        # Discrete scales do not do transformations
        return df

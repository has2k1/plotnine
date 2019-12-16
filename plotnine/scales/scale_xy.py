import numpy as np
import pandas as pd
from mizani.bounds import expand_range_distinct

from ..doctools import document
from ..utils import identity, match, alias, array_kind
from ..exceptions import PlotnineError
from .range import RangeContinuous
from .scale import scale_discrete, scale_continuous, scale_datetime


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
    limits : array_like, optional
        Limits of the scale. For discrete scale, these are
        the categories (unique values) of the variable.
        For scales that deal with categoricals, these may
        be a subset or superset of the categories.
    """
    # All positions have no guide
    guide = None

    # After transformations all position values map
    # to themselves
    palette = staticmethod(identity)

    # Keeps two ranges, range and range_c
    range_c = RangeContinuous

    def __init__(self, *args, **kwargs):
        self.range_c = self.range_c()
        scale_discrete.__init__(self, *args, **kwargs)

    def reset(self):
        # Can't reset discrete scale because
        # no way to recover values
        self.range_c.reset()

    def is_empty(self):
        if self.range is None:
            return True

        return (self.range.range is None and
                self._limits is None and
                self.range_c.range is None)

    def train(self, series):
        # The discrete position scale is capable of doing
        # training for continuous data.
        # This complicates training and mapping, but makes it
        # possible to place objects at non-integer positions,
        # as is necessary for jittering etc.
        if array_kind.continuous(series):
            self.range_c.train(series)
        else:
            self.range.train(series, drop=self.drop)

    def map(self, series, limits=None):
        # Discrete values are converted into integers starting
        # at 1
        if limits is None:
            limits = self.limits
        if array_kind.discrete(series):
            seq = np.arange(1, len(limits)+1)
            idx = np.asarray(match(series, limits, nomatch=len(series)))
            try:
                seq = seq[idx]
            except IndexError:
                # Deal with missing data
                # - Insert NaN where there is no match
                seq = np.hstack((seq.astype(object), np.nan))
                idx = np.clip(idx, 0, len(seq)-1)
                seq = seq[idx]
            return seq
        return series

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
            raise PlotnineError(
                'Lost, do not know what the limits are.')

    @limits.setter
    def limits(self, value):
        if isinstance(value, tuple):
            value = list(value)
        self._limits = value

    def dimension(self, expand=(0, 0, 0, 0), limits=None):
        """
        The phyical size of the scale, if a position scale
        Unlike limits, this always returns a numeric vector of length 2
        """
        if limits is None:
            limits = self.limits

        c_range = self.range_c.range
        d_range = self.limits

        if self.is_empty():
            return (0, 1)
        elif self.range.range is None:  # only continuous
            return expand_range_distinct(c_range, expand)
        elif c_range is None:  # only discrete
            # FIXME: I think this branch should not exist
            return expand_range_distinct((1, len(d_range)), expand)
        else:  # both
            # e.g categorical bar plot have discrete items, but
            # are plot on a continuous x scale
            a = np.hstack([
                c_range,
                expand_range_distinct((1, len(d_range)), expand)
                ])
            return a.min(), a.max()


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

    # After transformations all position values map
    # to themselves
    palette = staticmethod(identity)

    def map(self, series, limits=None):
        # Position aesthetics don't map, because the coordinate
        # system takes care of it.
        # But the continuous scale has to deal with out of bound points
        if not len(series):
            return series
        if limits is None:
            limits = self.limits
        scaled = self.oob(series, limits)
        scaled[pd.isnull(scaled)] = self.na_value
        return scaled


@document
class scale_x_discrete(scale_position_discrete):
    """
    Discrete x position

    Parameters
    ----------
    {superclass_parameters}
    """
    _aesthetics = ['x', 'xmin', 'xmax', 'xend']


@document
class scale_y_discrete(scale_position_discrete):
    """
    Discrete y position

    Parameters
    ----------
    {superclass_parameters}
    """
    _aesthetics = ['y', 'ymin', 'ymax', 'yend']


# Not part of the user API
alias('scale_x_ordinal', scale_x_discrete)
alias('scale_y_ordinal', scale_y_discrete)


@document
class scale_x_continuous(scale_position_continuous):
    """
    Continuous x position

    Parameters
    ----------
    {superclass_parameters}
    """
    _aesthetics = ['x', 'xmin', 'xmax', 'xend', 'xintercept']


@document
class scale_y_continuous(scale_position_continuous):
    """
    Continuous y position

    Parameters
    ----------
    {superclass_parameters}
    """
    _aesthetics = ['y', 'ymin', 'ymax', 'yend', 'yintercept',
                   'ymin_final', 'ymax_final',
                   'lower', 'middle', 'upper']


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


alias('scale_x_date', scale_x_datetime)
alias('scale_y_date', scale_y_datetime)


@document
class scale_x_timedelta(scale_x_continuous):
    """
    Continuous x position for timedelta data points

    Parameters
    ----------
    {superclass_parameters}
    """
    _trans = 'pd_timedelta'


@document
class scale_y_timedelta(scale_y_continuous):
    """
    Continuous y position for timedelta data points

    Parameters
    ----------
    {superclass_parameters}
    """
    _trans = 'pd_timedelta'


@document
class scale_x_sqrt(scale_x_continuous):
    """
    Continuous x position sqrt transformed scale

    Parameters
    ----------
    {superclass_parameters}
    """
    _trans = 'sqrt'


@document
class scale_y_sqrt(scale_y_continuous):
    """
    Continuous y position sqrt transformed scale

    Parameters
    ----------
    {superclass_parameters}
    """
    _trans = 'sqrt'


@document
class scale_x_log10(scale_x_continuous):
    """
    Continuous x position log10 transformed scale

    Parameters
    ----------
    {superclass_parameters}
    """
    _trans = 'log10'


@document
class scale_y_log10(scale_y_continuous):
    """
    Continuous y position log10 transformed scale

    Parameters
    ----------
    {superclass_parameters}
    """
    _trans = 'log10'


@document
class scale_x_reverse(scale_x_continuous):
    """
    Continuous x position reverse transformed scale

    Parameters
    ----------
    {superclass_parameters}
    """
    _trans = 'reverse'


@document
class scale_y_reverse(scale_y_continuous):
    """
    Continuous y position reverse transformed scale

    Parameters
    ----------
    {superclass_parameters}
    """
    _trans = 'reverse'

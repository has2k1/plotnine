from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from copy import deepcopy

import numpy as np
import pandas as pd
import pandas.core.common as com
import matplotlib.cbook as cbook
from matplotlib.ticker import MaxNLocator

from ..utils import waiver, is_waive
from ..utils import identity, match
from ..utils import round_any
from ..utils.exceptions import gg_warning, GgplotError
from .utils import rescale, censor, expand_range, zero_range
from ..components.aes import is_position_aes


class scale(object):
    """
    Base class for all scales
    """
    aesthetics = None   # aesthetics affected by this scale
    palette = None      # aesthetic mapping function
    range = None        # range of aesthetic
    trans = None        # transformation function
    na_value = np.NaN   # What to do with the NA values
    _expand = waiver()  # multiplicative and additive expansion constants.
    breaks = waiver()   # major breaks
    labels = waiver()   # labels at the breaks
    guide = 'legend'    # legend or any other guide
    _limits = None      # (min, max)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
            elif hasattr(self, '_'+k):
                setattr(self, '_'+k, v)
            else:
                msg = '{} could not recognise parameter `{}`'
                gg_warning(msg.format(self.__class__.__name__, k))

        if cbook.iterable(self.breaks) and cbook.iterable(self.labels):
            if len(self.breaks) != len(self.labels):
                raise GgplotError(
                    "Breaks and labels have unequal lengths")

        if (self.breaks is None and
                not is_position_aes(self.aesthetics) and
                self.guide is not None):
            self.guide = None

    def __radd__(self, gg):
        """
        Add this scales to the list of scales for the
        ggplot object
        """
        gg = deepcopy(gg)
        gg.scales.append(self)
        return gg

    def clone(self):
        return deepcopy(self)

    def reset(self):
        """
        Set the range of the scale to None.

        i.e Forget all the training
        """
        self.range = None

    @property
    def limits(self):
        # Fall back to the range if the limits
        # are not set or if any is NaN
        if not (self._limits is None):
            if not any(map(pd.isnull, self._limits)):
                return self._limits
        return self.range

    @limits.setter
    def limits(self, value):
        self._limits = value

    @property
    def expand(self):
        if is_waive(self._expand):
            # default
            return (0, 0)
        else:
            return self._expand

    @expand.setter
    def expand(self, value):
        self._expand = value

    def train_df(self, df):
        """
        Train scale from a dataframe
        """
        aesthetics = set(self.aesthetics) & set(df.columns)
        for ae in aesthetics:
            self.train(df[ae])

    def map_df(self, df):
        """
        Map df
        """
        if len(df) == 0:
            return

        aesthetics = set(self.aesthetics) & set(df.columns)
        for ae in aesthetics:
            df[ae] = self.map(df[ae])

        return df


class scale_discrete(scale):
    """
    Base class for all discrete scales
    """
    drop = True        # drop unused factor levels from the scale

    def train(self, series, drop=None):
        """
        Train scale

        Parameters
        ----------
        series: pd.series | np.array
            a column of data to train over

        A discrete range is stored in a list
        """
        if drop is None:
            drop = self.drop

        if self.range is None:
            self.range = []

        # new range values
        if com.is_categorical_dtype(series):
            rng = list(series.cat.categories)
            if drop:
                rng = [x for x in rng if x in set(series)]
        else:
            rng = list(series.drop_duplicates().sort(inplace=False))

        # update range
        self.range += [x for x in rng if not (x in set(self.range))]

    def dimension(self, expand=None):
        """
        The phyical size of the scale, if a position scale
        Unlike limits, this always returns a numeric vector of length 2
        """
        if expand is None:
            expand = self.expand
        return expand_range(len(self.limits), expand[0], expand[1])

    def map(self, x, limits=None):
        """
        Return an array-like of x mapped to values
        from the scales palette
        """
        if limits is None:
            limits = self.limits

        n = sum(~pd.isnull(limits))
        pal = np.asarray(self.palette(n))
        pal_match = pal[match(x, limits)]
        pal_match[pd.isnull(pal_match)] = self.na_value
        return pal_match

    def scale_breaks(self):
        """
        Returns a dictionary of the form {break: position}

        e.g.
        {'fair': 1, 'good': 2, 'very good': 3,
        'premium': 4, 'ideal': 5}
        """
        if self.breaks is None:
            return None
        elif is_waive(scale.breaks):
            breaks = self.limits
        elif callable(scale.breaks):
            breaks = scale.breaks(self.limits)
        else:
            breaks = scale.breaks

        # Breaks can only occur only on values in domain
        in_domain = list(set(breaks) & set(self.limits))
        pos = match(in_domain, breaks)
        return dict(zip(in_domain, pos))

    def scale_labels(self):
        breaks = self.scale_breaks()

        if breaks is None:
            return None

        if self.labels is None:
            return None
        elif is_waive(self.labels):
            # if breaks is
            #   {'I': 2, 'G': 1, 'P': 3, 'V': 4, 'F': 0}
            # We want the labels sorted acc. to the value
            # i.e ['F', 'G', 'I', 'P', 'V']
            return sorted(breaks, key=breaks.__getitem__)
        elif callable(self.labels):
            return self.labels(breaks)
        else:
            # if a dict is used to rename some labels
            if issubclass(scale.labels, dict):
                labels = breaks
                lookup = list(scale.labels.items())
                mp = match(lookup, labels, nomatch=-1)
                for idx in mp:
                    if idx != -1:
                        labels[idx] = lookup[idx]
                return labels
            else:
                # TODO: see ggplot2
                # Need to ensure that if breaks were dropped,
                # corresponding labels are too
                return self.labels


class scale_continuous(scale):
    """
    Base class for all continuous scales
    """
    rescaler = staticmethod(rescale)  # Used by diverging & n colour gradients
    oob = staticmethod(censor)  # what to do with out of bounds data points
    minor_breaks = waiver()
    trans = staticmethod(identity)  # transformation function

    def train(self, series):
        """
        Train scale

        Parameters
        ----------
        series: pd.series | np.array
            a column of data to train over

        """
        if not len(series):
            return

        mn = series.min()
        mx = series.max()
        if not (self.range is None):
            _mn, _mx = self.range
            mn = np.min([mn, _mn])
            mx = np.max([mx, _mx])

        self.range = [mn, mx]

    def dimension(self, expand=None):
        """
        The phyical size of the scale, if a position scale
        Unlike limits, this always returns a numeric vector of length 2
        """
        if expand is None:
            expand = self.expand
        return expand_range(self.limits, expand[0], expand[1])

    def map(self, x, limits=None):
        if limits is None:
            limits = self.limits

        x = self.oob(self.rescaler(x, from_=limits))

        # Points are rounded to the nearest 500th, to reduce the
        # amount of work that the scale palette must do - this is
        # particularly important for colour scales which are rather
        # slow.  This shouldn't have any perceptual impacts.
        x = round_any(x, 1 / 500)
        uniq = np.unique(x)
        pal = np.asarray(self.palette(uniq))
        scaled = pal[match(x, uniq)]
        scaled[pd.isnull(scaled)] = self.na_value
        return scaled

    def scale_breaks(self):
        # Limits in transformed space need to be converted back to
        # data space
        # TODO enable this after transforms are sorted out
        # limits = scale.trans.inv(scale.limits)
        limits = self.limits

        if scale.breaks is None:
            return None
        elif zero_range(limits):
            breaks = limits[0]
        elif is_waive(scale.breaks):
            # Transformation needed here XXX ?
            breaks = MaxNLocator(4).tick_values(*limits)
        elif callable(scale.breaks):
            breaks = scale.breaks(limits)
        else:
            breaks = scale.breaks

        # Breaks in data space need to be converted back to
        # transformed space And any breaks outside the
        # dimensions need to be flagged as missing
        # breaks = censor(scale.trans.trans(breaks),
        #                 scale.trans.trans(limits))
        breaks = censor(breaks, limits)
        if len(breaks) == 0:
            GgplotError('Zero breaks in scale for {}'.format(
                scale.aesthetics))
        return breaks

    def scale_labels(self):
        breaks = self.scale_breaks()

        if breaks is None:
            return None

        if self.labels is None:
            return None
        elif is_waive(self.labels):
            # TODO: Should apply transformation
            labels = breaks
        elif callable(self.labels):
            labels = self.labels(breaks)
        else:
            labels = self.labels

        if len(labels) != len(breaks):
            raise GgplotError(
                "Breaks and labels are different lengths")

        return labels

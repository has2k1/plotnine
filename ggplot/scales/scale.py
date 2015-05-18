from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import types
from copy import deepcopy
from collections import OrderedDict

import numpy as np
import pandas as pd
import pandas.core.common as com
import matplotlib.cbook as cbook
from matplotlib.ticker import Locator, Formatter, FuncFormatter

from ..utils import waiver, is_waive
from ..utils import match, is_sequence_of_strings
from ..utils import round_any
from ..utils.exceptions import gg_warning, GgplotError
from .utils import rescale, censor, expand_range, zero_range
from .utils import identity_trans, gettrans
from ..components.aes import is_position_aes


class scale(object):
    """
    Base class for all scales
    """
    aesthetics = None   # aesthetics affected by this scale
    palette = None      # aesthetic mapping function
    range = None        # range of aesthetic
    na_value = np.NaN   # What to do with the NA values
    expand = waiver()   # multiplicative and additive expansion constants.
    name = None         # used as the axis label or legend title
    breaks = waiver()   # major breaks
    labels = waiver()   # labels at the breaks
    guide = 'legend'    # legend or any other guide
    _limits = None      # (min, max) - set by user

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
        if self._limits is not None:
            if not any(map(pd.isnull, self._limits)):
                return self._limits
        return self.range

    @limits.setter
    def limits(self, value):
        self._limits = value

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

    def break_info(self, range=None):
        if range is None:
            range = self.dimension()
        # for discrete, limits != range
        limits = self.limits
        major = self.scale_breaks(limits)
        if major is None:
            labels = None
        else:
            labels = self.scale_labels(major)
            major = pd.Categorical(major.keys())
            major = self.map(major)
        return {'range': range,
                'labels': labels,
                'major': major}

    def scale_breaks(self, limits=None, can_waive=False):
        """
        Returns a ordered dictionary of the form {break: position}

        The form is suitable for use by the guides

        e.g.
        {'fair': 1, 'good': 2, 'very good': 3,
        'premium': 4, 'ideal': 5}
        """
        if limits is None:
            limits = self.limits

        if self.breaks is None:
            return None
        elif is_waive(scale.breaks):
            breaks = limits
        elif callable(scale.breaks):
            breaks = scale.breaks(limits)
        else:
            breaks = scale.breaks

        # Breaks can only occur only on values in domain
        in_domain = list(set(breaks) & set(self.limits))
        pos = match(in_domain, breaks)
        tups = zip(in_domain, pos)
        return OrderedDict(sorted(tups, key=lambda t: t[1]))

    def scale_labels(self, breaks=None, can_waive=False):
        """
        Generate labels for the legend/guide breaks
        """
        if breaks is None:
            breaks = self.scale_breaks(can_waive=can_waive)

        # The labels depend on the breaks if the breaks are None
        # or are waived, it is likewise for the labels
        if breaks is None or self.labels is None:
            return None
        elif is_waive(breaks):
            return waiver()
        elif is_waive(self.labels):
            # if breaks is a dict (ordered by value)
            #   {'I': 2, 'G': 1, 'P': 3, 'V': 4, 'F': 0}
            # The keys are the labels
            # i.e ['F', 'G', 'I', 'P', 'V']
            try:
                return list(breaks.keys())
            except AttributeError:
                return breaks
        elif callable(self.labels):
            return self.labels(breaks)
        # if a dict is used to rename some labels
        elif isinstance(scale.labels, dict):
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

    def transform_df(self, df):
        """
        Transform df
        """
        # Discrete scales do not do transformations
        return df

    def transform(self, series):
        """
        Transform
        """
        return series


class scale_continuous(scale):
    """
    Base class for all continuous scales
    """
    rescaler = staticmethod(rescale)  # Used by diverging & n colour gradients
    oob = staticmethod(censor)     # what to do with out of bounds data points
    minor_breaks = waiver()
    trans = 'identity'             # transform class

    def __init__(self, **kwargs):
        # Make sure we have a transform and it
        # should know the main aesthetic,
        # in case it has to manipulate the axis
        try:
            self.trans = kwargs.pop('trans')
        except KeyError:
            pass
        self.trans = gettrans(self.trans)
        self.trans.aesthetic = self.aesthetics[0]

        # The limits are given in original dataspace
        # but they leave in transformed space since all
        # computations happen on transformed data. The
        # labeling of the plot axis and the guides are in
        # the original dataspace.
        if 'limits' in kwargs:
            kwargs['limits'] = self.trans.trans(kwargs['limits'])

        # We can set the breaks to user defined values or
        # have matplotlib calculate them using the default locator
        # function. In case of transform, special locator and
        # formatter functions are created for mpl to use.

        # When both breaks and transformation are specified,
        # the trans object should not modify the axis. The
        # trans object will still transform the data
        if 'breaks' in kwargs:
            # locator wins
            if (callable(kwargs['breaks']) and
                    isinstance(kwargs['breaks'](), Locator)):
                self.trans.locator_factory = kwargs.pop('breaks')
            # trust the user breaks
            elif self.trans != identity_trans:
                # kill the locator but not the and the formatter.
                self.trans.locator_factory = waiver()

        if 'labels' in kwargs:
            # Accept an MPL Formatter, a function or a list-like
            if (callable(kwargs['labels']) and
                    isinstance(kwargs['labels'](), Formatter)):
                self.trans.formatter_factory = kwargs.pop('labels')
            elif isinstance(kwargs['labels'], types.FunctionType):
                self.trans.formatter_factory = FuncFormatter(
                    kwargs.pop('labels'))
            elif is_sequence_of_strings(kwargs['labels']):
                self.trans.formatter_factory = waiver()
            elif not is_sequence_of_strings(kwargs['labels']):
                msg = 'labels should be function or a sequence of strings'
                raise GgplotError(msg)

        scale.__init__(self, **kwargs)

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

    def transform_df(self, df):
        """
        Transform df
        """
        if len(df) == 0:
            return

        if self.trans.name == 'identity':
            return df

        aesthetics = set(self.aesthetics) & set(df.columns)
        for ae in aesthetics:
            try:
                df[ae] = self.transform(df[ae])
            except TypeError:
                pass

        return df

    def transform(self, series):
        """
        Transform
        """
        try:
            return self.trans.trans(series)
        except TypeError:
            return [self.trans.trans(x) for x in series]

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

    def break_info(self, range=None):
        if range is None:
            range = self.dimension()

        major = self.scale_breaks(range)
        labels = self.scale_labels(major)
        return {'range': range,
                'labels': labels,
                'major': major}

    def scale_breaks(self, limits=None, can_waive=True):
        """
        Generate breaks for the legend/guide

        Parameters
        ----------
        limits : list-like
        can_waive : bool
            Whether the method can return a waiver object.
            When the guides request breaks they really need
            them and cannot rely on Matplotlib. This option
            is for them.
        """
        if limits is None:
            limits = self.limits
        # Limits in transformed space need to be
        # converted back to data space
        limits = self.trans.inv(self.limits)

        if scale.breaks is None:
            return None
        elif zero_range(limits):
            breaks = [limits[0]]
        elif can_waive and is_waive(scale.breaks):
            # The MPL Locator will handle them
            return scale.breaks
        elif is_waive(scale.breaks):
            breaks = self.trans.breaks(4).tick_values(*limits)
        elif callable(scale.breaks):
            breaks = scale.breaks(limits)
        else:
            breaks = scale.breaks

        # Breaks in data space need to be converted back to
        # transformed space And any breaks outside the
        # dimensions need to be flagged as missing
        breaks = censor(self.transform(breaks),
                        self.transform(limits))
        if len(breaks) == 0:
            raise GgplotError('Zero breaks in scale for {}'.format(
                scale.aesthetics))
        return breaks

    def scale_labels(self, breaks=None, can_waive=False):
        """
        Generate labels for the legend/guide breaks
        """
        if breaks is None:
            breaks = self.scale_breaks(can_waive=can_waive)

        # The labels depend on the breaks if the breaks are None
        # or are waived, it is likewise for the labels
        if breaks is None or self.labels is None:
            return None
        elif is_waive(breaks):
            return waiver()
        elif can_waive and is_waive(self.labels):
            # The MPL Formatter will handle them
            return self.labels
        elif is_waive(self.labels):
            # Instantiate a formatter and "prep"
            # it for use
            breaks = np.asarray(breaks)
            locs = breaks[~np.isnan(breaks)]
            if not len(locs):
                locs = [0, 1]
            formatter = self.trans.format()
            formatter.create_dummy_axis()
            formatter.set_locs(locs)
            # This is what really matters
            labels = [formatter(b) for b in breaks]
        elif callable(self.labels):
            labels = self.labels(breaks)
        else:
            labels = self.labels

        if len(labels) != len(breaks):
            raise GgplotError(
                "Breaks and labels are different lengths")

        return labels

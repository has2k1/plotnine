from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy, copy
from collections import OrderedDict
from warnings import warn

import six
from six import add_metaclass
from six.moves import zip

import numpy as np
import pandas as pd
import matplotlib.cbook as cbook
from mizani.bounds import expand_range_distinct, zero_range
from mizani.bounds import rescale, censor
from mizani.breaks import date_breaks
from mizani.formatters import date_format
from mizani.transforms import gettrans

from ..aes import is_position_aes
from ..doctools import document
from ..exceptions import PlotnineError
from ..utils import match, suppress, waiver, is_waive, Registry
from .range import Range, RangeContinuous, RangeDiscrete


@add_metaclass(Registry)
class scale(object):
    """
    Base class for all scales

    Parameters
    ----------
    range : array_like
        Range of aesthetic. Default is to automatically
        determine the range from the data points.
    breaks : array_like or callable, optional
        Major break points. Alternatively, a callable that
        takes a tuple of limits and returns a list of breaks.
        Default is to automatically calculate the breaks.
    expand : array_like, optional
        Multiplicative and additive expansion constants
        that determine how the scale is expanded. If
        specified must of of length 2 or 4. Specifically the
        the values are of this order::

            (mul, add)
            (mul_low, add_low, mul_high, add_high)

        If not specified, suitable defaults are chosen.
    name : str, optional
        Name used as the label of the scale. This is what
        shows up as the axis label or legend title. Suitable
        defaults are chosen depending on the type of scale.
    labels : list or callable, optional
        List of :class:`str`. Labels at the `breaks`.
        Alternatively, a callable that takes an array_like of
        break points as input and returns a list of strings.
    limits : array_like, optional
        Limits of the scale. Most commonly, these are the
        min & max values for the scales. For scales that
        deal with categoricals, these may be a subset or
        superset of the categories.
    na_value : scalar
        What value to assign to missing values. Default
        is to assign ``np.nan``.
    palette : function, optional
        Function to map data points onto the scale. Most
        scales define their own palettes.
    aesthetics : list, very optional
        list of :class:`str`. Aesthetics covered by the
        scale. These are defined by each scale and the
        user should probably not change them. Have fun.
    """
    __base__ = True

    aesthetics = []     # aesthetics affected by this scale
    na_value = np.NaN   # What to do with the NA values
    name = None         # used as the axis label or legend title
    breaks = waiver()   # major breaks
    labels = waiver()   # labels at the breaks
    guide = 'legend'    # legend or any other guide
    _limits = None      # (min, max) - set by user

    #: range of aesthetic, instantiated by :meth:`scale.__init__``
    range = Range

    #: multiplicative and additive expansion constants
    expand = waiver()

    def __init__(self, **kwargs):
        self.range = self.range()
        for k, v in kwargs.items():
            if hasattr(self, '_'+k):
                setattr(self, '_'+k, v)
            elif hasattr(self, k):
                setattr(self, k, v)
            else:
                msg = "{} could not recognise parameter `{}`"
                warn(msg.format(self.__class__.__name__, k))

        if cbook.iterable(self.breaks) and cbook.iterable(self.labels):
            if len(self.breaks) != len(self.labels):
                raise PlotnineError(
                    "Breaks and labels have unequal lengths")

        if (self.breaks is None and
                not is_position_aes(self.aesthetics) and
                self.guide is not None):
            self.guide = None

    def __radd__(self, gg, inplace=False):
        """
        Add this scales to the list of scales for the
        ggplot object
        """
        gg = gg if inplace else deepcopy(gg)
        gg.scales.append(copy(self))
        return gg

    @staticmethod
    def palette(x):
        """
        Aesthetic mapping function
        """
        raise NotImplementedError('Not Implemented')

    def map(self, x, limits=None):
        """
        Map every element of x

        The palette should do the real work, this should
        make sure that sensible values are sent and
        return from the palette.
        """
        raise NotImplementedError('Not Implemented')

    def train(self, x):
        """
        Train scale

        Parameters
        ----------
        x: pd.series | np.array
            a column of data to train over
        """
        raise NotImplementedError('Not Implemented')

    def dimension(self, expand=None):
        """
        The phyical size of the scale.
        """
        raise NotImplementedError('Not Implemented')

    def transform_df(self, df):
        """
        Transform dataframe
        """
        raise NotImplementedError('Not Implemented')

    def transform(self, x):
        """
        Transform array|series x
        """
        raise NotImplementedError('Not Implemented')

    def inverse(self, x):
        """
        Inverse transform array|series x
        """
        raise NotImplementedError('Not Implemented')

    def clone(self):
        return deepcopy(self)

    def reset(self):
        """
        Set the range of the scale to None.

        i.e Forget all the training
        """
        self.range.reset()

    def is_empty(self):
        return self.range.range is None and self._limits is None

    @property
    def limits(self):
        if self.is_empty():
            return (0, 1)

        # Fall back to the range if the limits
        # are not set or if any is None or NaN
        if self._limits is not None:
            limits = []
            if len(self._limits) == len(self.range.range):
                for l, r in zip(self._limits, self.range.range):
                    value = r if pd.isnull(l) else l
                    limits.append(value)
            else:
                limits = self._limits
            return tuple(limits)
        return self.range.range

    @limits.setter
    def limits(self, value):
        if isinstance(value, tuple):
            value = list(value)
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


@document
class scale_discrete(scale):
    """
    Base class for all discrete scales

    Parameters
    ----------
    {superclass_parameters}
    drop : bool
        Whether to drop unused categories from
        the scale
    """
    range = RangeDiscrete
    drop = True        # drop unused factor levels from the scale

    def train(self, x, drop=None):
        """
        Train scale

        Parameters
        ----------
        x: pd.series| np.array
            a column of data to train over

        A discrete range is stored in a list
        """
        if not len(x):
            return

        self.range.train(x, drop)

    def dimension(self, expand=(0, 0, 0, 0)):
        """
        The phyical size of the scale, if a position scale
        Unlike limits, this always returns a numeric vector of length 2
        """
        return expand_range_distinct(len(self.limits), expand)

    def map(self, x, limits=None):
        """
        Return an array-like of x mapped to values
        from the scales palette
        """
        if limits is None:
            limits = self.limits

        n = sum(~pd.isnull(list(limits)))
        pal = self.palette(n)
        if isinstance(pal, dict):
            # manual palette with specific assignments
            pal_match = [pal[val] for val in x]
        else:
            pal = np.asarray(pal)
            pal_match = pal[match(x, limits)]
            pal_match[pd.isnull(pal_match)] = self.na_value
        return pal_match

    def break_info(self, range=None):
        if range is None:
            range = self.dimension()
        # for discrete, limits != range
        limits = self.limits
        major = self.get_breaks(limits)
        minor = []
        if major is None:
            major = labels = []
        else:
            labels = self.get_labels(major)
            major = pd.Categorical(major.keys())
            major = self.map(major)
        return {'range': range,
                'labels': labels,
                'major': major,
                'minor': minor}

    def get_breaks(self, limits=None, strict=True):
        """
        Returns a ordered dictionary of the form {break: position}

        The form is suitable for use by the guides

        e.g.
        {'fair': 1, 'good': 2, 'very good': 3,
        'premium': 4, 'ideal': 5}
        """
        if self.is_empty():
            return []

        if limits is None:
            limits = self.limits

        if self.breaks is None:
            return None
        elif is_waive(self.breaks):
            breaks = limits
        elif callable(self.breaks):
            breaks = self.breaks(limits)
        else:
            breaks = self.breaks

        # Breaks can only occur only on values in domain
        if strict:
            in_domain = list(set(breaks) & set(self.limits))
        else:
            in_domain = breaks
        pos = match(in_domain, breaks)
        tups = zip(in_domain, pos)
        return OrderedDict(sorted(tups, key=lambda t: t[1]))

    def get_labels(self, breaks=None):
        """
        Generate labels for the legend/guide breaks
        """
        if self.is_empty():
            return []

        if breaks is None:
            breaks = self.get_breaks()

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
        elif isinstance(self.labels, dict):
            labels = breaks
            lookup = list(self.labels.items())
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


@document
class scale_continuous(scale):
    """
    Base class for all continuous scales

    Parameters
    ----------
    {superclass_parameters}
    trans : str | function
        Name of a trans function or a trans function
    oob : function
        Function to deal with out of bounds (limits)
        data points. Default is to turn them into
        ``np.nan``, which then get dropped.
    minor_breaks : list or callable or None
        Minor breaks points or a function that given the
        limits returns a vector of minor breaks. If ``None``,
        there are not included. Default is to automatically
        calculate them.
    rescaler : function, optional
        Function to rescale data points so that they can
        be handled by the palette. Default is to rescale
        them onto the [0, 1] range. Scales that inherit
        from this class may have another default.

    Note
    ----
    If using the class directly all arguments must be
    keyword arguments.
    """
    range = RangeContinuous
    rescaler = staticmethod(rescale)  # Used by diverging & n colour gradients
    oob = staticmethod(censor)     # what to do with out of bounds data points
    minor_breaks = waiver()
    _trans = 'identity'            # transform class

    def __init__(self, **kwargs):
        # Make sure we have a transform.
        self.trans = kwargs.pop('trans', self._trans)

        with suppress(KeyError):
            self.limits = kwargs.pop('limits')

        scale.__init__(self, **kwargs)

    @property
    def trans(self):
        return self._trans

    @trans.setter
    def trans(self, value):
        self._trans = gettrans(value)
        self._trans.aesthetic = self.aesthetics[0]

    @scale.limits.setter
    def limits(self, value):
        """
        Limits for the continuous scale

        Note
        ----
        The limits are given in original dataspace
        but they are stored in transformed space since
        all computations happen on transformed data. The
        labeling of the plot axis and the guides are in
        the original dataspace.
        """
        limits = self.trans.transform(value)
        if six.PY2:
            # np.sort is not strict enough in python 2.7
            if any(x is None for x in limits):
                self._limits = limits
            else:
                try:
                    self._limits = np.sort(limits)
                except TypeError:
                    self._limits = limits
        else:
            try:
                self._limits = np.sort(limits)
            except TypeError:
                self._limits = limits

    def train(self, x):
        """
        Train scale

        Parameters
        ----------
        x: pd.series | np.array
            a column of data to train over

        """
        if not len(x):
            return

        self.range.train(x)

    def transform_df(self, df):
        """
        Transform dataframe
        """
        if len(df) == 0:
            return

        aesthetics = set(self.aesthetics) & set(df.columns)
        for ae in aesthetics:
            with suppress(TypeError):
                df[ae] = self.transform(df[ae])

        return df

    def transform(self, x):
        """
        Transform array|series x
        """
        try:
            return self.trans.transform(x)
        except TypeError:
            return np.array([self.trans.transform(val) for val in x])

    def inverse(self, x):
        """
        Inverse transform array|series x
        """
        try:
            return self.trans.inverse(x)
        except TypeError:
            return np.array([self.trans.inverse(val) for val in x])

    def dimension(self, expand=(0, 0, 0, 0)):
        """
        The phyical size of the scale, if a position scale
        Unlike limits, this always returns a numeric vector of length 2
        """
        return expand_range_distinct(self.limits, expand)

    def map(self, x, limits=None):
        if limits is None:
            limits = self.limits

        x = self.oob(self.rescaler(x, _from=limits))

        uniq = np.unique(x)
        pal = np.asarray(self.palette(uniq))
        scaled = pal[match(x, uniq)]
        scaled[pd.isnull(scaled)] = self.na_value
        return scaled

    def break_info(self, range=None):
        """
        Return break information for the axis

        The range, major breaks & minor_breaks are
        in transformed space. The labels for the major
        breaks depict data space values.
        """
        if range is None:
            range = self.dimension()

        major = self.get_breaks(range)
        if major is None or len(major) == 0:
            major = minor = labels = np.array([])
        else:
            major = major.compress(np.isfinite(major))
            minor = self.get_minor_breaks(major, range)

        major = major.compress(
            (range[0] <= major) & (major <= range[1]))
        labels = self.get_labels(major)

        return {'range': range,
                'labels': labels,
                'major': major,
                'minor': minor}

    def get_breaks(self, limits=None, strict=False):
        """
        Generate breaks for the axis or legend

        Parameters
        ----------
        limits : list-like | None
            If None the self.limits are used
            They are expected to be in transformed
            space.

        strict : bool
            If True then the breaks gauranteed to fall within
            the limits. e.g. when the legend uses this method.

        Returns
        -------
        out : array-like

        Note
        ----
        Breaks are calculated in data space and
        returned in transformed space since all
        data is plotted in transformed space.
        """
        if limits is None:
            limits = self.limits

        # To data space
        _limits = self.inverse(limits)

        if self.is_empty():
            breaks = []
        elif self.breaks is None or self.breaks is False:
            breaks = []
        elif zero_range(_limits):
            breaks = [_limits[0]]
        elif is_waive(self.breaks):
            breaks = self.trans.breaks(_limits)
        elif callable(self.breaks):
            breaks = self.breaks(_limits)
        else:
            breaks = self.breaks

        breaks = self.transform(breaks)
        # At this point, any breaks beyond the limits
        # are kept since they may be used to calculate
        # minor breaks
        if strict:
            cond = (breaks >= limits[0]) & (limits[1] >= breaks)
            breaks = np.compress(cond, breaks)
        return np.asarray(breaks)

    def get_minor_breaks(self, major, limits=None):
        """
        Return minor breaks
        """
        if major is None:
            return []

        if limits is None:
            limits = self.limits

        if callable(self.minor_breaks):
            breaks = self.minor_breaks(self.trans.inverse(limits))
            _major = set(major)
            minor = self.trans.transform(breaks)
            return [x for x in minor if x not in _major]

        if not is_waive(self.minor_breaks):
            return self.minor_breaks

        return self.trans.minor_breaks(major, limits)

    def get_labels(self, breaks=None):
        """
        Generate labels for the axis or legend
        """
        if breaks is None:
            breaks = self.get_breaks()

        breaks = self.inverse(breaks)

        # The labels depend on the breaks if the breaks are None
        # or are waived, it is likewise for the labels
        if breaks is None or self.labels is None:
            return None
        elif is_waive(breaks):
            return waiver()
        elif is_waive(self.labels):
            labels = self.trans.format(breaks)
        elif callable(self.labels):
            labels = self.labels(breaks)
        else:
            labels = self.labels

        if len(labels) != len(breaks):
            raise PlotnineError(
                "Breaks and labels are different lengths")

        return labels


@document
class scale_datetime(scale_continuous):
    """
    Base class for all date/datetime scales

    Parameters
    ----------
    date_breaks : str
        A string giving the distance between major breaks.
        For example `'2 weeks'`, `'5 years'`. If specified,
        ``date_breaks`` takes precedence over
        ``breaks``.
    date_labels : str
        Format string for the labels.
        See :ref:`strftime <strftime-strptime-behavior>`.
        If specified, ``date_labels`` takes precedence over
        ``labels``.
    date_minor_breaks : str
        A string giving the distance between minor breaks.
        For example `'2 weeks'`, `'5 years'`. If specified,
        ``date_minor_breaks`` takes precedence over
        ``minor_breaks``.
    {superclass_parameters}
    """
    _trans = 'datetime'

    def __init__(self, **kwargs):
        # Permit the use of the general parameters for
        # specifying the format strings
        with suppress(KeyError):
            breaks = kwargs['breaks']
            if isinstance(breaks, six.string_types):
                kwargs['breaks'] = date_breaks(breaks)

        with suppress(KeyError):
            minor_breaks = kwargs['minor_breaks']
            if isinstance(minor_breaks, six.string_types):
                kwargs['minor_breaks'] = date_breaks(minor_breaks)

        # Using the more specific parameters take precedence
        with suppress(KeyError):
            breaks_fmt = kwargs.pop('date_breaks')
            kwargs['breaks'] = date_breaks(breaks_fmt)

        with suppress(KeyError):
            labels_fmt = kwargs.pop('date_labels')
            kwargs['labels'] = date_format(labels_fmt)

        with suppress(KeyError):
            minor_breaks_fmt = kwargs.pop('date_minor_breaks')
            kwargs['minor_breaks'] = date_breaks(minor_breaks_fmt)

        scale_continuous.__init__(self, **kwargs)

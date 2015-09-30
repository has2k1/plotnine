"""
Functions related to the scales in some way or another

Any methods ported from Hadley Wickham's `scales` package
belong in this file

Reference:
----------
https://github.com/hadley/scales
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import re
import datetime
from types import FunctionType

import numpy as np
import pandas as pd
import scipy.stats as stats
from matplotlib.ticker import MaxNLocator, ScalarFormatter, Formatter
from matplotlib.ticker import AutoMinorLocator
from matplotlib.dates import MinuteLocator, HourLocator, DayLocator
from matplotlib.dates import WeekdayLocator, MonthLocator, YearLocator
from matplotlib.dates import AutoDateLocator
from matplotlib.dates import DateFormatter
from matplotlib.dates import date2num, num2date
import six

from ..utils import seq, round_any, identity, is_waive, gg_import
from ..utils.exceptions import GgplotError


# formatting functions
def dollar(x, pos):
    return '${:.2f}'.format(x)

currency = dollar


def comma(x, pos):
    return '{:0,d}'.format(int(x))


def millions(x, pos):
    return '${:1.1f}M'.format(x*1e-6)


def percent(x, pos):
    return'{0:.0f}%'.format(x*100)


def scientific(x, pos):
    return '{:.2e}'.format(x)


def rescale_pal(range=(0.1, 1)):
    """
    Rescale the input to the specific output range.
    Useful for alpha, size, and continuous position.
    """
    def rescale_(x):
        return rescale(x, range, (0, 1))
    return rescale_


def rescale(x, to=(0, 1), from_=None):
    """
    Rescale numeric vector to have specified minimum and maximum.

    Parameters
    ----------
    x: ndarray | numeric
        1D vector of values to manipulate.
    to: tuple
        output range (numeric vector of length two)
    from_: tuple
        input range (numeric vector of length two).
        If not given, is calculated from the range of x
    """
    if not from_:
        from_ = np.min(x), np.max(x)
    return np.interp(x, from_, to)


def rescale_mid(x, to=(0, 1), from_=None, mid=0):
    """
    Rescale numeric vector to have specified minimum, midpoint,
    and maximum.

    Parameters
    ----------
    x : ndarray | numeric
        1D vector of values to manipulate.
    to : tuple
        output range (numeric vector of length two)
    from_ : tuple
        input range (numeric vector of length two).
        If not given, is calculated from the range of x
    mid	: numeric
        mid-point of input range
    """
    array_like = True

    try:
        len(x)
    except TypeError:
        array_like = False
        x = [x]

    x = np.asarray(x)
    if not from_:
        from_ = np.array([np.min(x), np.max(x)])

    if (zero_range(from_) or zero_range(to)):
        out = np.repeat(np.mean(to), len(x))
    else:
        extent = 2 * np.max(np.abs(from_ - mid))
        out = (x - mid) / extent * np.diff(to) + np.mean(to)

    if not array_like:
        out = out[0]
    return out


def censor(x, range=(0, 1), only_finite=True):
    """
    Convert any values outside of range to np.NaN

    Parameters
    ----------
    x : array-like
        values to manipulate.
    range: tuple
        (min, max) giving desired output range.
    only_finite : bool
        if True (the default), will only modify
        finite values.

    Returns
    -------
    x : array-like
        Censored array
    """
    intype = None
    if not hasattr(x, 'dtype'):
        intype = type(x)
        x = np.array(x)

    # Not datetime or timedelta
    if x.dtype.kind not in 'Mm':
        if only_finite:
            finite = np.isfinite(x)
        else:
            finite = True

    below = x < range[0]
    above = x > range[1]
    # np.nan is a float therefore x.dtype
    # must be a float. The 'ifs' are to avoid
    # unnecessary type changes
    if any(below) or any(above):
        if issubclass(x.dtype.type, np.integer):
            x = x.astype(np.float)
        x[finite & below] = np.nan
        x[finite & above] = np.nan

    if intype:
        x = intype(x)
    return x


def zero_range(x, tol=np.finfo(float).eps * 100):
    """
    Determine if range of vector is close to zero,
    with a specified tolerance

    Default tolerance is the machine epsilon
    """
    try:
        if len(x) == 1:
            return True
    except TypeError:
        return True

    if len(x) != 2:
        raise GgplotError('x must be length 1 or 2')

    if isinstance(x[0], (pd.Timestamp, datetime.datetime)):
        x = date2num(x)
    elif isinstance(x[0], pd.Timedelta):
        # series preserves the timedelta,
        # then we want them as ints
        x = pd.Series(x).astype(np.int)

    if any(np.isnan(x)):
        return np.nan

    if x[0] == x[1]:
        return True

    if all(np.isinf(x)):
        return False

    m = np.abs(x).min()
    if m == 0:
        return False

    return np.abs((x[0] - x[1]) / m) < tol


def expand_range(range, mul=0, add=0, zero_width=1):
    """
    Expand a range with a multiplicative or additive constant.


    Parameters
    ----------
    range : tuple of size 2
        range of data
    mul : int | float
        multiplicative constract
    add : int | float
        additive constant
    zero_width : int | float
        distance to use if range has zero width
    """
    if range is None:
        return None

    # Enforce tuple
    try:
        range[0]
    except TypeError:
        range = (range, range)

    timestamp = isinstance(range[0], pd.Timestamp)
    timedelta = isinstance(range[0], pd.Timedelta)
    if timestamp:
        range = date2num(range)
    elif timedelta:
        range = pd.Series(range).astype(np.int)

    # The expansion cases
    if zero_range(range):
        erange = (range[0] - zero_width/2,
                  range[0] + zero_width/2)
    else:
        erange = (np.array(range) +
                  np.array([-1, 1]) * (np.diff(range) * mul + add))
        erange = tuple(erange)

    if timestamp:
        erange = tuple(num2date(erange))
    elif timedelta:
        erange = (pd.Timedelta(int(erange[0])),
                  pd.Timedelta(int(erange[1])))
    return erange


def resolution(x, zero=True):
    """
    Compute the resolution of a data vector

    Resolution is smallest non-zero distance between adjacent values

    Parameters
    ----------
    x    : 1D array-like
    zero : Boolean
        Whether to include zero values in the computation

    Result
    ------
    res : resolution of x
        If x is an integer array, then the resolution is 1
    """
    x = np.asarray(x)

    # (unsigned) integers or an effective range of zero
    _x = x[~np.isnan(x)]
    _x = (x.min(), x.max())
    if x.dtype.kind in ('i', 'u') or zero_range(_x):
        return 1

    x = np.unique(x)
    if zero:
        x = np.unique(np.hstack([0, x]))

    return np.min(np.diff(np.sort(x)))


def fullseq(range_, size, pad=False):
    """
    Generate sequence of fixed size intervals covering range.

    Parameters
    ----------
    range_ : array-like
        Range of sequence. Must be of length 2
    size : numeric
        interval size

    Note: This is a port of scales::fullseq.
          Source at https://github.com/hadley/scales
    """
    range_ = np.asarray(range_)
    if zero_range(range_):
        return range_ + size * np.array([-1, 1])/2

    x = seq(
        round_any(range_[0], size, np.floor),
        round_any(range_[1], size, np.ceil),
        size)

    # Add extra bin on bottom and on top, to guarantee that
    # we cover complete range of data, whether right = True/False
    if pad:
        x = np.hstack([np.min(x) - size, x, np.max(x) + size])
    return x


def _parse_break_str(txt):
    """
    Parses '10 weeks' into tuple (10, week).

    Helper for date_breaks
    """
    txt = txt.strip()
    if len(txt.split()) == 2:
        n, units = txt.split()
    else:
        n, units = 1, txt
    units = units.rstrip('s')  # e.g. weeks => week
    n = int(n)
    return n, units

# matplotlib's YearLocator uses different named
# arguments than the others
LOCATORS = {
    'minute': MinuteLocator,
    'hour': HourLocator,
    'day': DayLocator,
    'week': WeekdayLocator,
    'month': MonthLocator,
    'year': lambda interval: YearLocator(base=interval)
}


def date_breaks(width):
    """
    "Regularly spaced dates."

    Parameters:
    -----------
    width: str
        an interval specification. Must be one of
        [minute, hour, day, week, month, year]

    Example:
    --------
    >>> date_breaks(width = '1 year')
    >>> date_breaks(width = '6 weeks')
    >>> date_breaks('months')
    """
    period, units = _parse_break_str(width)
    Locator = LOCATORS[units]

    def make_locator():
        return Locator(interval=period)

    return make_locator


def date_format(format='%Y-%m-%d'):
    """
    Formatted dates.

    Parameters:
    -----------
    format : str
        Date format using standard strftime format.

    Example:
    --------
    >>> date_format('%b-%y')
    >>> date_format('%B %d, %Y')
    """
    def make_formatter():
        return DateFormatter(format)

    return make_formatter


class TimedeltaFormatter(Formatter):
    def __call__(self, x, pos=0):
        return str(pd.Timedelta(x))


class defaultLocator(MaxNLocator):
    trans_name = ''

    def __init__(self, nbins=5, steps=(1, 2, 5, 10)):
        MaxNLocator.__init__(self, nbins=nbins, steps=steps)


class DateLocator(AutoDateLocator):
    trans_name = ''

    def __init__(self):
        AutoDateLocator.__init__(self, minticks=5, interval_multiples=True)
        from matplotlib.dates import YEARLY
        self.intervald[YEARLY] = [5, 50]


class defaultMinorLocator(AutoMinorLocator):
    trans_name = ''

    def __init__(self):
        AutoMinorLocator.__init__(self, n=2)


# Transforms #

# To create the effect where by the scales are labelled in
# data space when the data plotted is in a transformed space,
# we use the default Locator (MaxNLocator) and default Formatter
# (ScalarFormatter). The Locator calculates ticks in data space
# and returns them in transformed space and the Formatter
# returns a label based on data space.
def make_locator(transform, inverse):
    class transformLocator(defaultLocator):
        trans_name = ''

        def __call__(self):
            # Transformed space
            vmin, vmax = self.axis.get_view_interval()
            vmin, vmax = self._clip_probability(vmin, vmax)

            # Original data space
            vmin, vmax = inverse(vmin), inverse(vmax)
            ticks = self.tick_values(vmin, vmax)

            # Transformed space
            try:
                ticks = transform(ticks)
            except TypeError:
                ticks = [transform(t) for t in ticks]
            return ticks

        def _clip_probability(self, vmin, vmax):
            """
            Make sure vmin and vmax are in the [0, 1]
            range if the transform is a probability
            distribution
            """
            if self.trans_name.startswith('prob-'):
                if vmin < 0:
                    vmin = 0

                if vmax > 1:
                    vmax = 1

            return vmin, vmax

    return transformLocator


def make_minor_locator(transform, inverse):
    class transformMinorLocator(defaultMinorLocator):
        trans_name = ''

        def __call__(self):
            'Return the locations of the ticks'
            majorlocs = self.axis.get_majorticklocs()
            majorlocs = [inverse(l) for l in majorlocs]

            try:
                majorstep = majorlocs[1] - majorlocs[0]
            except IndexError:
                majorstep = 0

            ndivs = self.ndivs
            minorstep = majorstep / ndivs
            vmin, vmax = self.axis.get_view_interval()

            # To original data space
            vmin, vmax = inverse(vmin), inverse(vmax)

            # Calculate locations
            if vmin > vmax:
                vmin, vmax = vmax, vmin

            if len(majorlocs) > 0:
                t0 = majorlocs[0]
                tmin = ((vmin - t0) // minorstep + 1) * minorstep
                tmax = ((vmax - t0) // minorstep + 1) * minorstep
                locs = np.arange(tmin, tmax, minorstep) + t0
                cond = np.abs((locs - t0) % majorstep) > minorstep / 10.0
                locs = locs.compress(cond)
            else:
                locs = []

            # Back to transformed space
            locs = [transform(l) for l in locs]
            return self.raise_if_exceeds(np.array(locs))

    return transformMinorLocator


# how to label(format) the break strings
def make_formatter(inverse):
    class transformFormatter(ScalarFormatter):

        def __init__(self):
            ScalarFormatter.__init__(self, useOffset=False)

        def __call__(self, x, pos=None):
            # Original data space
            x = inverse(x)
            label = ScalarFormatter.__call__(self, x, pos)
            # Remove unnecessary decimals
            pattern = re.compile(r'\.0+$')
            match = re.search(pattern, label)
            if match:
                label = re.sub(pattern, '', label)
            return label
    return transformFormatter


def trans_new(name, transform, inverse,
              breaks=None, format_=None,
              domain=(-np.inf, np.inf)):
    """
    Create a transform class

    This class is used to transform data and also tell the
    x and y axes how to create and label the tick locations.

    Parameters
    ----------
    name : str
        Name of the transform
    transform : function
        Preferrably a ufunc
    inverse : function
        Preferrably a ufunc
    breaks : array-like
    format_ : str
        format string
    domain : tuple

    Returns
    -------
    out : trans
        Transform class
    """
    trans_name = str('{}_trans'.format(name))

    class klass(object):
        aesthetic = None

        def modify_axis(self, ax):
            """
            Modify the xaxis and yaxis

            Set the locator and formatter
            """
            if self.aesthetic not in ('x', 'y'):
                return

            # xaxis or yaxis
            axis = '{}axis'.format(self.aesthetic)
            obj = getattr(ax, axis)
            if not is_waive(self.breaks_locator):
                obj.set_major_locator(self.breaks_locator())

            if not is_waive(self.minor_breaks_locator):
                obj.set_minor_locator(self.minor_breaks_locator())

            if not is_waive(self.labels_formatter):
                obj.set_major_formatter(self.labels_formatter())

    klass.__name__ = trans_name
    klass.name = name
    klass.transform = staticmethod(transform)
    klass.inverse = staticmethod(inverse)
    # Each axis requires a separate locator(MPL requirement),
    # and for consistency we used separate formatters too.
    klass.breaks_locator = make_locator(transform, inverse)
    klass.breaks_locator.trans_name = trans_name
    klass.labels_formatter = make_formatter(inverse)
    klass.minor_breaks_locator = make_minor_locator(transform, inverse)
    klass.minor_breaks_locator.trans_name = trans_name
    return klass


def log_trans(base=None):
    # transform function
    if base is None:
        name = 'log'
        base = np.exp(1)
        transform = np.log
    elif base == 10:
        name = 'log10'
        transform = np.log10
    elif base == 2:
        name = 'log2'
        transform = np.log2
    else:
        name = 'log{}'.format(base)

        def trans(x):
            return np.log(x)/np.log(base)

    # inverse function
    def inverse(x):
        return x ** base
    return trans_new(name, transform, inverse)


def exp_trans(base=None):
    # default to e
    if base is None:
        name = 'power-e'
        base = np.exp(1)
    else:
        name = 'power-{}'.format(base)

    # transform function
    def transform(x):
        return base ** x

    # inverse function
    def inverse(x):
        return np.log(x)/np.log(base)

    return trans_new(name, transform, inverse)

log10_trans = log_trans(10)
log2_trans = log_trans(2)
log1p_trans = trans_new('log1p', np.log1p, np.expm1)
identity_trans = trans_new('identity', identity, identity)
reverse_trans = trans_new('reverse', np.negative, np.negative)
sqrt_trans = trans_new('sqrt', np.sqrt, np.square, domain=(0, np.inf))
asn_trans = trans_new('asn',
                      lambda x: 2*np.arcsin(np.sqrt(x)),
                      lambda x: np.sin(x/2)**2)
atanh_trans = trans_new('atanh', np.arctanh, np.tanh)


def boxcox_trans(p):
    if np.abs(p) < 1e-7:
        return log_trans

    def transform(x):
        return (x**p - 1) / (p * np.sign(x-1))

    def inverse(x):
        return (np.abs(x) * p + np.sign(x)) ** (1 / p)

    return trans_new('pow-{}'.format(p), transform, inverse)


# Probability transforms
def probability_trans(distribution, *args, **kwargs):
    cdists = {k for k in dir(stats) if hasattr(getattr(stats, k), 'cdf')}
    if distribution not in cdists:
        msg = "Unknown distribution '{}'"
        raise GgplotError(msg.format(distribution))

    def transform(x):
        return getattr(stats, distribution).cdf(x, *args, **kwargs)

    def inverse(x):
        return getattr(stats, distribution).ppf(x, *args, **kwargs)

    return trans_new('prob-{}'.format(distribution), transform, inverse)


def datetime_trans():
    def transform(x):
        try:
            x = date2num(x)
        except AttributeError:
            # numpy datetime64
            x = [pd.Timestamp(item) for item in x]
            x = date2num(x)
        return x

    def inverse(x):
        return num2date(x)

    def _DateFormatter():
        return DateFormatter('%Y-%m-%d')

    _trans = trans_new('datetime', transform, inverse)
    _trans.breaks_locator = staticmethod(DateLocator)
    _trans.minor_breaks_locator = staticmethod(defaultMinorLocator)
    _trans.labels_formatter = staticmethod(_DateFormatter)
    return _trans


def timedelta_trans():
    def transform(x):
        try:
            iter(x)
            x = pd.Series(x).astype(np.int)
        except TypeError:
            x = np.int(x)
        return x

    def inverse(x):
        try:
            x = [pd.Timedelta(int(i)) for i in x]
        except TypeError:
            x = pd.Timedelta(int(x))
        return x

    _trans = trans_new('timedelta', transform, inverse)
    _trans.breaks_locator = staticmethod(defaultLocator)
    _trans.minor_breaks_locator = staticmethod(defaultMinorLocator)
    _trans.labels_formatter = staticmethod(TimedeltaFormatter)
    return _trans


def gettrans(t):
    """
    Return a trans object

    Parameters
    ----------
    t : string | function | class | object
        name of transformation function

    Returns
    -------
    out : tran
    """
    obj = t
    # Make sure trans object is instantiated
    if isinstance(obj, six.string_types):
        obj = gg_import('{}_trans'.format(obj))
    if isinstance(obj, FunctionType):
        obj = obj()
    if isinstance(obj, type):
        obj = obj()
    return obj

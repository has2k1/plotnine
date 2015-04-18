from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import re

import numpy as np
import pandas as pd
import scipy.stats as stats
from matplotlib.ticker import MaxNLocator, ScalarFormatter
import six

from ..utils import round_any, identity, is_waive, gg_import
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

    if 'datetime64' not in str(x.dtype):
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

    # TODO: Get rid of this copout and find a way to deal
    # with timestamps
    if type(x[0]) == pd.Timestamp:
        return False

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

    if zero_range(range):
        erange = (range[0] - zero_width/2,
                  range[0] + zero_width/2)
    # TODO: Get rid of this copout and find a way to deal
    # with timestamps
    elif type(range[0]) == pd.Timestamp:
        erange = range
    else:
        erange = (np.array(range) +
                  np.array([-1, 1]) * (np.diff(range) * mul + add))
        erange = tuple(erange)
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

    num = np.int(np.floor(np.ptp(range_)/size + size))
    x = np.linspace(
        round_any(range_[0], size, np.floor),
        round_any(range_[1], size, np.ceil),
        num)

    # Add extra bin on bottom and on top, to guarantee that
    # we cover complete range of data, whether right = True/False
    if pad:
        x = np.hstack([np.min(x) - size, x, np.max(x) + size])
    return x


# Transforms

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
    # To create the effect where by the scales are labelled in
    # data space when the data plotted is in a transformed space,
    # we use the default Locator (MaxNLocator) and default Formatter
    # (ScalarFormatter). The Locator calculates ticks in data space
    # and returns them in transformed space and the Formatter
    # returns a label based on data space.

    # FIXME: breaks and format_ are ignored
    class cls(object):
        aesthetic = None
        trans = staticmethod(transform)
        inv = staticmethod(inverse)

        # @staticmethod
        # def trans(series):
        #     try:
        #         return pd.Series(transform(series))
        #     except TypeError:
        #         return pd.Series([transform(x) for x in series])
        #
        # @staticmethod
        # def inv(series):
        #     try:
        #         return pd.Series(inverse(series))
        #     except TypeError:
        #         return pd.Series([inverse(x) for x in series])

        def modify_axis(self, axs):
            """
            Modify the xaxis and yaxis

            Set the locator and formatter
            """
            if self.name == 'identity':
                return

            if self.aesthetic not in ('x', 'y'):
                return

            # xaxis or yaxis
            axis = '{}axis'.format(self.aesthetic)

            if not is_waive(self.locator_factory):
                for ax in axs:
                    obj = getattr(ax, axis)
                    obj.set_major_locator(self.locator_factory())

            if not is_waive(self.formatter):
                for ax in axs:
                    obj = getattr(ax, axis)
                    obj.set_major_formatter(self.formatter)

        class transformLocator(MaxNLocator):
            def __init__(self, nbins=8, steps=(1, 2, 5, 10)):
                MaxNLocator.__init__(self, nbins=nbins, steps=steps)

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
                if cls.__name__.startswith('prob-'):
                    if vmin < 0:
                        vmin = 0

                    if vmax > 1:
                        vmax = 1

                    print('clipped')

                return vmin, vmax

        # how to label(format) the break strings
        class transformFormatter(ScalarFormatter):

            def __call__(self, x, pos=None):
                # Original data space
                x = inverse(x)
                label = ScalarFormatter.__call__(self, x, pos)
                pattern = re.compile('\.0+$')
                match = re.search(pattern, label)
                if match:
                    label = re.sub(pattern, '', label)
                return label

        # In case of faceted plots, each ax needs it's own locator
        # so we want something that can give us identical locator
        # objects
        locator_factory = transformLocator
        formatter = transformFormatter()

    cls.name = name
    cls.breaks = cls.locator_factory  # to match ggplot2
    cls.format = cls.formatter        # to match ggplot2
    cls.__name__ = str('{}_trans'.format(name))
    return cls


def log_trans(base=None):
    # transform function
    if base is None:
        name = 'log'
        base = np.exp(1)
        trans = np.log
    elif base == 10:
        name = 'log10'
        trans = np.log10
    elif base == 2:
        name = 'log2'
        trans = np.log2
    else:
        name = 'log{}'.format(base)

        def trans(x):
            np.log(x)/np.log(base)

    # inverse function
    def inv(x):
        return x ** base
    return trans_new(name, trans, inv)


def exp_trans(base=None):
    # transform function
    if base is None:
        name = 'power-e'
        base = np.exp(1)
    else:
        name = 'power-{}'.format(base)

    # trans function
    def trans(x):
        base ** x

    # inverse function
    def inv(x):
        return np.log(x)/np.log(base)

    return trans_new(name, trans, inv)

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

    def trans(x):
        return (x**p - 1) / (p * np.sign(x-1))

    def inv(x):
        return (np.abs(x) * p + np.sign(x)) ** (1 / p)

    return trans_new('pow-{}'.format(p), trans, inv)


# Probability transforms
def probability_trans(distribution, *args, **kwargs):
    cdists = {k for k in dir(stats) if hasattr(getattr(stats, k), 'cdf')}
    if distribution not in cdists:
        msg = "Unknown distribution '{}'"
        raise GgplotError(msg.format(distribution))

    def trans(x):
        return getattr(stats, distribution).cdf(x, *args, **kwargs)

    def inv(x):
        return getattr(stats, distribution).ppf(x, *args, **kwargs)

    return trans_new('prob-{}'.format(distribution), trans, inv)


def gettrans(t):
    """
    Return a trans object

    Parameters
    ----------
    t : string | function
        name of transformation function

    Returns
    -------
    out : tran
    """
    # Make sure trans object is instantiated
    if isinstance(t, six.string_types):
        out = gg_import(t+'_trans')()
    elif(isinstance(t, type)):
        out = t()
    return out

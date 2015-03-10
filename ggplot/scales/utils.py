from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import math

import numpy as np
import pandas as pd

from ..utils import round_any
from ..utils.exceptions import GgplotError


def drange(start, stop, step):
    """Compute the steps in between start and stop

    Only steps which are a multiple of `step` are used.

    """
    r = ((start // step) * step) + step # the first step higher than start
    # all subsequent steps are multiple of "step"!
    while r < stop:
        yield r
        r += step

def convert_if_int(x):
    if int(x)==x:
        return int(x)
    else:
        return x

def convertable_to_int(x):
    if int(x)==x:
        return True
    else:
        return False


def calc_axis_breaks_and_limits(minval, maxval, nlabs=None):
    """Calculates axis breaks and suggested limits.

    The limits are computed as minval/maxval -/+ 1/3 step of ticks.

    Parameters
    ----------
    minval : number
      lowest value on this axis
    maxval : number
      higest number on this axis
    nlabs : int
      number of labels which should be displayed on the axis
      Default: None
    """
    if nlabs is None:
        diff = maxval - minval
        base10 = math.log10(diff)
        power = math.floor(base10)
        base_unit = 10**power
        step = base_unit / 2
    else:
        diff = maxval - minval
        tick_range = diff / float(nlabs)
        # make the tick range nice looking...
        power = math.ceil(math.log(tick_range, 10))
        step = np.round(tick_range / (10**power), 1) * 10**power

    labs = list(drange(minval-(step/3), maxval+(step/3), step))

    if all([convertable_to_int(lab) for lab in labs]):
        labs = [convert_if_int(lab) for lab in labs]

    return labs, minval-(step/3), maxval+(step/3)


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

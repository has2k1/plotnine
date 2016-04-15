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
import datetime

import numpy as np
import pandas as pd
import scipy.stats as stats
from matplotlib.dates import MinuteLocator, HourLocator, DayLocator
from matplotlib.dates import WeekdayLocator, MonthLocator, YearLocator
from matplotlib.dates import DateFormatter
from matplotlib.dates import date2num, num2date
from matplotlib.colors import LinearSegmentedColormap, rgb2hex
from matplotlib.cm import get_cmap
import palettable.colorbrewer as colorbrewer

from ..utils import palettes
from ..utils import seq, round_any
from ..utils.exceptions import GgplotError, gg_warn


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
    else:
        from_ = np.asarray(from_)

    if (zero_range(from_) or zero_range(to)):
        out = np.repeat(np.mean(to), len(x))
    else:
        extent = 2 * np.max(np.abs(from_ - mid))
        out = (x - mid) / extent * np.diff(to) + np.mean(to)

    if not array_like:
        out = out[0]
    return out


def rescale_max(x, to=(0, 1), from_=None):
    """
    Rescale numeric vector to have specified maximum.

    Parameters
    ----------
    x : ndarray | numeric
        1D vector of values to manipulate.
    to : tuple
        output range (numeric vector of length two)
    from_ : tuple
        input range (numeric vector of length two).
        If not given, is calculated from the range of x
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

    out = x/from_[1] * to[1]

    if not array_like:
        out = out[0]
    return out


# Palette making utilities #

def area_pal(range=(1, 6)):
    """
    Point area palette (continuous).

    Parameters
    ----------
    range : tuple
        Numeric vector of length two, giving range of possible sizes.
        Should be greater than 0.
    """
    def area_palette(x):
        return rescale(np.sqrt(x), range, (0, 1))
    return area_palette


def grey_pal(start=0.2, end=0.8):
    """
    Utility for creating discrete grey scale palette
    """
    gamma = 2.2
    ends = ((0.0, start, start), (1.0, end, end))
    cdict = {'red': ends, 'green': ends, 'blue': ends}
    grey_cmap = LinearSegmentedColormap('grey', cdict)

    def func(n):
        colors = []
        # The grey scale points are linearly separated in
        # gamma encoded space
        for x in np.linspace(start**gamma, end**gamma, n):
            # Map points onto the [0, 1] palette domain
            x = (x ** (1./gamma) - start) / (end - start)
            colors.append(rgb2hex(grey_cmap(x)))
        return colors
    return func


def hue_pal(h=.01, l=.6, s=.65, color_space='hls'):
    """
    Utility for making hue palettes for color schemes.
    """
    if not all([0 <= val <= 1 for val in (h, l, s)]):
        msg = ("hue_pal expects values to be between 0 and 1. "
               " I got h={}, l={}, s={}".format(h, l, s))
        raise GgplotError(msg)

    if color_space not in ('hls', 'husl'):
        msg = "color_space should be one of ['hls', 'husl']"
        raise GgplotError(msg)

    palette = getattr(palettes, '{}_palette'.format(color_space))

    def func(n):
        colors = palette(n, h=h, l=l, s=s)
        return [rgb2hex(c) for c in colors]
    return func


def brewer_pal(type='seq', palette=1):
    """
    Utility for making a brewer palette
    """
    def _handle_shorthand(text):
        abbrevs = {
            "seq": "Sequential",
            "qual": "Qualitative",
            "div": "Diverging"
        }
        text = abbrevs.get(text, text)
        return text.title()

    def _number_to_palette(ctype, n):
        n -= 1
        palettes = sorted(colorbrewer.COLOR_MAPS[ctype].keys())
        if n < len(palettes):
            return palettes[n]

    def _max_palette_colors(type, palette_name):
        """
        Return the number of colors in the brewer palette
        """
        if type == 'Sequential':
            return 9
        elif type == 'Diverging':
            return 11
        else:
            # Qualitative palettes have different limits
            qlimit = {"Accent": 8, "Dark": 8, "Paired": 12,
                      "Pastel1": 9, "Pastel2": 8, "Set1": 9,
                      "Set2": 8, "Set3": 12}
            return qlimit[palette_name]

    type = _handle_shorthand(type)
    if isinstance(palette, int):
        palette_name = _number_to_palette(type, palette)
    else:
        palette_name = palette
    nmax = _max_palette_colors(type, palette_name)

    def func(n):
        # Only draw the maximum allowable colors from the palette
        # and fill any remaining spots with None
        _n = n if n <= nmax else nmax
        bmap = colorbrewer.get_map(palette_name, type, _n)
        hex_colors = bmap.hex_colors
        if n > nmax:
            msg = ("Warning message:"
                   "Brewer palette {} has a maximum of {} colors"
                   "Returning the palette you asked for with"
                   "that many colors")
            gg_warn(msg.format(palette_name, nmax))
            hex_colors = hex_colors + [None] * (n - nmax)
        return hex_colors
    return func


def ratios_to_colors(values, colormap):
    """
    Map values in the range [0, 1] onto colors

    Parameters
    ----------
    values : array_like | float
        Numeric(s) in the range [0, 1]
    colormap : cmap
        Matplotlib colormap to use for the mapping

    Returns
    -------
    out : list | float
        Color(s) corresponding to the values
    """
    color_tuples = colormap(values)
    try:
        hex_colors = [rgb2hex(t) for t in color_tuples]
    except IndexError:
        hex_colors = rgb2hex(color_tuples)
    return hex_colors


def gradient_n_pal(colors, values=None, name='gradientn'):
    # Note: For better results across devices and media types,
    # it would be better to do the interpolation in
    # Lab color space.
    if values is None:
        colormap = LinearSegmentedColormap.from_list(
            name, colors)
    else:
        colormap = LinearSegmentedColormap.from_list(
            name, list(zip(values, colors)))

    def cmap_palette(vals):
        return ratios_to_colors(vals, colormap)

    return cmap_palette


def cmap_pal(name=None, lut=None):
    colormap = get_cmap(name, lut)

    def cmap_palette(vals):
        return ratios_to_colors(vals, colormap)

    return cmap_palette


def abs_area(max):
    """
    Point area palette (continuous), with area proportional to value.

    Parameters
    ----------
    max : float
        A number representing the maximum size
    """
    def abs_area_palette(x):
        return rescale(np.sqrt(np.abs(x)), (0, max), (0, 1))
    return abs_area_palette


def squish_infinite(x, range=(0, 1)):
    intype = None
    if not hasattr(x, 'dtype'):
        intype = type(x)
        x = np.array(x)

    x[x == -np.inf] = range[0]
    x[x == np.inf] = range[1]

    if intype:
        x = intype(x)
    return x


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

    outside = (x < range[0]) | (x > range[1])
    flags = finite & outside
    # np.nan is a float therefore x.dtype
    # must be a float. The 'ifs' are to avoid
    # unnecessary type changes
    if any(flags):
        if x.dtype.kind == 'i':
            x = x.astype(np.float)
        x[flags] = np.nan

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


def iqr(a):
    """
    Calculate the IQR for an array of numbers.
    """
    a = np.asarray(a)
    q1 = stats.scoreatpercentile(a, 25)
    q3 = stats.scoreatpercentile(a, 75)
    return q3 - q1


def freedman_diaconis_bins(a):
    """
    Calculate number of hist bins using Freedman-Diaconis rule.
    """
    # From http://stats.stackexchange.com/questions/798/
    a = np.asarray(a)
    h = 2 * iqr(a) / (len(a) ** (1 / 3))

    # fall back to sqrt(a) bins if iqr is 0
    if h == 0:
        bins = np.ceil(np.sqrt(a.size))
    else:
        bins = np.ceil((a.max() - a.min()) / h)

    return np.int(bins)

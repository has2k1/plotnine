import numpy as np
import pandas as pd
import scipy.stats as stats
from mizani.utils import round_any

from ..scales.scale import scale_discrete
from ..exceptions import PlotnineError

__all__ = ['freedman_diaconis_bins', 'breaks_from_bins',
           'breaks_from_binwidth', 'assign_bins',
           'fuzzybreaks']


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
        bins = np.ceil((np.nanmax(a) - np.nanmin(a)) / h)

    return np.int(bins)


def breaks_from_binwidth(x_range, binwidth=None, center=None,
                         boundary=None):
    """
    Calculate breaks given binwidth

    Parameters
    ----------
    x_range : array_like
        Range over with to calculate the breaks. Must be
        of size 2.
    binwidth : float
        Separation between the breaks
    center : float
        The center of one of the bins
    boundary : float
        A boundary between two bins

    Returns
    -------
    out : array_like
        Sequence of break points.
    """
    if binwidth <= 0:
        raise PlotnineError("The 'binwidth' must be positive.")

    if boundary is not None and center is not None:
        raise PlotnineError("Only one of 'boundary' and 'center' "
                            "may be specified.")
    elif boundary is None:
        if center is None:
            # This puts min and max of data in outer half
            # of their bins
            boundary = binwidth/2
        else:
            boundary = center - binwidth/2

    epsilon = np.finfo(float).eps
    shift = np.floor((x_range[0]-boundary)/binwidth)
    origin = boundary + shift * binwidth
    # The (1-epsilon) factor prevents numerical roundoff in the
    # binwidth from creating an extra break beyond the one that
    # includes x_range[1].
    max_x = x_range[1]+binwidth*(1-epsilon)
    breaks = np.arange(origin, max_x, binwidth)
    return breaks


def breaks_from_bins(x_range, bins=30, center=None, boundary=None):
    """
    Calculate breaks given binwidth

    Parameters
    ----------
    x_range : array_like
        Range over with to calculate the breaks. Must be
        of size 2.
    bins : int
        Number of bins
    center : float
        The center of one of the bins
    boundary : float
        A boundary between two bins

    Returns
    -------
    out : array_like
        Sequence of break points.
    """
    if bins < 1:
        raise PlotnineError("Need at least one bin.")
    elif bins == 1:
        binwidth = x_range[1] - x_range[0]
        boundary = x_range[1]
    else:
        binwidth = (x_range[1]-x_range[0])/(bins-1)

    return breaks_from_binwidth(x_range, binwidth, center, boundary)


def assign_bins(x, breaks, weight=None, pad=False, closed='right'):
    """
    Assign value in x to bins demacated by the break points

    Parameters
    ----------
    x : array_like
        Values to be binned.
    breaks : array_like
        Sequence of break points.
    weight : array_like
        Weight of each value in `x`. Used in creating the frequency
        table. If `None`, then each value in `x` has a weight of 1.
    pad : bool
        If `True`, add empty bins at either end of `x`.
    closed : str in ``['right', 'left']``
        Whether the right or left edges of the bins are part of the
        bin.

    Returns
    -------
    out : dataframe
        Bin count and density information.
    """
    right = closed == 'right'
    # If weight not supplied to, use one (no weight)
    if weight is None:
        weight = np.ones(len(x))
    else:
        weight = np.asarray(weight)
        weight[np.isnan(weight)] = 0

    bin_idx = pd.cut(x, bins=breaks, labels=False,
                     right=right, include_lowest=True)
    bin_widths = np.diff(breaks)
    bin_x = (breaks[:-1] + breaks[1:]) * 0.5

    # Create a dataframe with two columns:
    #   - the bins to which each x is assigned
    #   - the weight of each x value
    # Then create a weighted frequency table
    df = pd.DataFrame({'bin_idx': bin_idx, 'weight': weight})
    wftable = df.pivot_table(
        'weight', index=['bin_idx'], aggfunc=np.sum)['weight']

    # Empty bins get no value in the computed frequency table.
    # We need to add the zeros and since frequency table is a
    # Series object, we need to keep it ordered
    if len(wftable) < len(bin_x):
        empty_bins = set(range(len(bin_x))) - set(bin_idx)
        for b in empty_bins:
            wftable.loc[b] = 0
        wftable = wftable.sort_index()
    bin_count = wftable.tolist()

    if pad:
        bw0 = bin_widths[0]
        bwn = bin_widths[-1]
        bin_count = np.hstack([0, bin_count, 0])
        bin_widths = np.hstack([bw0, bin_widths, bwn])
        bin_x = np.hstack([bin_x[0]-bw0, bin_x, bin_x[-1]+bwn])

    return result_dataframe(bin_count, bin_x, bin_widths)


def result_dataframe(count, x, width, xmin=None, xmax=None):
    """
    Create a dataframe to hold bin information
    """
    if xmin is None:
        xmin = x-width/2

    if xmax is None:
        xmax = x+width/2

    # Eliminate any numerical roundoff discrepancies
    # between the edges
    xmin[1:] = xmax[:-1]
    density = (count/width) / np.sum(np.abs(count))

    out = pd.DataFrame({
        'count': count,
        'x': x,
        'xmin': xmin,
        'xmax': xmax,
        'width': width,
        'density': density,
        'ncount': count/np.max(np.abs(count)),
        'ndensity': count/np.max(np.abs(density))})
    return out


def fuzzybreaks(scale, breaks=None, boundary=None,
                binwidth=None, bins=30, right=True):
    """
    Compute fuzzy breaks

    For a continuous scale, fuzzybreaks "preserve" the range of
    the scale. The fuzzing is close to numerical roundoff and
    is visually imperceptible.

    Parameters
    ----------
    scale : scale
        Scale
    breaks : array_like
        Sequence of break points. If provided and the scale is not
        discrete, they are returned.
    boundary : float
        First break. If `None` a suitable on is computed using
        the range of the scale and the binwidth.
    binwidth : float
        Separation between the breaks
    bins : int
        Number of bins
    right : bool
        If `True` the right edges of the bins are part of the
        bin. If `False` then the left edges of the bins are part
        of the bin.

    Returns
    -------
    out : array_like
    """
    # Bins for categorical data should take the width
    # of one level, and should show up centered over
    # their tick marks. All other parameters are ignored.
    if isinstance(scale, scale_discrete):
        breaks = scale.get_breaks()
        return -0.5 + np.arange(1, len(breaks)+2)
    else:
        if breaks is not None:
            breaks = scale.transform(breaks)

    if breaks is not None:
        return breaks

    recompute_bins = binwidth is not None
    srange = scale.limits

    if binwidth is None or np.isnan(binwidth):
        binwidth = (srange[1]-srange[0]) / bins

    if boundary is None or np.isnan(boundary):
        boundary = round_any(srange[0], binwidth, np.floor)

    if recompute_bins:
        bins = np.int(np.ceil((srange[1]-boundary)/binwidth))

    # To minimise precision errors, we do not pass the boundary and
    # binwidth into np.arange as params. The resulting breaks
    # can then be adjusted with finer(epsilon based rather than
    # some arbitrary small number) precision.
    breaks = np.arange(boundary, srange[1]+binwidth, binwidth)
    return _adjust_breaks(breaks, right)


def _adjust_breaks(breaks, right):
    epsilon = np.finfo(float).eps
    plus = 1+epsilon
    minus = 1-epsilon

    # fuzzy breaks to protect from floating point rounding errors
    if right:
        fuzz = np.hstack(
            [minus, np.repeat(plus, len(breaks)-1)])
    else:
        fuzz = np.hstack(
            [np.repeat(minus, len(breaks)-1), plus])

    fuzzybreaks = breaks * fuzz
    return fuzzybreaks

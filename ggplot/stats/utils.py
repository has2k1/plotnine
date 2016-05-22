from __future__ import absolute_import, division, print_function

import numpy as np
import scipy.stats as stats


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

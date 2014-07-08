from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from six import string_types

import numpy as np
import scipy.stats
import pandas as pd

from ggplot.utils import make_iterable_ntimes
from .stat import stat


def bootstrap_statistics(series, statistic, n_samples=1000, confidence_interval=0.95):
    """
    Default parameters taken from
    R's Hmisc smean.cl.boot
    """
    alpha = 1 - confidence_interval
    inds = np.random.randint(0, len(series), size=(n_samples, len(series)))
    samples = series.values[inds]
    means = np.sort(statistic(samples, axis=1))
    return pd.Series({'ymin': means[int((alpha/2)*n_samples)],
                      'ymax': means[int((1-alpha/2)*n_samples)],
                      'y': statistic(series)})


def mean_cl_boot(series, n_samples=1000, confidence_interval=0.95):
    return bootstrap_statistics(series, np.mean, n_samples=n_samples, confidence_interval=confidence_interval)


def mean_cl_normal(series, confidence_interval=0.95):
    """
    Adapted from http://stackoverflow.com/a/15034143
    """
    a = np.asarray(series)
    m = np.mean(a)
    se = scipy.stats.sem(a)
    h = se * scipy.stats.t._ppf((1+confidence_interval)/2, len(a)-1)
    return pd.Series({'y': m,
                      'ymin': m-h,
                      'ymax': m+h})


def mean_sdl(series, mult=2):
    m = series.mean()
    s = series.std()
    return pd.Series({'y': m,
                      'ymin': m-mult*s,
                      'ymax': m+mult*s})


def median_hilow(series, confidence_interval=0.95):
    tail = (1 - confidence_interval) / 2
    return pd.Series({'y': np.median(series),
                      'ymin': np.percentile(series, 100 * tail),
                      'ymax': np.percentile(series, 100 * (1 - tail))})


# TODO: Implement remaining functions provided in stat_summary (mean_cl_normal,
# median_hilow, see
# https://github.com/hadley/ggplot2/blob/master/R/stat-summary.r)

function_dict = {'mean_cl_boot': mean_cl_boot,
                 'mean_cl_normal': mean_cl_normal,
                 'mean_sdl': mean_sdl,
                 'median_hilow': median_hilow}


def combined_fun_data(series, fun_y, fun_ymin, fun_ymax):
    d = {}
    if fun_y:
        d['y'] = fun_y(series)
    if fun_ymin:
        d['ymin'] = fun_ymin(series)
    if fun_ymax:
        d['ymax'] = fun_ymax(series)
    return pd.Series(d)


class stat_summary(stat):
    """
    Calculate summary statistics depending on x, usually by
    calculating three values ymin, y and ymax for each value of x.

    Parameters
    ----------

    fun_data : string or function
        One of `"mean_cl_boot"`, `"mean_cl_normal"`, `"mean_sdl"`, `"median_hilow"` or
        any function that takes a pandas series and returns a series with three
        rows indexed as `y`, `ymin` and `ymax`. Defaults to `"mean_cl_boot"`.
    fun_y, fun_ymin, fun_ymax : function
        Any function that takes a pandas series and returns a value


    Notes
    -----

    If any of `fun_y`, `fun_ymin` or `fun_ymax` are provided, the value of
    `fun_data` will be ignored.


    As R's syntax `fun.data = some_function` is not valid in python, here
    `fun_data = somefunction` is used for now.

    Examples
    --------


    General usage:

    .. plot::
        :include-source:

        from ggplot import *

        ggplot(aes(x='cut', y='carat'), data=diamonds) \
            + stat_summary(fun_data = 'mean_cl_boot')

    Provide own function:

    .. plot::
        :include-source:

        import numpy as np
        from ggplot import *
        def median_quantile(series):
            return pd.Series({'y': np.median(series),
                              'ymin': np.percentile(series, 5),
                              'ymax': np.percentile(series, 95)})
        ggplot(aes(x='cut', y='carat'), data=diamonds) \
            + stat_summary(fun_data = median_quantile)

    Provide different funtions for y, ymin and ymax:

    .. plot:
        :include-source:

        import numpy as np
        from ggplot import *
        ggplot(aes(x='cut', y='carat'), data=diamonds) \
            + stat_summary(fun_y = np.median, fun_ymin=np.min, fun_ymax=np.max)

    """
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'pointrange', 'position': 'identity', 'fun_data': 'mean_cl_boot',
                      'fun_y': None, 'fun_ymin': None, 'fun_ymax': None}
    CREATES = {'ymin', 'ymax'}

    def _calculate(self, data):

        if self.params['fun_y'] or self.params['fun_ymin'] or self.params['fun_ymax']:
            fun_data = lambda s: combined_fun_data(s, self.params['fun_y'], self.params['fun_ymin'], self.params['fun_ymax'])
        elif isinstance(self.params['fun_data'], string_types):
            fun_data = function_dict[self.params['fun_data']]
        else:
            fun_data = self.params['fun_data']

        new_data = data.groupby('x').apply(lambda df: fun_data(df['y'])).reset_index()
        data.pop('x')
        data.pop('y')

        # Copy the other aesthetics into the new dataframe
        n = len(new_data.x)
        for ae in data:
            new_data[ae] = make_iterable_ntimes(data[ae].iloc[0], n)
        return new_data

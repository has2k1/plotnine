from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from six import string_types

import numpy as np
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


def mean_sdl(series, mult=2):
    m = series.mean()
    s = series.std()
    return pd.Series({'y': m,
                      'ymin': m-mult*s,
                      'ymax': m+mult*s})


# TODO: Implement remaining functions provided in stat_summary (mean_cl_normal,
# median_hilow, see
# https://github.com/hadley/ggplot2/blob/master/R/stat-summary.r)

function_dict = {'mean_cl_boot': mean_cl_boot,
                 'mean_sdl': mean_sdl}


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
    As R's syntax `fun.data = some_function` is not valid in python, here
    `fun_data = somefunction` is used for now.

    If fun_data is not given by a string, e.g. `"mean_cl_boot"`, it has to be a
    function that takes a pandas series and returns a series containing the values
    for `y`, `ymin` and `ymax`.

    If `fun_y`, `fun_ymin` or `fun_ymax` are given, they have to be functions that
    take a pandas series and return a value.
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

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import pandas as pd

from ggplot.components import smoothers
from ggplot.utils import make_iterable_ntimes
from .stat import stat

def bootstrap(series, n_samples=1000, confidence_interval=0.95):
    """
    Default parameters taken from
    R's Hmisc smean.cl.boot
    """
    alpha = 1 - confidence_interval
    inds = np.random.randint(0, len(series), size=(n_samples, len(series)))
    samples = series.values[inds]
    means = np.sort(np.mean(samples, axis=1))
    return pd.Series({'ymin': means[int((alpha/2)*n_samples)],
                      'ymax': means[int((1-alpha/2)*n_samples)],
                      'y': series.mean()})


class stat_summary(stat):
    # TODO: maybe fun would better be a function reference instead of a string?
    # Would make providing own functions much easier, too.
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'pointrange', 'position': 'identity', 'fun': 'mean_cl_boot'}
    CREATES = {'ymin', 'ymax'}

    def _calculate(self, data):

        if self.params['fun'] != 'mean_cl_boot':
            raise NotImplementedError()

        new_data = data.groupby('x').apply(lambda df: bootstrap(df['y'])).reset_index()
        data.pop('x')
        data.pop('y')

        # Copy the other aesthetics into the new dataframe
        n = len(new_data.x)
        for ae in data:
            new_data[ae] = make_iterable_ntimes(data[ae].iloc[0], n)
        return new_data

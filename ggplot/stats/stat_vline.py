from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pandas as pd

from ggplot.utils import pop, make_iterable, make_iterable_ntimes
from .stat import stat


class stat_vline(stat):
    DEFAULT_PARAMS = {'geom': 'vline', 'position': 'identity',
                      'xintercept': 0}
    CREATES = {'xintercept'}

    def _calculate(self, data):
        x = pop(data, 'x', None)
        # xintercept may be one of:
        #   - aesthetic to geom_vline or
        #   - parameter setting to stat_vline
        xintercept = pop(data, 'xintercept', self.params['xintercept'])

        # TODO: Enable this when the parameters are passed correctly
        # and uncomment test case
        if hasattr(xintercept, '__call__'):
            if x is None:
                raise Exception(
                    'To compute the intercept, x aesthetic is needed')
            xintercept = xintercept(x)

        xintercept = make_iterable(xintercept)
        new_data = pd.DataFrame({'xintercept': xintercept})
        # Copy the other aesthetics into the new dataframe
        n = len(xintercept)
        for ae in data:
            new_data[ae] = make_iterable_ntimes(data[ae].iloc[0], n)
        return new_data

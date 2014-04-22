from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pandas as pd

from ggplot.utils import make_iterable, make_iterable_ntimes
from .stat import stat


class stat_hline(stat):
    DEFAULT_PARAMS = {'geom': 'hline', 'position': 'identity',
                      'yintercept': 0}
    CREATES = {'yintercept'}

    def _calculate(self, data):
        try:
            y = data.pop('y')
        except KeyError:
            pass

        # yintercept may be one of:
        #   - aesthetic to geom_hline or
        #   - parameter setting to stat_hline
        try:
            yintercept = data.pop('yintercept')
        except KeyError:
            yintercept = self.params['yintercept']

        # TODO: Enable this when the parameters are passed correctly
        # and uncomment test case
        if hasattr(yintercept, '__call__'):
            try:
                y = y
            except NameError:
                raise Exception(
                    'To compute the intercept, y aesthetic is needed')
            yintercept = yintercept(y)

        yintercept = make_iterable(yintercept)
        new_data = pd.DataFrame({'yintercept': yintercept})
        # Copy the other aesthetics into the new dataframe
        n = len(yintercept)
        for ae in data:
            new_data[ae] = make_iterable_ntimes(data[ae].iloc[0], n)
        return new_data

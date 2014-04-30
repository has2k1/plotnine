from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pandas as pd

from ggplot.utils import pop, make_iterable, make_iterable_ntimes
from ggplot.utils.exceptions import GgplotError
from .stat import stat


class stat_hline(stat):
    DEFAULT_PARAMS = {'geom': 'hline', 'position': 'identity',
                      'yintercept': 0}
    CREATES = {'yintercept'}

    def _calculate(self, data):
        y = pop(data, 'y', None)

        # yintercept may be one of:
        #   - aesthetic to geom_hline or
        #   - parameter setting to stat_hline
        yintercept = pop(data, 'yintercept', self.params['yintercept'])

        if hasattr(yintercept, '__call__'):
            if y is None:
                raise GgplotError(
                    'To compute the intercept, y aesthetic is needed')
            try:
                yintercept = yintercept(y)
            except TypeError as err:
                raise GgplotError(*err.args)

        yintercept = make_iterable(yintercept)
        new_data = pd.DataFrame({'yintercept': yintercept})
        # Copy the other aesthetics into the new dataframe
        n = len(yintercept)
        for ae in data:
            new_data[ae] = make_iterable_ntimes(data[ae].iloc[0], n)
        return new_data

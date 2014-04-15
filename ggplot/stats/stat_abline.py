from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pandas as pd

from ggplot.utils import make_iterable, make_iterable_ntimes
from .stat import stat


# Note when documenting
# slope and intercept can be functions that compute the slope
# and intercept using the data
class stat_abline(stat):
    DEFAULT_PARAMS = {'geom': 'abline', 'position': 'identity',
                      'slope': 1, 'intercept': 0}
    CREATES = {'slope', 'intercept'}

    def _calculate(self, data):
        # intercept and slope may be one of:
        #   - aesthetics to geom_abline or
        #   - parameter settings to stat_abline
        try:
            slope = data.pop('slope')
        except KeyError:
            slope = self.params['slope']

        try:
            intercept = data.pop('intercept')
        except KeyError:
            intercept = self.params['intercept']

        # TODO: Enable this when the parameters are passed correctly
        # and uncomment test case
        # if hasattr(slope, '__call__'):
        #     slope = slope(data['x'], data['y'])
        # if hasattr(intercept, '__call__'):
        #     intercept = intercept(data['y'])

        try:
            n = len(slope)
        except TypeError:
            n = 1

        try:
            _n = len(intercept)
        except TypeError:
            _n = 1

        if n != _n:
            # TODO: Test case
            raise Exception(
                'Specified {} slopes but {} intercepts'.format(n, _n))

        slope = make_iterable(slope)
        intercept = make_iterable(intercept)
        new_data = pd.DataFrame({'slope': slope, 'intercept': intercept})
        # Copy the other aesthetics into the new dataframe
        n = len(slope)
        for ae in data:
            new_data[ae] = make_iterable_ntimes(data[ae].iloc[0], n)
        return new_data

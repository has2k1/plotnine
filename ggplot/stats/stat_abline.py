from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pandas as pd

from ..utils import pop
from ..utils.exceptions import GgplotError
from .stat import stat


# Note when documenting
# slope and intercept can be functions that compute the slope
# and intercept using the data
class stat_abline(stat):
    DEFAULT_PARAMS = {'geom': 'abline', 'position': 'identity',
                      'slope': 1, 'intercept': 0}
    CREATES = {'slope', 'intercept'}

    def _calculate(self, data, scales, **kwargs):
        x = pop(data, 'x', None)
        y = pop(data, 'y', None)

        # intercept and slope may be one of:
        #   - aesthetics to geom_abline or
        #   - parameter settings to stat_abline
        slope = pop(data, 'slope', self.params['slope'])
        intercept = pop(data, 'intercept', self.params['intercept'])

        if hasattr(slope, '__call__'):
            if x is None or y is None:
                raise GgplotError(
                    'To compute the slope, x & y aesthetics are needed')
            try:
                slope = slope(x, y)
            except TypeError as err:
                raise GgplotError(*err.args)

        if hasattr(intercept, '__call__'):
            if x is None or y is None:
                raise GgplotError(
                    'To compute the intercept, x & y aesthetics are needed')
            try:
                intercept = intercept(x, y)
            except TypeError as err:
                raise GgplotError(*err.args)

        try:
            n = len(slope)
        except TypeError:
            n = 1

        try:
            _n = len(intercept)
        except TypeError:
            _n = 1

        if n != _n:
            raise GgplotError(
                'Specified {} slopes but {} intercepts'.format(n, _n))

        new_data = pd.DataFrame({'slope': slope, 'intercept': intercept})
        return new_data

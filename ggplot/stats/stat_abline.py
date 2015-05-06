from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import pop, make_iterable
from ..utils.exceptions import GgplotError
from .stat import stat

_MSG_MAPXY = """\
To compute the intercept or slope, map to the x & y aesthetics. \
Note: stat_abline does not inherit the aesthetics from the \
ggplot call. You can do so exclitily i.e stat_abline(inherit_aes=True)"""


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
                raise GgplotError(_MSG_MAPXY)
            try:
                slope = slope(x, y)
            except TypeError as err:
                raise GgplotError(*err.args)

        if hasattr(intercept, '__call__'):
            if x is None or y is None:
                raise GgplotError(_MSG_MAPXY)
            try:
                intercept = intercept(x, y)
            except TypeError as err:
                raise GgplotError(*err.args)

        slope = make_iterable(slope)
        intercept = make_iterable(intercept)

        n, _n = len(slope), len(intercept)
        if n != _n:
            raise GgplotError(
                'Specified {} slopes but {} intercepts'.format(n, _n))

        data = data.iloc[range(len(intercept)), :]
        data.is_copy = None
        data['intercept'] = intercept
        data['slope'] = slope
        return data

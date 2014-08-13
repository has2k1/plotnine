from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pandas as pd

from ..utils import pop
from ..utils.exceptions import GgplotError
from .stat import stat


class stat_vline(stat):
    DEFAULT_PARAMS = {'geom': 'vline', 'position': 'identity',
                      'xintercept': 0}
    CREATES = {'xintercept'}

    def _calculate(self, data, scales, **kwargs):
        x = pop(data, 'x', None)
        # xintercept may be one of:
        #   - aesthetic to geom_vline or
        #   - parameter setting to stat_vline
        xintercept = pop(data, 'xintercept', self.params['xintercept'])

        if hasattr(xintercept, '__call__'):
            if x is None:
                raise GgplotError(
                    'To compute the intercept, x aesthetic is needed')
            try:
                xintercept = xintercept(x)
            except TypeError as err:
                raise GgplotError(*err.args)

        new_data = pd.DataFrame({'xintercept': xintercept})
        new_data['x'] = new_data['xintercept']
        new_data['xend'] = new_data['xintercept']
        return new_data

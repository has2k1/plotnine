from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pandas as pd

from ..utils import pop
from ..utils.exceptions import GgplotError
from .stat import stat


class stat_hline(stat):
    DEFAULT_PARAMS = {'geom': 'hline', 'position': 'identity',
                      'yintercept': 0}
    CREATES = {'yintercept'}

    def _calculate(self, data, scales, **kwargs):
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

        new_data = pd.DataFrame({'yintercept': yintercept})
        new_data['y'] = new_data['yintercept']
        new_data['yend'] = new_data['yintercept']
        return new_data

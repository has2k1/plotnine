from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import pop, make_iterable
from ..utils.exceptions import GgplotError
from .stat import stat

_MSG_MAPY = """\
To compute the yintercept, map to the y aesthetic. \
Note: stat_hline does not inherit the aesthetics from the \
ggplot call. You can do so exclitily i.e stat_hline(inherit_aes=True)"""


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
                raise GgplotError(_MSG_MAPY)
            try:
                yintercept = yintercept(y)
            except TypeError as err:
                raise GgplotError(*err.args)

        yintercept = make_iterable(yintercept)
        data = data.iloc[range(len(yintercept)), :]
        data.is_copy = None
        data['yintercept'] = yintercept
        data['y'] = data['yintercept']
        data['yend'] = data['yintercept']
        return data

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import pop, make_iterable
from ..utils.exceptions import GgplotError
from .stat import stat

_MSG_MAPX = """\
To compute the xintercept, map to the y aesthetic. \
Note: stat_vline does not inherit the aesthetics from the \
ggplot call. You can do so exclitily i.e stat_vline(inherit_aes=True)"""


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
                raise GgplotError(_MSG_MAPX)
            try:
                xintercept = xintercept(x)
            except TypeError as err:
                raise GgplotError(*err.args)

        xintercept = make_iterable(xintercept)
        data = data.iloc[range(len(xintercept)), :]
        data.is_copy = None
        data['xintercept'] = xintercept
        data['x'] = data['xintercept']
        data['xend'] = data['xintercept']
        return data

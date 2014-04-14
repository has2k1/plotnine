from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .stat import stat


class stat_vline(stat):
    DEFAULT_PARAMS = {'geom': 'vline', 'position': 'identity',
                      'xintercept': 0}
    CREATES = {'xintercept'}

    def _calculate(self, pinfo):
        # xintercept may be one of:
        #   - aesthetic to geom_hline or
        #   - parameter setting to stat_hline
        xintercept = pinfo.pop('xintercept', self.params['xintercept'])

        # TODO: Enable this when the parameters are passed correctly
        # and uncomment test case
        # if hasattr(xintercept, '__call__'):
        #     if 'x'not in pinfo:
        #         raise Exception(
        #             'To compute the intercept, x aesthetic is needed')
        #     xintercept = xintercept(pinfo['x'])

        pinfo['xintercept'] = xintercept
        return pinfo

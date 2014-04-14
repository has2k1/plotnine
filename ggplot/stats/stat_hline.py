from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .stat import stat


class stat_hline(stat):
    DEFAULT_PARAMS = {'geom': 'hline', 'position': 'identity',
                      'yintercept': 0}
    CREATES = {'yintercept'}

    def _calculate(self, pinfo):
        # yintercept may be one of:
        #   - aesthetic to geom_hline or
        #   - parameter setting to stat_hline
        yintercept = pinfo.pop('yintercept', self.params['yintercept'])

        # TODO: Enable this when the parameters are passed correctly
        # and uncomment test case
        # if hasattr(xintercept, '__call__'):
        #     if 'y' not in pinfo:
        #         raise Exception(
        #             'To compute the intercept, y aesthetic is needed')
        #     yintercept = yintercept(pinfo['y'])

        pinfo['yintercept'] = yintercept
        return pinfo

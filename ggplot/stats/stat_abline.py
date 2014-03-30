from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .stat import stat


class stat_abline(stat):
    DEFAULT_PARAMS = {'geom': 'abline', 'position': 'identity',
                      'slope': 1, 'intercept': 0}

    def _calculate(self, pinfo):
        # intercept and slope can be classified as
        # params or as aesthetics
        slope = pinfo.pop('slope', self.params['slope'])
        intercept = pinfo.pop('intercept', self.params['intercept'])

        try:
            n = len(slope)
        except TypeError:
            n = 1

        try:
            _n = len(intercept)
        except TypeError:
            _n = 1

        if n != _n:
            raise('Specified %d slopes but %d intercepts' % (n, _n))

        if n == 1:
            slope = [slope]
            intercept = [intercept]

        pinfo['slope'] = slope
        pinfo['intercept'] = intercept

        return pinfo

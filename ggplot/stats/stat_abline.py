from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .stat import stat


# Note when documenting
# slope and intercept can be functions that compute the slope
# and intercept using the data
class stat_abline(stat):
    DEFAULT_PARAMS = {'geom': 'abline', 'position': 'identity',
                      'slope': 1, 'intercept': 0}
    CREATES = {'slope', 'intercept'}

    def _calculate(self, pinfo):
        # intercept and slope may be one of:
        #   - aesthetics to geom_abline or
        #   - parameter settings to stat_abline
        slope = pinfo.pop('slope', self.params['slope'])
        intercept = pinfo.pop('intercept', self.params['intercept'])

        # TODO: Enable this when the parameters are passed correctly
        # and uncomment test case
        # if hasattr(slope, '__call__'):
        #     slope = slope(pinfo['x'], pinfo['y'])
        # if hasattr(intercept, '__call__'):
        #     intercept = intercept(pinfo['y'])

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

        if n == 1:
            slope = [slope]
            intercept = [intercept]

        pinfo['slope'] = slope
        pinfo['intercept'] = intercept

        return pinfo

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .stat import stat


class stat_vline(stat):
    DEFAULT_PARAMS = {'geom': 'vline', 'position': 'identity',
                      'xintercept': 0, 'ymin': None, 'ymax': None}

    def _calculate(self, pinfo):
        # There is no calculation to do.
        # But these are both aesthetics and parameters
        names = ['xintercept', 'ymin', 'ymax']
        for name in names:
            if name not in pinfo:
                pinfo[name] = self.params[name]

        # NOTE: In preparation for stats to accept
        # a dataframe we remove all scalar and
        # none numeric data
        try:
            if pinfo['ymin'] is None:
                pinfo.pop('ymin')
        except KeyError:
            pass
        try:
            if pinfo['ymax'] is None:
                pinfo.pop('ymax')
        except KeyError:
            pass
        return pinfo

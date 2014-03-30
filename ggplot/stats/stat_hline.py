from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .stat import stat


class stat_hline(stat):
    DEFAULT_PARAMS = {'geom': 'hline', 'position': 'identity',
                      'yintercept': 0, 'xmin': None, 'xmax': None}

    def _calculate(self, pinfo):
        # There is no calculation to do.
        # But these are both aesthetics and parameters
        names = ['yintercept', 'xmin', 'xmax']
        for name in names:
            if name not in pinfo:
                pinfo[name] = self.params[name]

        # NOTE: In preparation for stats to accept
        # a dataframe we remove all scalar and
        # none numeric data
        try:
            if pinfo['xmin'] is None:
                pinfo.pop('xmin')
        except KeyError:
            pass
        try:
            if pinfo['xmax'] is None:
                pinfo.pop('xmax')
        except KeyError:
            pass
        return pinfo

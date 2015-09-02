from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .stat import stat


class stat_unique(stat):
    DEFAULT_PARAMS = {'geom': 'point', 'position': 'identity'}

    @classmethod
    def compute_panel(cls, data, scales, **params):
        return data.drop_duplicates()

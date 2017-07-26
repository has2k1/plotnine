from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..doctools import document
from .stat import stat


@document
class stat_unique(stat):
    """
    Remove duplicates

    {usage}

    Parameters
    ----------
    {common_parameters}

    {aesthetics}
    """
    DEFAULT_PARAMS = {'geom': 'point', 'position': 'identity',
                      'na_rm': False}

    @classmethod
    def compute_panel(cls, data, scales, **params):
        return data.drop_duplicates()

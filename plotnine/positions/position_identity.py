from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .position import position


class position_identity(position):
    """
    Do not adjust the position
    """

    @classmethod
    def compute_layer(cls, data, params, layout):
        return data

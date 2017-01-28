from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .position_stack import position_stack


class position_fill(position_stack):
    """
    Normalise stacked objects to unit height
    """
    fill = True

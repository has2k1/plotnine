from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd

from .position import position
from .collide import collide, pos_fill
from ..utils import check_required_aesthetics
from ..utils.exceptions import gg_warning


class position_fill(position):

    def adjust(self, data):
        if len(data) == 0:
            return pd.DataFrame()

        check_required_aesthetics(
            ['x', 'ymax'], data.columns, "position_fill")

        if not all(data['ymin'] == 0):
            gg_warning('Filling not well defined when ymin != 0')

        width = data['width'] if 'width' in data else None
        return collide(data, width=width,
                       name='position_fill',
                       strategy=pos_fill)

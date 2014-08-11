from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd

from .position import position
from .collide import collide, pos_stack
from ..utils import remove_missing
from ..utils.exceptions import gg_warning


class position_stack(position):

    def adjust(self, data):
        if len(data) == 0:
            return pd.DataFrame()

        data = remove_missing(
            data,
            vars=('x', 'y', 'ymin', 'ymax', 'xmin', 'xmax'),
            name='position_stack')

        if not ('ymax' in data) and not ('y' in data):
            gg_warning(
                """\
                Missing y and ymax in position = 'stack'. \
                Maybe you want position = 'identity'?""")
            return data

        if 'ymin' in data and not all(data['ymin'] == 0):
            gg_warning('Stacking not well defined when ymin != 0')

        width = data['width'] if 'width' in data else None

        return collide(data, width=width,
                       name='position_stack',
                       strategy=pos_stack)

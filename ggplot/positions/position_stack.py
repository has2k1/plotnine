from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .position import position
from .collide import collide, pos_stack
from ..utils import remove_missing
from ..utils.exceptions import gg_warn


class position_stack(position):
    def setup_data(self, data, params):
        if ('ymax' not in data) and ('y' not in data):
            gg_warn(
                """\
                Missing y and ymax in position = 'stack'. \
                Maybe you want position = 'identity'?""")
            return data

        data = remove_missing(
            data,
            vars=('x', 'y', 'ymin', 'ymax', 'xmin', 'xmax'),
            name='position_stack')

        if 'ymin' in data and not all(data['ymin'] == 0):
            gg_warn('Stacking not well defined when ymin != 0')

        return data

    @classmethod
    def compute_panel(cls, data, scales, params):
        return collide(data, width=None,
                       name='position_stack',
                       strategy=pos_stack)

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .position import position
from .collide import collide, pos_fill
from ..utils import suppress
from ..utils.exceptions import gg_warn


class position_fill(position):
    REQUIRED_AES = {'x', 'ymax'}

    def setup_data(self, data, params):
        with suppress(KeyError):
            if not all(data['ymin'] == 0):
                gg_warn("Filling not well defined when ymin != 0")
        return position.setup_data(self, data, params)

    @classmethod
    def compute_panel(cls, data, scales, params):
        return collide(data, width=None,
                       name='position_fill',
                       strategy=pos_fill)

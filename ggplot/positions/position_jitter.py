from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import jitter
from ..scales.utils import resolution
from .position import _position_base


class position_jitter(_position_base):

    def adjust(self, data):
        if not self.width:
            self.width = resolution(data['x']) * .4
        if not self.height:
            self.height = resolution(data['y']) * .4

        trans_x = None
        trans_y = None

        if self.width:
            def trans_x(x):
                return jitter(x, self.width)

        if self.height:
            def trans_y(y):
                return jitter(y, self.height)

        return self._transform_position(data, trans_x, trans_y)

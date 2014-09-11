from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from .geom_path import geom_path


class geom_line(geom_path):

    @staticmethod
    def draw(pinfo, scales, ax, **kwargs):
        x = pinfo.pop('x')
        y = pinfo.pop('y')

        idx = np.argsort(x)
        pinfo['x'] = [x[i] for i in idx]
        pinfo['y'] = [y[i] for i in idx]

        geom_path.draw(pinfo, scales, ax, **kwargs)

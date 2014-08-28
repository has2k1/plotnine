from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom_path import geom_path


# TODO: Add test case
class geom_step(geom_path):

    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'direction': 'hv'}

    def draw(self, pinfo, scales, ax, **kwargs):
        x = pinfo.pop('x')
        y = pinfo.pop('y')

        xs = [None] * (2 * (len(x)-1))
        ys = [None] * (2 * (len(x)-1))

        # create stepped path -- interweave x with
        # itself and y with itself
        if self.params['direction'] == 'hv':
            xs[::2], xs[1::2] = x[:-1], x[1:]
            ys[::2], ys[1::2] = y[:-1], y[:-1]
        elif self.params['direction'] == 'vh':
            xs[::2], xs[1::2] = x[:-1], x[:-1]
            ys[::2], ys[1::2] = y[:-1], y[1:]

        pinfo['x'] = xs
        pinfo['y'] = ys
        geom_path.draw(self, pinfo, scales, ax, **kwargs)

from __future__ import absolute_import, division, print_function

from matplotlib.cbook import Bunch

from ..scales.utils import expand_range, gettrans, squish_infinite
from ..positions.position import transform_position
from .coord import coord, dist_euclidean


class coord_trans(coord):

    def __init__(self, x='identity', y='identity',
                 xlim=None, ylim=None):
        self.trans = Bunch(x=gettrans(x), y=gettrans(y))
        self.limits = Bunch(xlim=xlim, ylim=ylim)

    def transform(self, data, panel_scales, munch=False):
        if not self.is_linear and munch:
            data = self.munch(data, panel_scales)

        def trans_x(data):
            return transform_value(self.trans.x,
                                   data, panel_scales['x_range'])

        def trans_y(data):
            return transform_value(self.trans.y,
                                   data, panel_scales['y_range'])

        data = transform_position(data, trans_x, trans_y)
        return transform_position(data, squish_infinite, squish_infinite)

    def train(self, scale):
        name = scale.aesthetics[0]
        if name == 'x':
            limits = self.limits.xlim
            trans = self.trans.x
        else:
            limits = self.limits.ylim
            trans = self.trans.y

        if limits is None:
            rangee = scale.dimension()
        else:
            rangee = scale.transform(limits)

        # data space
        out = scale.break_info(rangee)

        # trans'd range
        out['range'] = trans.transform(out['range'])

        if limits is None:
            expand = self.expand_default(scale)
            out['range'] = expand_range(out['range'], expand[0], expand[1])

        # major and minor breaks in plot space
        out['major'] = transform_value(trans, out['major'], out['range'])
        out['minor'] = transform_value(trans, out['minor'], out['range'])

        for key in list(out.keys()):
            new_key = '{}_{}'.format(name, key)
            out[new_key] = out.pop(key)

        return out

    def distance(self, x, y, panel_scales):
        max_dist = dist_euclidean(panel_scales['x_range'],
                                  panel_scales['y_range'])[0]
        return dist_euclidean(self.trans.x.transform(x),
                              self.trans.y.transform(y)) / max_dist


def transform_value(trans, value, range):
    return trans.transform(value)

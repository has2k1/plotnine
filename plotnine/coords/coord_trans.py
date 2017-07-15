from __future__ import absolute_import, division, print_function

from warnings import warn

from matplotlib.cbook import Bunch
from mizani.bounds import expand_range_distinct, squish_infinite
from mizani.transforms import gettrans

from ..positions.position import transform_position
from .coord import coord, dist_euclidean


class coord_trans(coord):
    """
    Transformed cartesian coordinate system

    Parameters
    ----------
    x : str | trans
        Name of transform or `trans` class to
        transform the x axis
    y : str | trans
        Name of transform or `trans` class to
        transform the y axis
    xlim : None | (float, float)
        Limits for x axis. If None, then they are
        automatically computed.
    ylim : None | (float, float)
        Limits for y axis. If None, then they are
        automatically computed.
    """

    def __init__(self, x='identity', y='identity',
                 xlim=None, ylim=None):
        self.trans = Bunch(x=gettrans(x), y=gettrans(y))
        self.limits = Bunch(xlim=xlim, ylim=ylim)

    def transform(self, data, panel_params, munch=False):
        if not self.is_linear and munch:
            data = self.munch(data, panel_params)

        def trans_x(data):
            result = transform_value(self.trans.x,
                                     data, panel_params['x_range'])
            if any(result.isnull()):
                warn("Coordinate transform of x aesthetic "
                     "created one or more NaN values.")
            return result

        def trans_y(data):
            result = transform_value(self.trans.y,
                                     data, panel_params['y_range'])
            if any(result.isnull()):
                warn("Coordinate transform of y aesthetic "
                     "created one or more NaN values.")
            return result

        data = transform_position(data, trans_x, trans_y)
        return transform_position(data, squish_infinite, squish_infinite)

    def setup_panel_params(self, scale_x, scale_y):
        """
        Compute the range and break information for the panel

        """
        def train(scale, limits, trans, name):
            """
            Train a single coordinate axis
            """
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
                out['range'] = expand_range_distinct(out['range'], expand)

            # major and minor breaks in plot space
            out['major'] = transform_value(trans, out['major'], out['range'])
            out['minor'] = transform_value(trans, out['minor'], out['range'])

            for key in list(out.keys()):
                new_key = '{}_{}'.format(name, key)
                out[new_key] = out.pop(key)

            return out

        # When Python 2.7 end of life, change this to dict(**a, **b)
        out = train(scale_x, self.limits.xlim, self.trans.x, 'x')
        out.update(train(scale_y, self.limits.xlim, self.trans.y, 'y'))
        return out

    def distance(self, x, y, panel_params):
        max_dist = dist_euclidean(panel_params['x_range'],
                                  panel_params['y_range'])[0]
        return dist_euclidean(self.trans.x.transform(x),
                              self.trans.y.transform(y)) / max_dist


def transform_value(trans, value, range):
    return trans.transform(value)

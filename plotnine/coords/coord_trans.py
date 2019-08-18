from types import SimpleNamespace as NS
from warnings import warn

import numpy as np
from mizani.bounds import squish_infinite
from mizani.transforms import gettrans

from ..exceptions import PlotnineWarning
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
    expand : bool
        If `True`, expand the coordinate axes by
        some factor. If `False`, use the limits
        from the data.
    """

    def __init__(self, x='identity', y='identity',
                 xlim=None, ylim=None, expand=True):
        self.trans = NS(x=gettrans(x), y=gettrans(y))
        self.limits = NS(x=xlim, y=ylim)
        self.expand = expand

    def transform(self, data, panel_params, munch=False):
        if not self.is_linear and munch:
            data = self.munch(data, panel_params)

        def trans_x(data):
            result = transform_value(self.trans.x,
                                     data, panel_params.x.range)
            if any(result.isnull()):
                warn("Coordinate transform of x aesthetic "
                     "created one or more NaN values.", PlotnineWarning)
            return result

        def trans_y(data):
            result = transform_value(self.trans.y,
                                     data, panel_params.y.range)
            if any(result.isnull()):
                warn("Coordinate transform of y aesthetic "
                     "created one or more NaN values.", PlotnineWarning)
            return result

        data = transform_position(data, trans_x, trans_y)
        return transform_position(data, squish_infinite, squish_infinite)

    def backtransform_range(self, panel_params):
        x = self.trans.x.inverse(panel_params.x.range)
        y = self.trans.y.inverse(panel_params.y.range)
        return NS(x=x, y=y)

    def setup_panel_params(self, scale_x, scale_y):
        """
        Compute the range and break information for the panel

        """
        def get_view_limits(scale, coord_limits, trans):
            if coord_limits:
                coord_limits = trans.transform(coord_limits)

            expansion = scale.default_expansion(expand=self.expand)
            ranges = scale.expand_limits(
                scale.limits, expansion, coord_limits, trans)
            vs = scale.view(limits=coord_limits, range=ranges.range)
            vs.range = np.sort(ranges.range_coord)
            vs.breaks = transform_value(trans, vs.breaks, vs.range)
            vs.minor_breaks = transform_value(trans, vs.minor_breaks, vs.range)
            return vs

        out = NS(x=get_view_limits(scale_x, self.limits.x, self.trans.x),
                 y=get_view_limits(scale_y, self.limits.y, self.trans.y))
        return out

    def distance(self, x, y, panel_params):
        max_dist = dist_euclidean(panel_params.x.range,
                                  panel_params.y.range)[0]
        return dist_euclidean(self.trans.x.transform(x),
                              self.trans.y.transform(y)) / max_dist


def transform_value(trans, value, range):
    return trans.transform(value)

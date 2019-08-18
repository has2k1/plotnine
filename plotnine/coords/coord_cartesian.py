from types import SimpleNamespace as NS
from mizani.bounds import squish_infinite
from mizani.transforms import identity_trans

from .coord import coord, dist_euclidean
from ..positions.position import transform_position


class coord_cartesian(coord):
    """
    Cartesian coordinate system

    Parameters
    ----------
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

    is_linear = True

    def __init__(self, xlim=None, ylim=None, expand=True):
        self.limits = NS(x=xlim, y=ylim)
        self.expand = expand

    def transform(self, data, panel_params, munch=False):
        def squish_infinite_x(data):
            return squish_infinite(data, range=panel_params.x.range)

        def squish_infinite_y(data):
            return squish_infinite(data, range=panel_params.y.range)

        return transform_position(data, squish_infinite_x, squish_infinite_y)

    def setup_panel_params(self, scale_x, scale_y):
        """
        Compute the range and break information for the panel
        """
        def get_view_limits(scale, coord_limits):
            expansion = scale.default_expansion(expand=self.expand)
            ranges = scale.expand_limits(
                scale.limits, expansion, coord_limits, identity_trans)
            vs = scale.view(limits=coord_limits, range=ranges.range)
            return vs

        out = NS(x=get_view_limits(scale_x, self.limits.x),
                 y=get_view_limits(scale_y, self.limits.y))
        return out

    @staticmethod
    def distance(x, y, panel_params):
        max_dist = dist_euclidean(panel_params.x.range,
                                  panel_params.y.range)[0]
        return dist_euclidean(x, y) / max_dist

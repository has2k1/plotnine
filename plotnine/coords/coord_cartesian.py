from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.cbook import Bunch
from mizani.bounds import expand_range_distinct

from .coord import coord, dist_euclidean


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
        self.limits = Bunch(xlim=xlim, ylim=ylim)
        self.expand = expand

    def setup_panel_params(self, scale_x, scale_y):
        """
        Compute the range and break information for the panel
        """

        def train(scale, limits, name):
            """
            Train a single coordinate axis
            """
            # Which axis are we dealing with
            name = scale.aesthetics[0]

            if self.expand:
                expand = self.expand_default(scale)
            else:
                expand = (0, 0, 0, 0)

            if limits is None:
                rangee = scale.dimension(expand)
            else:
                rangee = scale.transform(limits)
                rangee = expand_range_distinct(rangee, expand)

            out = scale.break_info(rangee)
            # This is where
            # x_major, x_labels, x_minor, ...
            # range keys are created
            for key in list(out.keys()):
                new_key = '{}_{}'.format(name, key)
                out[new_key] = out.pop(key)
            return out

        # When Python 2.7 end of life, change this to dict(**a, **b)
        out = train(scale_x, self.limits.xlim, 'x')
        out.update(train(scale_y, self.limits.ylim, 'y'))
        return out

    @staticmethod
    def distance(x, y, panel_params):
        max_dist = dist_euclidean(panel_params['x_range'],
                                  panel_params['y_range'])[0]
        return dist_euclidean(x, y) / max_dist

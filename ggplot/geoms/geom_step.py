from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from itertools import groupby
from operator import itemgetter
from .geom import geom


class geom_step(geom):

    VALID_AES = {'x', 'y', 'color', 'alpha', 'linetype', 'size',
                 'group'}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
            'direction': 'hv', 'group': None, 'label': ''}

    _groups = {'color', 'alpha', 'linetype', 'size'}
    _aes_renames = {'size': 'markersize', 'linetype': 'linestyle'}

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop('x')
        y = pinfo.pop('y')
        pinfo['label'] = self.params['label']
        if 'linetype' in pinfo and 'color' not in pinfo:
            pinfo['color'] = 'k'

        x_stepped = []
        y_stepped = []
        for i in range(len(x) - 1):
            x_stepped.append(x[i])
            x_stepped.append(x[i+1])
            y_stepped.append(y[i])
            y_stepped.append(y[i])

        # TODO: Fix this when the group aes/parameter is handled
        # across all geoms
        if 'group' not in pinfo:
            ax.plot(x_stepped, y_stepped, **pinfo)
        else:
            g = pinfo.pop('group')
            for k, v in groupby(sorted(zip(x_stepped, y_stepped, g),
                                       key=itemgetter(2)), key=itemgetter(2)):
                x_g, y_g, _ = zip(*v)
                ax.plot(x_g, y_g, **pinfo)

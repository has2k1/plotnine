from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom

# TODO: Needs testing
class geom_step(geom):

    DEFAULT_AES = {'color': 'black', 'alpha': None, 'linetype': 'solid',
                   'size': 1.0}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
            'direction': 'hv', 'label': ''}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}
    _groups = {'alpha', 'color', 'linestyle', 'linewidth'}

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop('x')
        y = pinfo.pop('y')
        pinfo['label'] = self.params['label']

        x_stepped = []
        y_stepped = []
        # TODO: look into this?
        # seems off and there are no test cases
        for i in range(len(x) - 1):
            x_stepped.append(x[i])
            x_stepped.append(x[i+1])
            y_stepped.append(y[i])
            y_stepped.append(y[i])

        ax.plot(x_stepped, y_stepped, **pinfo)

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom

class geom_hline(geom):
    DEFAULT_AES = {'xmin': 0, 'xmax': 1, 'color': 'black', 'linetype': 'solid',
                   'size': 1.0, 'alpha': None}
    REQUIRED_AES = {'y'}
    DEFAULT_PARAMS = {'stat': 'hline', 'position': 'identity',
                      'show_guide': False, 'label': ''}

    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth'}
    _groups = {'alpha', 'color', 'linestyle', 'linewidth'}

    def _plot_unit(self, pinfo, ax):
        pinfo['label'] = self.params['label']
        pinfo['label'] = self.params['label']
        if isinstance(pinfo['y'], list):
            ys = pinfo['y']
            for y in ys:
                pinfo['y'] = y
                ax.axhline(**pinfo)
        else:
            ax.axhline(**pinfo)


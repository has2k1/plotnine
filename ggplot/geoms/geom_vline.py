from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom

class geom_vline(geom):
    DEFAULT_AES = {'ymin': 0, 'ymax': 1, 'color': 'black', 'linetype': 'solid',
                 'size': 1.0, 'alpha': None}
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'stat': 'vline', 'position': 'identity', 'show_guide': False,
            'label': ''}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}
    _groups = {'alpha', 'color', 'linestyle'}

    def _plot_unit(self, pinfo, ax):
        pinfo['label'] = self.params['label']
        if isinstance(pinfo['x'], list):
            xs = pinfo['x']
            for x in xs:
                pinfo['x'] = x
                ax.axvline(**pinfo)
        else:
            ax.axvline(**pinfo)

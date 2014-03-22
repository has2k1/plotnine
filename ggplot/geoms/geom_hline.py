from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom

class geom_hline(geom):
    VALID_AES = {'y', 'xmin', 'xmax', 'color', 'linetype', 'size', 'alpha'}
    REQUIRED_AES = {'y'}
    DEFAULT_PARAMS = {'stat': 'hline', 'position': 'identity', 'show_guide': False,
            'label': ''}

    _groups = {'color', 'alpha', 'linetype'}
    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}

    def _plot_unit(self, pinfo, ax):
        pinfo['label'] = self.params['label']
        ax.axhline(**pinfo)



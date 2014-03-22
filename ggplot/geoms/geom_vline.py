from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom

class geom_vline(geom):
    VALID_AES = {'x', 'ymin', 'ymax', 'color', 'linetype', 'size', 'alpha'}
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'stat': 'vline', 'position': 'identity', 'show_guide': False,
            'label': ''}

    _groups = {'color', 'alpha', 'linetype'}
    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}

    def _plot_unit(self, pinfo, ax):
        pinfo['label'] = self.params['label']
        ax.axvline(**pinfo)

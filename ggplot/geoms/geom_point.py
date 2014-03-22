from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib as mpl
from .geom import geom
import numpy as np

class geom_point(geom):
    VALID_AES = {'x', 'y', 'alpha', 'color', 'fill', 'shape', 'size'}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity', 'cmap':None, 'label': ''}

    _groups = {'color', 'shape', 'alpha'}
    _aes_renames = {'size': 's', 'shape': 'marker'}

    def _plot_unit(self, pinfo, ax):
        pinfo['label'] = self.params['label']
        # for some reason, scatter doesn't default to the same color styles
        # as the axes.color_cycle
        if "color" not in pinfo and self.params['cmap'] is None:
            pinfo["color"] = mpl.rcParams.get("axes.color_cycle", ["#333333"])[0]

        if self.params['position'] == 'jitter':
            pinfo['x'] *= np.random.uniform(.9, 1.1, len(pinfo['x']))
            pinfo['y'] *= np.random.uniform(.9, 1.1, len(pinfo['y']))

        ax.scatter(**pinfo)


from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd

from ..scales.utils import resolution
from ..utils import copy_missing_columns
from .geom import geom
from .geom_segment import geom_segment


class geom_errorbarh(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black',
                   'linetype': 'solid', 'size': 1.5}
    REQUIRED_AES = {'y', 'xmin', 'xmax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'height': 0.5}
    legend_geom = 'path'

    def setup_data(self, data):
        if 'height' not in data:
            if self.params['height']:
                data['height'] = self.params['height']
            else:
                data['height'] = resolution(data['y'], False) * 0.9

        data['ymin'] = data['y'] - data['height']/2
        data['ymax'] = data['y'] + data['height']/2
        del data['height']
        return data

    @staticmethod
    def draw_group(data, panel_scales, coord, ax, **params):
        f = np.hstack
        # create (two vertical bars) + horizontal bar
        df = pd.DataFrame({
            'y': f([data['ymin'], data['ymin'], data['y']]),
            'yend': f([data['ymax'], data['ymax'], data['y']]),
            'x': f([data['xmin'], data['xmax'], data['xmin']]),
            'xend': f([data['xmin'], data['xmax'], data['xmax']])})

        copy_missing_columns(df, data)
        geom_segment.draw_group(df, panel_scales, coord, ax, **params)

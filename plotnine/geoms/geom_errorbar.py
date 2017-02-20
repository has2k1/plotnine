from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd

from ..utils import copy_missing_columns, resolution
from ..utils.doctools import document
from .geom import geom
from .geom_segment import geom_segment


@document
class geom_errorbar(geom):
    """
    Vertical interval represented as an errorbar

    {usage}

    Parameters
    ----------
    {common_parameters}

    {aesthetics}
    """
    DEFAULT_AES = {'alpha': 1, 'color': 'black',
                   'linetype': 'solid', 'size': 0.5}
    REQUIRED_AES = {'x', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'width': 0.5, 'na_rm': False}
    legend_geom = 'path'

    def setup_data(self, data):
        if 'width' not in data:
            if self.params['width']:
                data['width'] = self.params['width']
            else:
                data['width'] = resolution(data['x'], False) * 0.9

        data['xmin'] = data['x'] - data['width']/2
        data['xmax'] = data['x'] + data['width']/2
        del data['width']
        return data

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        f = np.hstack
        # create (two horizontal bars) + vertical bar
        df = pd.DataFrame({
            'x': f([data['xmin'], data['xmin'], data['x']]),
            'xend': f([data['xmax'], data['xmax'], data['x']]),
            'y': f([data['ymin'], data['ymax'], data['ymax']]),
            'yend': f([data['ymin'], data['ymax'], data['ymin']])})

        copy_missing_columns(df, data)
        geom_segment.draw_group(df, panel_params, coord, ax, **params)

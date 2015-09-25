from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
import pandas.core.common as com
from matplotlib.cbook import boxplot_stats

from ..scales.utils import resolution
from .stat import stat


class stat_boxplot(stat):
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'boxplot', 'position': 'dodge',
                      'coef': 1.5}

    def setup_params(self, data):
        if 'width' not in self.params:
            self.params['width'] = resolution(data['x'], False) * 0.75
        return self.params

    @classmethod
    def compute_group(cls, data, scales, **params):
        labels = ['x', 'y']
        X = np.array(data[labels])
        res = boxplot_stats(X, whis=params['coef'], labels=labels)[1]
        try:
            n = data['weight'].sum()
        except KeyError:
            n = len(data['y'])

        if len(np.unique(data['x'])) > 1:
            width = np.ptp(data['x']) * 0.9
        else:
            width = params['width']

        if com.is_categorical(data['x']):
            x = data['x'].iloc[0]
        else:
            x = np.mean([data['x'].min(), data['x'].max()])

        d = {'ymin': res['whislo'],
             'lower': res['q1'],
             'middle': [res['med']],
             'upper': res['q3'],
             'ymax': res['whishi'],
             'outliers': [res['fliers']],
             'notchupper': res['med']+1.58*res['iqr']/np.sqrt(n),
             'notchlower': res['med']-1.58*res['iqr']/np.sqrt(n),
             'x': x,
             'width': width,
             'relvarwidth': np.sqrt(n)}
        return pd.DataFrame(d)

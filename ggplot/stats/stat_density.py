from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import pandas as pd
import pandas.core.common as com
import statsmodels.api as sm

from ..utils.exceptions import GgplotError
from .stat import stat


# NOTE: Parameter discriptions are in
# statsmodels/nonparametric/kde.py
# TODO: Update when statsmodels-0.6 is released
class stat_density(stat):
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'density', 'position': 'stack',
                      'kernel': 'gaussian', 'adjust': 1,
                      'trim': False, 'n': 512, 'gridsize': None,
                      'bw': 'normal_reference', 'cut': 3,
                      'clip': (-np.inf, np.inf)}
    CREATES = {'y'}

    def _calculate(self, data, scales, **kwargs):
        x = data.pop('x')

        _sc = scales.x if scales.x else scales.y
        range_x = _sc.dimension((0, 0))

        try:
            float(x.iloc[0])
        except:
            try:
                # try to use it as a pandas.tslib.Timestamp
                x = [ts.toordinal() for ts in x]
            except:
                raise GgplotError(
                    "stat_density(): aesthetic x mapping " +
                    "needs to be convertable to float!")

        # kde is computed efficiently using fft. But the fft does
        # not support weights and is only available with the
        # gaussian kernel. When weights are relevant we
        # turn off the fft.
        try:
            weight = data.pop('weight')
        except KeyError:
            weight = np.ones(len(x))

        lookup = {
            'biweight': 'biw',
            'cosine': 'cos',
            'epanechnikov': 'epa',
            'gaussian': 'gau',
            'triangular': 'tri',
            'triweight': 'triw',
            'uniform': 'uni'}
        kernel = lookup[self.params['kernel'].lower()]

        if kernel == 'gaussian':
            fft, weight = True, None
        else:
            fft = False

        kde = sm.nonparametric.KDEUnivariate(x)
        kde.fit(
            # kernel=kernel,        # enable after statsmodels 0.6
            # bw=self.params['bw'], # enable after statsmodels 0.6
            fft=fft,
            weights=weight,
            adjust=self.params['adjust'],
            cut=self.params['cut'],
            gridsize=self.params['gridsize'],
            clip=self.params['clip'],)
        x2 = np.linspace(range_x[0], range_x[1], self.params['n'])
        y = kde.evaluate(x2)
        new_data = pd.DataFrame({'x': x2, 'y': y})
        return new_data

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import pandas as pd
import statsmodels.api as sm

from ..utils.exceptions import GgplotError
from ..utils import suppress
from .stat import stat


# NOTE: Parameter discriptions are in
# statsmodels/nonparametric/kde.py
class stat_density(stat):
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'density', 'position': 'stack',
                      'kernel': 'gaussian', 'adjust': 1,
                      'trim': False, 'n': 1024, 'gridsize': None,
                      'bw': 'normal_reference', 'cut': 3,
                      'clip': (-np.inf, np.inf)}
    DEFAULT_AES = {'y': '..density..'}
    CREATES = {'y'}

    def setup_params(self, data):
        params = self.params.copy()
        lookup = {
            'biweight': 'biw',
            'cosine': 'cos',
            'cosine2': 'cos2',
            'epanechnikov': 'epa',
            'gaussian': 'gau',
            'triangular': 'tri',
            'triweight': 'triw',
            'uniform': 'uni'}

        with suppress(KeyError):
            params['kernel'] = lookup[params['kernel'].lower()]

        if params['kernel'] not in lookup.viewvalues():
            msg = ("kernel should be one of {}. "
                   "You may use the abbreviations {}")
            raise GgplotError(msg.format(lookup.viewkeys(),
                                         lookup.viewvalues))

        return params

    @classmethod
    def compute_group(cls, data, scales, **params):
        weight = data.get('weight')

        if params['trim']:
            range_x = data['x'].min(), data['x'].max()
        else:
            range_x = scales.x.dimension()

        return compute_density(data['x'], weight, range_x, **params)


def compute_density(x, weight, range, **params):
    n = len(x)

    if weight is None:
        weight = np.ones(n) / n

    # if less than 3 points, spread density evenly
    # over points
    if n < 3:
        return pd.DataFrame({
            'x': x,
            'density': weight / np.sum(weight),
            'scaled': weight / np.max(weight),
            'count': 1,
            'n': n})

    # kde is computed efficiently using fft. But the fft does
    # not support weights and is only available with the
    # gaussian kernel. When weights are relevant we
    # turn off the fft.
    if params['kernel'] == 'gau':
        fft, weight = True, None
    else:
        fft = False

    kde = sm.nonparametric.KDEUnivariate(x)
    kde.fit(
        kernel=params['kernel'],
        bw=params['bw'],
        fft=fft,
        weights=weight,
        adjust=params['adjust'],
        cut=params['cut'],
        gridsize=params['gridsize'],
        clip=params['clip'])

    x2 = np.linspace(range[0], range[1], params['n'])

    try:
        y = kde.evaluate(x2)
    except ValueError:
        y = np.array([kde.evaluate(_x)[0] for _x in x2])

    return pd.DataFrame({'x': x2,
                         'density': y,
                         'scaled': y / np.max(y),
                         'count': y * n,
                         'n': n})

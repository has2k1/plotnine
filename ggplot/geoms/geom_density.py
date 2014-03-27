from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom
from scipy.stats import gaussian_kde
import numpy as np


class geom_density(geom):
    DEFAULT_AES = {'alpha': None, 'color': 'black', 'fill': None,
                   'linetype': 'solid', 'size': 1.0, 'weight': 1}
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'stat': 'density', 'position': 'identity', 'label': ''}

    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth',
                    'fill': 'facecolor'}
    _groups = {'alpha', 'color', 'facecolor', 'linestyle', 'linewidth'}

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop('x')
        # TODO: Implement weight
        # find where to multiply by it
        weight = pinfo.pop('weight')
        pinfo['label'] = self.params['label']

        try:
            float(x[0])
        except:
            try:
                # try to use it as a pandas.tslib.Timestamp
                x = [ts.toordinal() for ts in x]
            except:
                raise Exception("geom_density(): aesthetic x mapping needs to be convertable to float!")

        # TODO: Get "full" range of densities
        # i.e tail off to zero like ggplot2? But there is nothing
        # wrong with the current state.
        kde = gaussian_kde(x)
        bottom = np.min(x)
        top = np.max(x)
        step = (top - bottom) / 1000.0
        x = np.arange(bottom, top, step)
        y = kde.evaluate(x)

        # alpha only applies to the line, otherwise a single
        # needed for plot
        _alpha = pinfo.pop('alpha')
        _fc = pinfo.pop('facecolor')

        ax.plot(x, y, **pinfo)

        if _fc not in (None, False):
            _c = pinfo.pop('color')
            pinfo.pop('linewidth')
            pinfo['alpha'] = _alpha
            pinfo['facecolor'] = _c if _fc == True else _fc
            ax.fill_between(x, y1=np.zeros(len(x)), y2=y, **pinfo)

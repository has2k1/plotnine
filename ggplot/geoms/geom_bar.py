from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import pandas as pd
from .geom import geom
from pandas.lib import Timestamp


class geom_bar(geom):
    DEFAULT_AES = {'alpha': None, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.0, 'weight': None}
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'stat': 'bin', 'position': 'stack'}

    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth',
                    'fill': 'facecolor', 'color': 'edgecolor'}

    # NOTE: Currently, geom_bar does not support mapping
    # to alpha and linestyle. TODO: raise exception
    _groups = {'alpha', 'linestyle', 'linewidth'}

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop('x')
        weights = pinfo.pop('weight')

        # TODO: fix the weight aesthetic,
        # ggplot2 has the default as 1
        if weights is None:
            counts = pd.value_counts(x)
            labels = counts.index.tolist()
            weights = counts.tolist()
        else:
            # TODO: pretty sure this isn't right
            if not isinstance(x[0], Timestamp):
                labels = x
            else:
                df = pd.DataFrame({'weights':weights, 'timepoint': pd.to_datetime(x)})
                df = df.set_index('timepoint')
                ts = pd.TimeSeries(df.weights, index=df.index)
                ts = ts.resample('W', how='sum')
                ts = ts.fillna(0)
                weights = ts.values.tolist()
                labels = ts.index.to_pydatetime().tolist()

        indentation = np.arange(len(labels)) + 0.2
        width = 0.9
        idx = np.argsort(labels)
        labels, weights = np.array(labels)[idx], np.array(weights)[idx]
        labels = sorted(labels)

        # TODO: Add this test, preferably using fill aesthetic
        # p = ggplot(aes(x='factor(cyl)', color='factor(cyl)'), data=mtcars)
        # p + geom_bar(size=10)
        # mapped coloring aesthetics are required in ascending order acc. x
        for ae in ('edgecolor', 'facecolor'):
            if isinstance(pinfo[ae], list):
                pinfo[ae] = [color for _, color in
                             sorted(set(zip(x, pinfo[ae])))]

        ax.bar(indentation, weights, width, **pinfo)
        ax.autoscale()
        ax.set_xticks(indentation+width/2)
        ax.set_xticklabels(labels)

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import pandas as pd
from .geom import geom
from pandas.lib import Timestamp


class geom_bar(geom):
    VALID_AES = {'x', 'alpha', 'color', 'fill', 'linetype', 'size', 'weight'}
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'stat': 'bin', 'position':'stack'}

    _groups = {'color'}
    def plot(self, layer, ax):
        x = layer.pop('x')
        if 'weight' not in layer:
            counts = pd.value_counts(x)
            labels = counts.index.tolist()
            weights = counts.tolist()
        else:
            # TODO: pretty sure this isn't right
            weights = layer.pop('weight')
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

        layer['edgecolor'] = layer.pop('color', '#333333')
        layer['color'] = layer.pop('fill', '#333333')

        ax.bar(indentation, weights, width, **layer)
        ax.autoscale()
        ax.set_xticks(indentation+width/2)
        ax.set_xticklabels(labels)

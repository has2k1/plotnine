from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .geom import geom
from pandas.lib import Timestamp


class geom_bar(geom):
    VALID_AES = ['x', 'color', 'alpha', 'fill', 'label', 'weight', 'position']

    def plot_layer(self, layer):
        layer = dict((k, v) for k, v in layer.items() if k in self.VALID_AES)
        layer.update(self.manual_aes)

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

        if 'color' in layer:
            layer['edgecolor'] = layer['color']
            del layer['color']
        else:
            layer['edgecolor'] = '#333333'

        if 'fill' in layer:
            layer['color'] = layer['fill']
            del layer['fill']
        else:
            layer['color'] = '#333333'

        plt.bar(indentation, weights, width, **layer)
        plt.autoscale()
        return [
                {"function": "set_xticks", "args": [indentation+width/2]},
                {"function": "set_xticklabels", "args": [labels]}
            ]

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
    _aes_renames = {'linetype': 'linestyle'}

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop('x')
        if 'weight' not in pinfo:
            counts = pd.value_counts(x)
            labels = counts.index.tolist()
            weights = counts.tolist()
        else:
            # TODO: pretty sure this isn't right
            weights = pinfo.pop('weight')
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

        pinfo['edgecolor'] = pinfo.pop('color', '#333333')
        pinfo['color'] = pinfo.pop('fill', '#333333')

        ax.bar(indentation, weights, width, **pinfo)
        ax.autoscale()
        ax.set_xticks(indentation+width/2)
        ax.set_xticklabels(labels)

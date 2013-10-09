import matplotlib.pyplot as plt
from copy import deepcopy
from geom import geom
import pandas as pd
from scipy.stats import t
import numpy as np
from statsmodels.nonparametric.smoothers_lowess import lowess

class stat_smooth(geom):
    VALID_AES = ['x', 'y', 'color', 'alpha', 'label', 'se', 'method', 'span']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.iteritems() if k in self.VALID_AES}
        layer.update(self.manual_aes)

        if 'x' in layer:
            x = layer.pop('x')
        if 'y' in layer:
            y = layer.pop('y')
        if 'se' in layer:
            se = layer.pop('se')
        else:
            se = None
        if 'span' in layer:
            span = layer.pop('span')
        else:
            span = 2/3.
        if 'method' in layer:
            method = layer.pop('method')
        else:
            method = None
        # TODO: should probably change this to LOESS
        if method=="lm":
            pass
        elif method=="ma":
            y = pd.Series(y)
            std_err = pd.expanding_std(y, span)
            y = pd.rolling_mean(y, span)
            idx = pd.isnull(y)
            x = pd.Series(x)[idx==False]
            y = pd.Series(y)[idx==False]
            std_err = pd.Series(std_err)[idx==False]
            y1 = y - std_err
            y2 = y + std_err
        else:
            if isinstance(x[0], pd.tslib.Timestamp):
                x = [i.toordinal() for i in x]
            result = lowess(y, x, frac=span)
            x = pd.Series(result[::,0])
            y = pd.Series(result[::,1])
            lower, upper = t.interval(0.67, len(x), loc=0, scale=2)
            std = np.std(y)
            y1 = pd.Series(lower * std +  y)
            y2 = pd.Series(upper * std +  y)

        plt.plot(x.tolist(), y, **layer)
        if se==True:
            plt.fill_between(x.tolist(), y1.tolist(), y2.tolist(),
                    alpha=0.5, color="grey")
        

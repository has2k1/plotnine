import matplotlib.pyplot as plt
from copy import deepcopy
from geom import geom
import pandas as pd

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
            span = 1.0
        if 'method' in layer:
            method = layer.pop('method')
        else:
            method = None
        # TODO: should probably change this to LOESS
        if method=="lm":
            pass
        elif method=="":
            pass
        else:
            y = pd.Series(y)
            std_err = pd.expanding_std(y, span)
            y = pd.rolling_mean(y, span)
            idx = pd.isnull(y)
            x = pd.Series(x)[idx==False]
            y = pd.Series(y)[idx==False]
            std_err = pd.Series(std_err)[idx==False]
            y1 = y - std_err
            y2 = y + std_err
        plt.plot(x.tolist(), y, **layer)
        if se:
            plt.fill_between(x.tolist(), y1.tolist(), y2.tolist(),
                    alpha=0.5, color="grey")
        

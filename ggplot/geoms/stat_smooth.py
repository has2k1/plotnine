import matplotlib.pyplot as plt
from copy import deepcopy
from geom import geom
import pandas as pd

class stat_smooth(geom):
    VALID_AES = ['x', 'y', 'color', 'alpha', 'label']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.iteritems() if k in self.VALID_AES}
        layer.update(self.manual_aes)

        if 'x' in layer:
            x = layer.pop('x')
        if 'y' in layer:
            y = layer.pop('y')
        # TODO: should probably change this to LOESS
        if layer.get("method")=="lm":
            pass
        elif layer.get("method")=="":
            pass
        else:
            y = pd.Series(y)
            y = pd.rolling_mean(y, 10.)
            idx = pd.isnull(y)
            x = pd.Series(x)[idx==False]
            y = pd.Series(y)[idx==False]
        plt.plot(x, y, **layer)

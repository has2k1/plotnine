import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from copy import deepcopy
from geom import geom



class geom_bar(geom):
    VALID_AES = ['x', 'color', 'alpha', 'fill', 'label']

    def plot_layer(self, layer): 
        layer = {k: v for k, v in layer.iteritems() if k in self.VALID_AES}
        layer.update(self.manual_aes)

        x = layer.pop('x')
        counts = pd.value_counts(x)
        labels = counts.index.tolist()
        weights = counts.tolist()

        indentation = np.arange(len(labels))
        width = 0.35
        plt.bar(indentation, weights, width, **layer)
        return [
                {"function": "set_xticks", "args": [indentation+width]},
                {"function": "set_xticklabels", "args": [labels]}
            ]

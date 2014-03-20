from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib as mpl
from .geom import geom
import numpy as np

class geom_point(geom):
    VALID_AES = ['x', 'y', 'size', 'color', 'alpha', 'shape', 'label', 'cmap',
                 'position']

    def plot_layer(self, data, ax):
        groups = {'color', 'shape', 'alpha'}

        # NOTE: This is the correct check however with aes
        # set in ggplot(), self.aes is empty
        # groups = groups & set(self.aes) & set(data.columns)

        groups = groups & set(data.columns)
        if groups:
            for name, _data in data.groupby(list(groups)):
                _data = _data.to_dict('list')
                for ae in groups:
                    _data[ae] = _data[ae][0]
                self._plot(_data, ax)
        else:
            _data = data.to_dict('list')
            self._plot(_data, ax)

    def _plot(self, layer, ax):
        layer = dict((k, v) for k, v in layer.items() if k in self.VALID_AES)
        layer.update(self.manual_aes)

        if "size" in layer:
            layer["s"] = layer["size"]
            del layer["size"]

        if "shape" in layer:
            layer["marker"] = layer["shape"]
            del layer["shape"]

        # for some reason, scatter doesn't default to the same color styles
        # as the axes.color_cycle
        if "color" not in layer and "cmap" not in layer:
            layer["color"] = mpl.rcParams.get("axes.color_cycle", ["#333333"])[0]
        
        if "position" in layer:
            del layer["position"]
            layer['x'] *= np.random.uniform(.9, 1.1, len(layer['x']))
            layer['y'] *= np.random.uniform(.9, 1.1, len(layer['y']))

        ax.scatter(**layer)


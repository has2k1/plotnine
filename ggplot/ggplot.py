import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ggplot stuff
from components import colors, shapes, aes
from geoms import *


class ggplot(object):

    CONTINUOUS = ['x', 'y', 'size']
    DISCRETE = ['color', 'shape', 'marker', 'alpha']

    def __init__(self, aesthetics, data):
        # ggplot should just 'figure out' which is which
        if not isinstance(data, pd.DataFrame):
            aesthetics, data = data, aesthetics
            
        self.aesthetics = aesthetics
        self.data = data

        # defaults
        self.geoms= []
        self.n_dim_x = 1
        self.n_dim_y = 1
        self.facets = []
        # components
        self.title = None
        self.xlab = None
        self.ylab = None
        self.legend = True

    def __repr__(self):
        fig, axs = plt.subplots(self.n_dim_x, self.n_dim_y)
        plt.subplot(self.n_dim_x, self.n_dim_y, 1)
        
        if self.facets:
            cntr = 0
            for facet, frame in self.data.groupby(self.facets):
                for layer in self._get_layers(frame):
                    for geom in self.geoms:
                        plt.subplot(self.n_dim_x, self.n_dim_y, cntr)
                        callbacks = geom.plot_layer(layer)
                        if callbacks:
                            for callback in callbacks:
                                fn = getattr(axs[cntr], callback['function'])
                                fn(*callback['args'])
                plt.title(facet)
                cntr += 1
        else:
            for layer in self._get_layers(self.data):
                for geom in self.geoms:
                    plt.subplot(1, 1, 1)
                    callbacks = geom.plot_layer(layer)
                    if callbacks:
                        for callback in callbacks:
                            fn = getattr(axs, callback['function'])
                            fn(*callback['args'])
        
        if self.title:
            plt.title(self.title)
        if self.xlab:
            plt.xlabel(self.xlab)
        if self.ylab:
            plt.ylabel(self.ylab)
        if self.legend==True:
            plt.legend()

        return "ggplot" 

    def _get_layers(self, data=None):
        if data is None:
            data = self.data
        mapping = pd.DataFrame({
            ae: data.get(key, key)
                for ae, key in self.aesthetics.iteritems()
        })

        rev_color_mapping = {}
        if 'color' in mapping:
            possible_colors = np.unique(mapping.color)
            if set(possible_colors).issubset(set(colors.COLORS))==False:
                color = colors.color_gen()
                color_mapping = {value: color.next() for value in possible_colors}
                rev_color_mapping = {v: k for k, v in color_mapping.iteritems()}
                mapping.color = mapping.color.replace(color_mapping)

        rev_shape_mapping = {}
        if 'shape' in mapping:
            possible_shapes = np.unique(mapping['shape'])
            shape = shapes.shape_gen()
            shape_mapping = {value: shape.next() for value in possible_shapes}
            rev_shape_mapping = {v: k for k, v in shape_mapping.iteritems()}
            mapping['marker'] = mapping['shape'].replace(shape_mapping)
            del mapping['shape']

        keys = [ae for ae in self.DISCRETE if ae in mapping]
        layers = []
        if len(keys)==0:
            layers.append(mapping.to_dict('list'))
        else:
            for name, frame in mapping.groupby(keys):
                frame = frame.to_dict('list')
                for ae in self.DISCRETE:
                    if ae in frame:
                        frame[ae] = frame[ae][0]
                        if ae=="color":
                            label = rev_color_mapping.get(name[0], name[0])
                        elif ae=="shape" or ae=="marker":
                            if isinstance(name, (str, unicode, list)):
                                key = name[0]
                            else:
                                key = name
                                raise Exception("Cannot have numeric shape!")
                            label = rev_shape_mapping.get(key, key)
                        frame['label'] = label
                layers.append(frame)
        return layers


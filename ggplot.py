import pandas as pd
import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
from copy import deepcopy
from scipy.stats import gaussian_kde

from components import colors, shapes


aes = dict

class ggplot(object):

    CONTINUOUS = ['x', 'y']
    DISCRETE = ['color', 'shape', 'marker', 'alpha']

    def __init__(self, aesthetics, data):
        self.aesthetics = aesthetics
        self.data = data
        self.geoms= []
        self.n_dim_x = 1
        self.n_dim_y = 1
        self.facets = []
        # components
        self.title = None
        self.xlab = None
        self.ylab = None

    def __repr__(self):
        fig, axs = plt.subplots(self.n_dim_x, self.n_dim_y)
        plt.subplot(self.n_dim_x, self.n_dim_y, 1)
        
        if self.facets:
            cntr = 0
            for facet, frame in self.data.groupby(self.facets):
                for layer in self._get_layers(frame):
                    for geom in self.geoms:
                        plt.subplot(self.n_dim_x, self.n_dim_y, cntr)
                        geom.plot_layer(layer)
                cntr += 1
        else:
            for layer in self._get_layers(self.data):
                for geom in self.geoms:
                    plt.subplot(1, 1, 1)
                    geom.plot_layer(layer)
        
        if self.title:
            plt.title(self.title)
        if self.xlab:
            plt.xlabel(self.xlab)
        if self.ylab:
            plt.ylabel(self.ylab)
        return "ggplot" 

    def _get_layers(self, data=None):
        if data is None:
            data = self.data
        mapping = pd.DataFrame({
            ae: data.get(key, key)
                for ae, key in self.aesthetics.iteritems()
        })

        if 'color' in mapping:
            possible_colors = np.unique(mapping.color)
            if set(possible_colors).issubset(set(colors.COLORS))==False:
                color = colors.color_gen()
                color_mapping = {value: color.next() for value in possible_colors}
                mapping.color = mapping.color.replace(color_mapping)

        if 'shape' in mapping:
            possible_shapes = np.unique(mapping['shape'])
            shape = shapes.shape_gen()
            shape_mapping = {value: shape.next() for value in possible_shapes}
            mapping['marker'] = mapping['shape'].replace(shape_mapping)
            del mapping['shape']

        keys = [ae for ae in self.DISCRETE if ae in mapping]
        layers = []
        if len(keys)==0:
            layers.append(mapping)
        else:
            for name, frame in mapping.groupby(keys):
                frame = frame.to_dict('list')
                for ae in self.DISCRETE:
                    if ae in frame:
                        frame[ae] = frame[ae][0]
                layers.append(frame)
        return layers

class geom(object):
    def __init__(self, **kwargs):
        self.manual_aes = {k: v for k, v in kwargs.iteritems() if k in self.VALID_AES}

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.geoms.append(self)
        return gg

class geom_point(geom):
    VALID_AES = ['x', 'y', 'color', 'alpha', 'shape', 'marker']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.iteritems() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        plt.scatter(**layer)

class geom_hist(geom):
    VALID_AES = ['x', 'color', 'alpha']

    def plot_layer(self, layer): 
        layer = {k: v for k, v in layer.iteritems() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        plt.hist(**layer)

class geom_density(geom):
    VALID_AES = ['x', 'color', 'alpha']

    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.iteritems() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        if 'x' in layer:
            x = layer.pop('x')
        kde = gaussian_kde(x)
        bottom = np.min(x)
        top = np.max(x)
        step = (top - bottom) / 1000.0
        x = np.arange(bottom, top, step)
        y = kde.evaluate(x)
        plt.plot(x, y, **layer)

class geom_line(geom):
    VALID_AES = ['x', 'y', 'color', 'alpha']
    def plot_layer(self, layer):
        layer = {k: v for k, v in layer.iteritems() if k in self.VALID_AES}
        layer.update(self.manual_aes)
        if 'x' in layer:
            x = layer.pop('x')
        if 'y' in layer:
            y = layer.pop('y')
        pl.plot(x, y, **layer)

class stat_smooth(geom):
    VALID_AES = ['x', 'y', 'color', 'alpha']

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
        pl.plot(x, y, **layer)

class facet_wrap(object):
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def __radd__(self, gg):

        x = gg.data.get(self.x)
        y = gg.data.get(self.y)
        if x is None:
            n_dim_x = 1
        else:
            n_dim_x = x.nunique()
        if y is None:
            n_dim_y = 1
        else:
            n_dim_y = y.nunique()
        
        gg.n_dim_x, gg.n_dim_y = n_dim_x, n_dim_y
        facets = []
        if self.x:
            facets.append(self.x)
        if self.y:
            facets.append(self.y)
        gg.facets = facets

        return deepcopy(gg)


class ggtitle(object):
    def __init__(self, title):
        self.title = title

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.title = self.title
        return gg

class xlab(object):
    def __init__(self, xlab):
        self.xlab = xlab

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.xlab = self.xlab
        return gg

class ylab(object):
    def __init__(self, ylab):
        self.ylab = ylab

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.ylab = self.ylab
        return gg

class labs(object):
    def __init__(self, xlab=None, ylab=None):
        self.xlab = xlab
        self.ylab = ylab

    def __radd__(self, gg):
        gg = deepcopy(gg)
        if self.xlab:
            gg.xlab = self.xlab
        if self.ylab:
            gg.ylab = self.ylab
        return gg

df = pd.DataFrame({
    "x": np.arange(0, 100),
    "y": np.arange(0, 100),
    "z": np.arange(0, 100)
})

df['cat'] = np.where(df.x*2 > 50, 'blah', 'blue')
df['cat'] = np.where(df.y > 50, 'hello', df.cat)
df['cat2'] = np.where(df.y < 15, 'one', 'two')
df['y'] = np.sin(df.y)

gg = ggplot(aes(x="x", y="z", color="cat", alpha=0.2), data=df)
gg = ggplot(aes(x="x", color="c"), data=pd.DataFrame({"x": np.random.normal(0, 1, 10000), "c": ["blue" if i%2==0 else "red" for i in range(10000)]}))
#print gg + geom_density() + xlab("Density chart")
gg = ggplot(aes(x="x", y="y", shape="cat2", color="cat"), data=df)
#print gg + geom_point() + facet_wrap(x="cat", y="cat2") 
#print gg + geom_point() + facet_wrap(y="cat2") + ggtitle("My Single Facet") 
#print gg + stat_smooth(color="blue") + ggtitle("My Smoothed Chart")
#print gg + geom_hist() + ggtitle("My Histogram")
print gg + geom_point()


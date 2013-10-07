import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ggstyle import rstyle
from pal import facet_grid


def line(ax, args):
    x = args.pop('x')
    y = args.pop('y')
    ax.plot(x, y, **args)
    return ax

def aes():
    return 

class Geom(object):
    def __init__(self, aesthetics=None):
        self.aesthetics = aesthetics

    def __repr__(self):
        axs = self.render()
        for ax in axs:
            plot = rstyle(ax)
        pl.show()
        return ""

    def __radd__(layer, self):
        
        if isinstance(layer, FacetWrap):
            self.facets.append(layer.x)
            return self
        else:
            for k, v in self.aesthetics.mapping().iteritems():
                if getattr(layer.aesthetics, k) is None:
                    setattr(layer.aesthetics, k, v)
            self.layers.append(layer)

        return self

    def show(self):
        self.render()
        pl.show()

    def render(self):
        pass

class Ggpy(Geom):

    def __init__(self, aesthetics=None, data=None):
        if aesthetics:
            self.aesthetics = aesthetics
        self.data = data
        self.layers = []
        self.facets = []

    def render(self):
        # fig, ax = plt.subplots(1)
        if len(self.facets)==0:
            fix, axs = plt.subplots(1)
            for layer in self.layers:
                axs = layer.render(axs, None)
            axs = [axs]
        else:
            facets = np.unique(self.facets[0])
            fix, axs = plt.subplots(len(facets))
            for ax, facet in zip(axs, facets):
                mask = np.array(self.facets[0])==facet
                for layer in self.layers:
                    ax = layer.render(ax, mask)
        return axs


class GeomPoint(Geom):

    def render(self, ax, mapping):
        ax.scatter(**mapping)
        return ax


class GeomLine(Geom):

    def render(self, ax, mapping):
        if self.aesthetics:
            for static_col in self.aesthetics:
                mapping[static_col] = self.aesthetics[static_col]
        ax = line(ax, mapping)
        return ax

class GeomHline(Geom):

    def render(self, ax, mapping):
        x = self.aesthetics.mapping()['x']
        mapping['y'] = mapping['yintercept']
        del mapping['yintercept']
        ax = line(ax, mapping)
        return ax


layers = [
    GeomPoint(),
    GeomLine({"color": "red"}),
]


df = pd.DataFrame({
    "pins": range(10),
    "needles": range(10),
    "colors": ["red" if i%2==0 else "blue" for i in range(10)],
    "otherstuff": ["dog" if i%2==0 else "cat" for i in range(10)]
})

aes = {"x": "pins", "y": "needles"}
aes_map =  {v: k for k,v in aes.iteritems()}

plot_df = df.rename(columns=aes_map)

datas = facet_grid(plot_df, [], "colors", "otherstuff")
plot_components = ['x', 'y', 'color', 'shape']

fig, axs = plt.subplots(len(datas[0]), len(datas))

print axs

def subplots(x):
    for i in x:
        for j in i:
            yield j

canvases = subplots(axs)
for row in datas:
    for plot_data in row:
        canvas = canvases.next()
        plot_data = {k: v for k, v in plot_data.iteritems() if k in plot_components}
        print plot_data
        for layer in layers:
            layer.render(canvas, plot_data)


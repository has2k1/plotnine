import pylab as pl
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde
import pandas as pd
import smoothers
from ggstyle import rstyle
import time
import math, random
from colors import color_gen


def line(ax, args):
    x = args.pop('x')
    y = args.pop('y')
    ax.plot(x, y, **args)
    return ax

def bar(ax, args):
    x = args.pop('x')
    weights = args.pop('weights')
    ax.bar(x, weights, **args)
    return ax

def ribbon(ax, args):
    x = args.pop('x')
    ymin = args.pop('ymin')
    ymax = args.pop('ymax')
    ax.fill_between(x, ymin, ymax, **args)
    return ax

def density(ax, args):
    x = args['x']
    density = gaussian_kde(x)
    xs = np.linspace(0,8,200)
    density.covariance_factor = lambda : .25
    density._compute_covariance()
    xs = np.linspace(np.min(x), np.max(x), 200)
    args['x'] = xs
    args['y'] = density(xs)
    return line(ax, args)

def is_iterable(some_object):
    try:
        some_object_iterator = iter(some_object)
    except TypeError, te:
        pass

class aes(object):
    def __init__(self, x=None, y=None, colour=None, size=None, shape=None, alpha=None,
                weights=None, xintercept=None, yintercept=None, ymin=None, ymax=None):
        # don't split by these
        self.x = x
        self.y = y
        self.weights = weights

        # maybe split by these
        self.xintercept = xintercept
        self.yintercept = yintercept
        self.ymin = ymin
        self.ymax = ymax

        # split by these
        self.size = size
        self.color = colour
        self.shape = shape
        self.alpha = alpha

        idx_len = max([len(v) for k, v in vars(self).iteritems() if is_iterable(v)] + [0])

        self.data = {}
        for col, value in vars(self).iteritems():
            if value is None:
                continue
            if isinstance(value, list)==False:
                value = [value for value in range(idx_len)]
            self.data[col] = value

        self.data = pd.DataFrame(self.data)


    def mapping(self, mask=None):
        group = [g for g in ["size", "color", "shape", "alpha"] if getattr(self, g) is not None]
        self.data.groupby(groups)
        mapping = vars(self)
        result = {}
        for k, v in mapping.iteritems():
            if v is not None and k != "data":
                if mask is None:
                    mask = [True for i in range(len(self.data))]
                if not is_iterable(v):
                    result[k] = v
                else:
                    result[k] = [value for value, keep in zip(v, mask) if keep==True]
        return result

class Geom(object):
    def __init__(self, aesthetics=None, data=None):
        if aesthetics:
            self.aesthetics = aesthetics
        else:
            self.aesthetics = aes()
        self.data = data
        self.layers = []

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

    def render(self, ax, mask):
        ax.scatter(**self.aesthetics.mapping(mask))
        return ax

class GeomHistogram(Geom):

    def render(self, ax, mask):
        ax.hist(**self.aesthetics.mapping(mask))
        return ax

class GeomLine(Geom):

    def render(self, ax, mask):
        ax = line(ax, self.aesthetics.mapping(mask))
        return ax

class GeomHline(Geom):

    def render(self, ax, mask):
        x = self.aesthetics.mapping()['x']
        self.aesthetics.y = None
        self.aesthetics.y = [self.aesthetics.mapping()['yintercept'] for i in range(len(x))]
        self.aesthetics.yintercept = None
        ax = line(ax, self.aesthetics.mapping(mask))
        return ax

class GeomVline(Geom):

    def render(self, ax, mask):
        y = self.aesthetics.mapping()['y']
        self.aesthetics.x = None
        self.aesthetics.x = [self.aesthetics.mapping()['xintercept'] for i in range(len(y))]
        self.aesthetics.xintercept = None
        ax = line(ax, self.aesthetics.mapping(mask))
        return ax

class GeomBar(Geom):

    def render(self, ax, mask):
        ax = bar(ax, self.aesthetics.mapping(mask))
        return ax

class GeomRibbon(Geom):

    def render(self, ax, mask):
        ax = ribbon(ax, self.aesthetics.mapping(mask))
        return ax

class GeomDensity(Geom):

    def render(self, ax, mask):
        ax = density(ax, self.aesthetics.mapping(mask))
        return ax

class GgTitle(Geom):

    def __init__(self, title):
        self.aesthetics = aes()
        self.title = title

    def render(self, ax, mask):
        ax.set_title(self.title)
        return ax

class Xlab(Geom):

    def __init__(self, xlab):
        self.aesthetics = aes()
        self.xlab = xlab

    def render(self, ax, mask):
        ax.set_xlabel(self.xlab)
        return ax

class Ylab(Geom):

    def __init__(self, ylab):
        self.aesthetics = aes()
        self.ylab = ylab

    def render(self, ax, mask):
        ax.set_ylabel(self.ylab)
        return ax


class StatSmooth(Geom):

    def __init__(self, aesthetics=None, method="lm", se=True, period=None):
        if aesthetics:
            self.aesthetics = aesthetics
        else:
            self.aesthetics = aes()
        self.method = method
        self.se = se
        self.period = period

    def render(self, ax, mask):

        x = pd.Series(self.aesthetics.mapping()['x'])
        y = pd.Series(self.aesthetics.mapping()['y'])
        
        if self.method=="lm":
            low_band, smoothed, high_band = smoothers.lm(x, y)
        elif self.method=="ma":
            low_band, smoothed, high_band = smoothers.ma(y, self.period)
        elif self.method=="lowess":
            smoothed = smoothers.lowess(x, y)
        else:
            smoothed = y
        ax.plot(self.aesthetics.mapping()['x'], smoothed)
        if self.se:
            aesthetics = {"x": self.aesthetics.mapping()['x'], "ymin": low_band,
                          "ymax": high_band, "color": "grey", "alpha": 0.4}
            ribbon(ax, aesthetics)
        return ax

class StatBin2d(Geom):

    def render(self, ax, mask):
        ax.histogram2d(**self.aesthetics.mapping(mask))
        return ax

class FacetWrap(Geom):

    def __init__(self, x):
        self.x = x

p = Ggpy(aes(x=range(100), y=map(lambda x: math.cos(x), range(100))))
p = p + GeomPoint(aes(colour="red")) + \
     GeomLine(aes(x=range(100), y=map(lambda x: math.sin(x), range(100)))) + \
     StatSmooth(aes(x=range(100), y=map(lambda x: math.sin(x), range(100))), method="lm") + \
     GgTitle("Greg's Plot")
print p

p = Ggpy(aes(x=range(100), y=map(lambda x: math.cos(x), range(100))))
p = p + GeomPoint(aes(colour="red")) + \
     StatSmooth(method="ma", period=2*3.14) + \
     GgTitle("Greg's Plot") + Xlab("Greg's X") + Ylab("Greg's Y")
print p

p = Ggpy(aes(x=range(100), y=map(lambda x: math.cos(x), range(100))))
p = p + GeomPoint() + GeomHline(aes(yintercept=0.5, colour="red")) +\
        GeomVline(aes(xintercept=50, colour="green"))
print p


p = Ggpy(aes(x=[random.random() for i in range(100)]))
p = p + GeomHistogram()
print p

p = Ggpy(aes(x=range(5), weights=[100, 200, 300, 200, 100]))
p + GeomBar(aes(alpha=0.1))
print p

p = Ggpy(aes(x=range(5), ymin=[10, 20, 34, 20, 10],  ymax=[100, 200, 300, 200, 100]))
p + GeomRibbon()
print p

data = np.random.normal(size=1000)
p = Ggpy(aes(x=data, colour="green"))
p = p + GeomDensity()
print p

p = Ggpy(aes(x=range(100), y=map(lambda x: math.cos(x), range(100))))
p = p + GeomPoint() + StatSmooth(se=True)
print p

# x = range(100)
# y = map(lambda x: math.cos(x) * random.random() * 10 if x%2==0  else x * 5 + random.random() * 50, range(100))
# data = [i%2 for i in x]
# colours = ["blue" if i%2==0 else "red" for i in x]

# p = Ggpy(aes(x=x, y=y, colour=colours), data=data)
# p = p + GeomPoint() + StatSmooth() + FacetWrap(data)
# print p


# p = GeomPoint(aes(x=range(100), y=range(100)))
# print p
# time.sleep(.5)

# p = GeomLine(aes(x=range(100), y=range(100)))
# print p
# time.sleep(.5)

# p = GeomHistogram(aes(x=np.random.normal(0, 1, 1000), colour="red"))
# print p

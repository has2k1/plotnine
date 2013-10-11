import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ggplot stuff
from components import colors, shapes, aes
from components.legend import draw_legend
from geoms import *
from scales import *
from utils import *

import re


def is_identity(x):
    if x in colors.COLORS:
        return True
    elif x in shapes.SHAPES:
        return True
    elif isinstance(x, (float, int)):
        return True
    else:
        return False

class ggplot(object):
    """
    ggplot is the base layer or object that you use to define
    the components of your chart (x and y axis, shapes, colors, etc.).
    You can combine it with layers (or geoms) to make complex graphics
    with minimal effort.

    Parameters
    -----------
    aesthetics:  aes (ggplot.components.aes.aes)
        aesthetics of your plot
    data:  pandas DataFrame (pd.DataFrame)
        a DataFrame with the data you want to plot

    Examples
    ----------
    p = ggplot(aes(x='x', y='y'), data=diamonds)
    print p + geom_point()
    """

    # TODO: make color discrete and continuous
    CONTINUOUS = ['x', 'y', 'size']
    DISCRETE = ['color', 'shape', 'marker', 'alpha']

    def __init__(self, aesthetics, data):
        # ggplot should just 'figure out' which is which
        if not isinstance(data, pd.DataFrame):
            aesthetics, data = data, aesthetics
            
        self.aesthetics = aesthetics
        self.data = data

        # Look for alias/lambda functions
        # The test criteria could use some work
        for ae, name in self.aesthetics.iteritems():
            if name not in self.data and not is_identity(name):
                result = re.findall(r'(?:[A-Z])|(?:[A-Za_-z0-9]+)|(?:[/*+_=\(\)-])', name)
                if re.match("factor[(][A-Za-z_0-9]+[)]", name):
                    m = re.search("factor[(]([A-Za-z_0-9]+)[)]", name)
                    self.data[name] = self.data[m.group(1)].apply(str)
                else:
                    lambda_column = ""
                    for item in result:
                        if re.match("[/*+_=\(\)-]", item):
                            pass
                        elif re.match("^[0-9.]+$", item):
                            pass
                        else:
                            item = "self.data.get('%s')" % item
                        lambda_column += item 
                    self.data[name] = eval(lambda_column)
        # defaults
        self.geoms= []
        self.n_wide = 1
        self.n_high = 1
        self.n_dim_x = None
        self.n_dim_y = None
        self.facets = []
        self.facet_type = None
        # components
        self.title = None
        self.xlab = None
        self.ylab = None
        self.xlimits = None
        self.ylimits = None
        self.legend = {}

        # continuous color configs
        self.color_scale = None
        self.colormap = plt.cm.Blues

    def __repr__(self):
        # TODO: Handle facet_wrap better so that we only have
        # as many plots as we do discrete values. Currently it
        # creates a grid of plots but doesn't use all of them
        if self.facet_type=="grid":
            fig, axs = plt.subplots(self.n_wide, self.n_high, 
                    sharex=True, sharey=True)
        elif self.facet_type=="wrap":
            subplots_available = self.n_wide * self.n_high
            extra_subplots = subplots_available - self.n_dim_x

            fig, axs = plt.subplots(self.n_wide, self.n_high)
            for extra_plot in axs.flatten()[-extra_subplots:]:
                extra_plot.axis('off')

            plots = [None for i in range(self.n_dim_x)]
            for i in range(self.n_dim_x):
                idx = (i % self.n_high) * self.n_wide + (i % self.n_wide)
                plots[idx] = (i % self.n_wide, i % self.n_high)

            plots = [plot for plot in plots if plot is not None]
            plots = sorted(plots, key=lambda x: x[1] + x[0] * self.n_high + 1)

        else:
            fig, axs = plt.subplots(self.n_wide, self.n_high)

        plt.subplot(self.n_wide, self.n_high, 1)

        # Faceting just means doing an additional groupby. The
        # dimensions of the plot remain the same
        if self.facets:
            cntr = 0
            for facet, frame in self.data.groupby(self.facets):
                for layer in self._get_layers(frame):
                    for geom in self.geoms:
                        if self.facet_type=="wrap":
                            if cntr+1 > len(plots):
                                continue
                            pos = plots[cntr]
                            if pos is None:
                                continue
                            y_i, x_i = pos
                            pos = x_i + y_i * self.n_high + 1
                            plt.subplot(self.n_wide, self.n_high, pos) 
                        else:
                            plt.subplot(self.n_wide, self.n_high, cntr)
                            # TODO: this needs some work
                            if (cntr % self.n_high)!=0:
                                plt.tick_params(axis='y', which='both', 
                                        bottom='off', top='off',
                                        labelbottom='off')

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
        
        # Handling the details of the chart here; might be a better
        # way to do this...
        if self.title:
            plt.title(self.title)
        if self.xlab:
            plt.xlabel(self.xlab)
        if self.ylab:
            plt.ylabel(self.ylab)
        if self.xlimits:
            plt.xlim(self.xlimits)
        if self.ylimits:
            plt.ylim(self.ylimits)

        # TODO: Having some issues here with things that shouldn't have a legend
        # or at least shouldn't get shrunk to accomodate one. Need some sort of
        # test in place to prevent this OR prevent legend getting set to True.
        if self.legend:
            if self.facets:
                if 1==2:
                    ax_to_use = [ax for ax in axs if not isinstance(ax, np.ndarray)]
                    ax = axs[-1]
                    box = ax.get_position()
                    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
                    cntr = 0
                    for name, legend in self.legend.iteritems():
                        ax.add_artist(draw_legend(ax, legend, name, cntr))
                        cntr += 1
            else:
                box = axs.get_position()
                axs.set_position([box.x0, box.y0, box.width * 0.8, box.height])
                cntr = 0
                for name, legend in self.legend.iteritems():
                    if legend:
                        axs.add_artist(draw_legend(axs, legend, name, cntr))
                        cntr += 1

        # TODO: We can probably get pretty sugary with this
        return "<ggplot: (%d)>" % self.__hash__() 

    def _get_layers(self, data=None):
        # This is handy because... (something to do w/ facets?)
        if data is None:
            data = self.data
        # We want everything to be a DataFrame. We're going to default
        # to key to handle items where the user hard codes a aesthetic
        # (i.e. alpha=0.6)
        mapping = pd.DataFrame({
            ae: data.get(key, key)
                for ae, key in self.aesthetics.iteritems()
        })
        if "x" in self.aesthetics and self.xlab is None:
            self.xlab = self.aesthetics['x']
        if "y" in self.aesthetics and self.ylab is None:
            self.ylab = self.aesthetics['y']
        mapping = mapping.dropna()

        # We need to normalize size so that the points aren't really big or
        # really small.
        # TODO: add different types of normalization
        if "size" in mapping:
            mapping.size = mapping.size.astype(np.float)
            mapping.size = 200.0 * (mapping.size - mapping.size.min()) / \
                    (mapping.size.max() - mapping.size.min())

        # Here we're mapping discrete values to colors/shapes. For colors
        # we're also checking to see if we don't need to map them (i.e. if vars
        # are 'blue', 'green', etc.). The reverse mapping allows us to convert
        # from the colors/shapes to the original values.
        rev_color_mapping = {}
        if 'color' in mapping:
            possible_colors = np.unique(mapping.color)
            if set(possible_colors).issubset(set(colors.COLORS))==False:
                if "color" in mapping._get_numeric_data().columns:
                    mapping['cmap'] = self.colormap
                else:
                    # discrete
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
        if "cmap" in mapping:
            keys.remove("color")
        layers = []
        if len(keys)==0:
            legend = {}
            frame = mapping.to_dict('list')
            if "cmap" in frame:
                frame["cmap"] = frame["cmap"][0]
                quantiles = np.percentile(mapping.color, [0, 25, 50, 75, 100])
                # TODO: add support for more colors
                if self.color_scale:
                    key_colors = self.color_scale
                else:
                    key_colors = ["white", "lightblue", "skyblue", "blue", "navy"]
                legend["color"] = dict(zip(key_colors, quantiles))
            layers.append(frame)
        else:
            legend = {"color": {}, "marker": {}}
            for name, frame in mapping.groupby(keys):
                frame = frame.to_dict('list')
                for ae in self.DISCRETE:
                    if ae in frame:
                        frame[ae] = frame[ae][0]
                        if len(keys) > 1:
                            aes_name = name[keys.index(ae)]
                        else:
                            aes_name = name
                        if ae=="color":
                            label = rev_color_mapping.get(aes_name, aes_name)
                            legend[ae][frame[ae]] = label
                        elif ae=="shape" or ae=="marker":
                            legend[ae][frame[ae]] = rev_shape_mapping.get(aes_name, aes_name)
                            # raise Exception("Cannot have numeric shape!")
                            label = rev_shape_mapping.get(aes_name, aes_name)
                        frame['label'] = label
                if "cmap" in frame:
                    frame["cmap"] = frame["cmap"][0]
                layers.append(frame)
        # adding legends back to the plot
        self.legend = legend
        return layers


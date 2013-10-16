import sys # need this for sys.hexversion to see if its py3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.dates import DateFormatter
# ggplot stuff
from .components import colors, shapes, linestyles, aes
from .components.legend import draw_legend
from .geoms import *
from .scales import *
from .utils import *

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

    CONTINUOUS = ['x', 'y', 'size', 'alpha']
    DISCRETE = ['color', 'shape', 'marker', 'alpha', 'linestyle']

    def __init__(self, aesthetics, data):
        # ggplot should just 'figure out' which is which
        if not isinstance(data, pd.DataFrame):
            aesthetics, data = data, aesthetics

        self.aesthetics = aesthetics
        self.data = data

        # Look for alias/lambda functions
        # The test criteria could use some work
        # py3 doesnt have iteritems(), iterator should be
        # small enough that we lose nothing by using items() in py2
        for ae, name in self.aesthetics.items():
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
        # format for x/y major ticks
        self.xtick_formatter = None
        self.xbreaks = None
        self.xtick_labels = None
        self.xmajor_locator = None
        self.xminor_locator = None
        self.ytick_formatter = None
        self.xlimits = None
        self.ylimits = None
        self.legend = {}

        # continuous color configs
        self.color_scale = None
        self.colormap = plt.cm.Blues

    def __repr__(self):
        # TODO: Handle facet_grid better. Currently facet_grid doesn't
        # fuse the plots together, they're individual subplots.
        if self.facet_type=="grid":
            fig, axs = plt.subplots(self.n_wide, self.n_high,
                    sharex=True, sharey=True)
            plt.subplots_adjust(wspace=.05, hspace=.05)
        elif self.facet_type=="wrap":
            subplots_available = self.n_wide * self.n_high
            extra_subplots = subplots_available - self.n_dim_x

            fig, axs = plt.subplots(self.n_wide, self.n_high)
            for extra_plot in axs.flatten()[-extra_subplots:]:
                extra_plot.axis('off')

            # TODO: This isn't working
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
            if len(self.facets)==2:
                for facets, frame in self.data.groupby(self.facets):
                    pos = self.facet_pairs.index(facets) + 1
                    plt.subplot(self.n_wide, self.n_high, pos)
                    for layer in self._get_layers(frame):
                        for geom in self.geoms:
                            callbacks = geom.plot_layer(layer)
                # This needs to enumerate all possibilities
                for pos, facets in enumerate(self.facet_pairs):
                    pos += 1
                    if pos <= self.n_high:
                        plt.subplot(self.n_wide, self.n_high, pos)
                        plt.table(cellText=[[facets[1]]], loc='top',
                                cellLoc='center', cellColours=[['lightgrey']])
                    if pos % self.n_high==0:
                        plt.subplot(self.n_wide, self.n_high, pos)
                        x = max(plt.xticks()[0])
                        y = max(plt.yticks()[0])
                        ax = axs[pos % self.n_wide][pos % self.n_high]
                        plt.text(x*1.025, y/2., facets[0],
                                bbox=dict(facecolor='lightgrey', color='black'),
                                fontdict=dict(rotation=-90, verticalalignment="center")
                                )
                    plt.subplot(self.n_wide, self.n_high, pos)

                    # TODO: Something is wrong w/ facet_grid colors

                    # TODO: We need to add in scales="free|free_y|free_x" for faceting.
                    # We can throw this in here. Loop thru and find the smallest/biggest
                    # for x and y. Then loop back thru and set xticks() and yticks() for
                    # each to the min/max values. We can create a range that goes between
                    # the min and max w/ the same number of ticks as the other axes.
                    if pos % self.n_high!=1:
                        ticks = plt.yticks()
                        plt.yticks(ticks[0], [])

                    if pos <= (len(self.facet_pairs) - self.n_high):
                        ticks = plt.xticks()
                        plt.xticks(ticks[0], [])


            else:
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
                                if (cntr % self.n_high)==-1:
                                    plt.tick_params(axis='y', which='both',
                                            bottom='off', top='off',
                                            labelbottom='off')
                            callbacks = geom.plot_layer(layer)
                            if callbacks:
                                for callback in callbacks:
                                    fn = getattr(axs[cntr], callback['function'])
                                    fn(*callback['args'])
                    #TODO: selective titles
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

        # Handling the details of the chart here; probably be a better
        # way to do this...
        if self.title:
            plt.title(self.title)
        if self.xlab:
            if self.facet_type=="grid":
                fig.text(0.5, 0.025, self.xlab)
            else:
                plt.xlabel(self.xlab)
        if self.ylab:
            if self.facet_type=="grid":
                fig.text(0.025, 0.5, self.ylab, rotation='vertical')
            else:
                plt.ylabel(self.ylab)
        if self.xmajor_locator:
            plt.gca().xaxis.set_major_locator(self.xmajor_locator)
        if self.xtick_formatter:
            plt.gca().xaxis.set_major_formatter(self.xtick_formatter)
            fig.autofmt_xdate()
        if self.xbreaks: # xbreaks is a list manually provided
            plt.gca().xaxis.set_ticks(self.xbreaks)
        if self.xtick_labels:
            plt.gca().xaxis.set_ticklabels(self.xtick_labels)
        if self.ytick_formatter:
            plt.gca().yaxis.set_major_formatter(self.ytick_formatter)
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
                    ax = axs[0][self.n_wide]
                    box = ax.get_position()
                    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
                    cntr = 0
                    for name, legend in self.legend.items():
                        ax.add_artist(draw_legend(ax, legend, name, cntr))
                        cntr += 1
            else:
                box = axs.get_position()
                axs.set_position([box.x0, box.y0, box.width * 0.8, box.height])
                cntr = 0
                for name, legend in self.legend.items():
                    if legend:
                        axs.add_artist(draw_legend(axs, legend, name, cntr))
                        cntr += 1

        # TODO: We can probably get more sugary with this
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
                for ae, key in self.aesthetics.items()
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
                    if sys.hexversion > 0x03000000:
                        color_mapping = {value: color.__next__() for value in possible_colors}
                    else:
                        color_mapping = {value: color.next() for value in possible_colors}
                    rev_color_mapping = {v: k for k, v in color_mapping.items()}
                    mapping.color = mapping.color.replace(color_mapping)

        rev_shape_mapping = {}
        if 'shape' in mapping:
            possible_shapes = np.unique(mapping['shape'])
            shape = shapes.shape_gen()
            shape_mapping = {value: shape.next() for value in possible_shapes}
            rev_shape_mapping = {v: k for k, v in shape_mapping.items()}
            mapping['marker'] = mapping['shape'].replace(shape_mapping)
            del mapping['shape']

        rev_linetype_mapping = {}
        if 'linestyle' in mapping:
            mapping['linestyle'] = mapping['linestyle'].apply(str)
            possible_styles = np.unique(mapping['linestyle'])
            linestyle = linestyles.line_gen()
            line_mapping = {value: linestyle.next() for value in possible_styles}
            rev_linetype_mapping = {v: k for k, v in line_mapping.items()}
            mapping['linestyle'] = mapping['linestyle'].replace(line_mapping)

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
            legend = {"color": {}, "marker": {}, "linestyle": {}}
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
                        elif ae=="linestyle":
                            legend[ae][frame[ae]] = rev_linetype_mapping.get(aes_name, aes_name)
                            label = rev_linetype_mapping.get(aes_name, aes_name)
                        elif ae=="alpha":
                            label = ""
                        frame['label'] = label
                if "cmap" in frame:
                    frame["cmap"] = frame["cmap"][0]
                layers.append(frame)
        if "size" in mapping:
            labels = np.percentile(mapping['size'], [5, 25, 50, 75, 95])
            quantiles = np.percentile(self.data[self.aesthetics['size']], [5, 25, 50, 75, 95])
            legend["size"] = dict(zip(labels, quantiles))
        # adding legends back to the plot
        self.legend = legend
        return layers


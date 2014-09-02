from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
from copy import deepcopy

import pandas as pd
import pandas.core.common as com
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from patsy.eval import EvalEnvironment

from .components import colors, shapes
from .components.legend import add_legend
# from .geoms import *
# from .scales import *
from .facets import facet_null, facet_grid
from .themes.theme_gray import theme_gray
from .utils import is_waive
from .utils.exceptions import GgplotError, gg_warning
from .utils.ggutils import gg_context
from .panel import Panel
from .layer import add_group
from .scales.scales import Scales
from .scales.scales import scales_add_missing
from .scales.scale import scale_discrete


__all__ = ["ggplot"]
__all__ = [str(u) for u in __all__]

# Show plots if in interactive mode
if sys.flags.interactive:
    plt.ion()


class ggplot(object):
    """
    ggplot is the base layer or object that you use to define
    the components of your chart (x and y axis, shapes, colors, etc.).
    You can combine it with layers (or geoms) to make complex graphics
    with minimal effort.

    Parameters
    -----------
    aesthetics :  aes (ggplot.components.aes.aes)
        aesthetics of your plot
    data :  pandas DataFrame (pd.DataFrame)
        a DataFrame with the data you want to plot

    Examples
    ----------
    >>> p = ggplot(aes(x='x', y='y'), data=diamonds)
    >>> print(p + geom_point())
    """

    CONTINUOUS = ['x', 'y', 'size', 'alpha']
    DISCRETE = ['color', 'shape', 'marker', 'alpha', 'linestyle']

    def __init__(self, mapping, data):
        if not isinstance(data, pd.DataFrame):
            mapping, data = data, mapping

        self.data = data
        self.mapping = mapping
        self.facet = facet_null()
        self.labels = mapping  # TODO: Should allow for something else!!
        self.layers = []
        self.scales = Scales()
        # default theme is theme_gray
        self.theme = theme_gray()
        self.plot_env = EvalEnvironment.capture(1)

    def __repr__(self):
        """Print/show the plot"""
        figure = self.draw()
        # We're going to default to making the plot appear when __repr__ is
        # called.
        #figure.show() # doesn't work in ipython notebook
        plt.show()
        # TODO: We can probably get more sugary with this
        return "<ggplot: (%d)>" % self.__hash__()

    def __deepcopy__(self, memo):
        '''deepcopy support for ggplot'''
        # This is a workaround as ggplot(None, None) does not really work :-(
        class _empty(object):
            pass
        result = _empty()
        result.__class__ = self.__class__
        # don't make a deepcopy of data, or plot_env
        shallow = {'data', 'plot_env'}
        for key, item in self.__dict__.items():
            if key in shallow:
                result.__dict__[key] = self.__dict__[key]
                continue
            result.__dict__[key] = deepcopy(self.__dict__[key], memo)

        return result

    def draw(self):
        plt.close("all")
        with gg_context(theme=self.theme):
            data, panel, plot = self.plot_build()
            fig, axs = plt.subplots(plot.facet.nrow,
                                    plot.facet.ncol,
                                    sharex=False,
                                    sharey=False)
            # TODO: spaces should depend on the axis horizontal
            # and vertical lengths since the values are in
            # transAxes dimensions
            plt.subplots_adjust(wspace=.05, hspace=.05)
            axs = np.atleast_2d(axs)
            axs = [ax for row in axs for ax in row]

            # ax - axes for a particular panel
            # pnl - a panel (facet)
            for ax, (_, pnl) in zip(axs, panel.layout.iterrows()):
                panel_idx = pnl['PANEL'] - 1
                xy_scales = {'x': panel.x_scales[pnl['SCALE_X'] - 1],
                             'y': panel.y_scales[pnl['SCALE_Y'] - 1]}

                # Plot all data for each layer
                for zorder, (l, d) in enumerate(
                        zip(plot.layers, data), start=1):
                    bool_idx = (d['PANEL'] == pnl['PANEL'])
                    l.plot(d[bool_idx], xy_scales, ax, zorder)

                # panel limits
                ax.set_xlim(panel.ranges[panel_idx]['x'])
                ax.set_ylim(panel.ranges[panel_idx]['y'])

                # panel breaks
                set_breaks(panel, panel_idx, ax)

                # panel labels
                set_labels(panel, panel_idx, ax)

                # xaxis, yaxis stuff
                set_axis_attributes(plot, pnl, ax)

                # TODO: Need to find a better place for this
                # theme_apply turns on the minor grid only to turn
                # it off here!!!
                if isinstance(xy_scales['x'], scale_discrete):
                    ax.grid(False, which='minor', axis='x')

                if isinstance(xy_scales['y'], scale_discrete):
                    ax.grid(False, which='minor', axis='y')

                # draw facet labels
                if isinstance(plot.facet, facet_grid):
                    draw_facet_label(plot, pnl, ax, fig)

            # Draw legend
            # print(panel.layout)
        return plt.gcf()

    def add_to_legend(self, legend_type, legend_dict, scale_type="discrete"):
        """Adds the the specified legend to the legend

        Parameters
        ----------
        legend_type : str
            type of legend, one of "color", "linestyle", "marker", "size"
        legend_dict : dict
            a dictionary of {visual_value: legend_key} where visual_value
            is color value, line style, marker character, or size value;
            and legend_key is a quantile.
        scale_type : str
            either "discrete" (default) or "continuous"; usually only color
            needs to specify which kind of legend should be drawn, all
            other scales will get a discrete scale.
        """
        # scale_type is up to now unused
        # TODO: what happens if we add a second color mapping?
        # Currently the color mapping in the legend is overwritten.
        # What does ggplot do in such a case?
        if legend_type in self.legend:
            pass
            #msg = "Adding a secondary mapping of {0} is unsupported and no legend for this mapping is added.\n"
            #sys.stderr.write(msg.format(str(legend_type)))
        self.legend[legend_type] = legend_dict

    def plot_build(self):
        """
        Build ggplot for rendering.

        This function takes the plot object, and performs all steps
        necessary to produce an object that can be rendered.

        Returns
        -------
        data : list
            dataframes, one for each layer
        panel : panel
            panel object with all the information required
            for ploting
        plot : ggplot
            A copy of the ggplot object
        """
        # TODO:
        # - copy the plot_data in here and give each layer
        #   a separate copy. Currently this is happening in
        #   facet.map_layout
        # - Do not alter the user dataframe, create a copy
        #   that keeps only the columns mapped to aesthetics.
        #   Currently, this space conservation is happening
        #   in compute_aesthetics. Can we get this evaled
        #   dataframe before train_layout!!!
        if not self.layers:
            raise GgplotError('No layers in plot')

        plot = deepcopy(self)

        layers = self.layers
        layer_data = [x.data for x in self.layers]
        all_data = [plot.data] + layer_data
        scales = plot.scales

        def dlapply(f):
            """
            Call the function f with the dataframe and layer
            object as arguments.%s
            """
            out = [None] * len(data)
            for i in range(len(data)):
                out[i] = f(data[i], layers[i])
            return out

        # Initialise panels, add extra data for margins & missing facetting
        # variables, and add on a PANEL variable to data
        panel = Panel()
        panel.layout = plot.facet.train_layout(all_data)
        data = plot.facet.map_layout(panel.layout, layer_data, plot.data)

        # Compute aesthetics to produce data with generalised variable names
        data = dlapply(lambda d, l: l.compute_aesthetics(d, plot))
        data = list(map(add_group, data))

        # Transform all scales

        # Map and train positions so that statistics have access to ranges
        # and all positions are numeric
        scale_x = lambda: scales.get_scales('x')
        scale_y = lambda: scales.get_scales('y')

        panel.train_position(data, scale_x(), scale_y())
        data = panel.map_position(data, scale_x(), scale_y())

        # Apply and map statistics
        data = panel.calculate_stats(data, layers)
        data = dlapply(lambda d, l: l.map_statistic(d, plot))
        # data = list(map(order_groups, data)) # !!! look into this

        # Make sure missing (but required) aesthetics are added
        scales_add_missing(plot, ('x', 'y'))

        # Reparameterise geoms from (e.g.) y and width to ymin and ymax
        data = dlapply(lambda d, l: l.reparameterise(d))

        # Apply position adjustments
        data = dlapply(lambda d, l: l.adjust_position(d))

        # Reset position scales, then re-train and map.  This ensures
        # that facets have control over the range of a plot:
        #   - is it generated from what's displayed, or
        #   - does it include the range of underlying data
        panel.reset_scales()
        panel.train_position(data, scale_x(), scale_y())
        data = panel.map_position(data, scale_x(), scale_y())

        # Train and map non-position scales
        npscales = scales.non_position_scales()
        if len(npscales):
            map(lambda d: npscales.train_df(d), data)
            data = list(map(lambda d: npscales.map_df(d), data))

        panel.train_ranges()
        return data, panel, plot


def set_axis_attributes(plot, pnl, ax):
    # Figure out the parameters that should be set
    # in the theme
    params = {'xaxis': [], 'yaxis': []}

    if pnl['ROW'] == plot.facet.nrow:
        params['xaxis'] += [('set_ticks_position', 'bottom')]
    else:
        params['xaxis'] += [('set_ticks_position', 'none'),
                            ('set_ticklabels', [])]

    if pnl['COL'] == 1:
        params['yaxis'] += [('set_ticks_position', 'left')]
    else:
        params['yaxis'] += [('set_ticks_position', 'none'),
                            ('set_ticklabels', [])]

    plot.theme.post_plot_callback(ax, params)


def set_breaks(panel, idx, ax):
    xbreaks = panel.ranges[idx]['x_breaks']
    ybreaks = panel.ranges[idx]['y_breaks']

    if not is_waive(xbreaks):
        ax.set_xticks(xbreaks)

    if not is_waive(ybreaks):
        ax.set_yticks(ybreaks)


def set_labels(panel, idx, ax):
    xlabels = panel.ranges[idx]['x_labels']
    ylabels = panel.ranges[idx]['y_labels']

    if not is_waive(xlabels):
        ax.set_xticklabels(xlabels)

    if not is_waive(ylabels):
        ax.set_yticklabels(ylabels)


# Should probably be in themes
def draw_facet_label(plot, pnl, ax, fig):
    if pnl['ROW'] != 1 and pnl['COL'] != plot.facet.ncol:
        return

    # The facet labels are placed onto the figure using
    # transAxes dimensions. The line height and line
    # width are mapped to the same [0, 1] range
    # i.e (pts) * (inches / pts) * (1 / inches)
    # plus a padding factor of 1.65
    bbox = ax.get_window_extent().transformed(
        fig.dpi_scale_trans.inverted())
    w, h = bbox.width, bbox.height  # in inches
    oneh = 1 / (fig.dpi * w)  # 1pt horizontal in transAxes
    onev = 1 / (fig.dpi * h)  # 1pt vertical in transAxes
    w = mpl.rcParams['font.size'] * 1.65 * oneh
    h = mpl.rcParams['font.size'] * 1.65 * onev

    # Need to use theme (element_rect) for the colors
    # top labels
    if pnl['ROW'] == 1:
        facet_var = plot.facet.cols[0]
        ax.text(0.5, 1+onev, pnl[facet_var],
                bbox=dict(
                    xy=(0, 1+onev),
                    facecolor='lightgrey',
                    edgecolor='lightgrey',
                    height=h,
                    width=1,
                    transform=ax.transAxes),
                transform=ax.transAxes,
                fontdict=dict(verticalalignment="bottom",
                              horizontalalignment='left')
                )

    # right labels
    if pnl['COL'] == plot.facet.ncol:
        facet_var = plot.facet.rows[0]
        ax.text(1+oneh, 0.5, pnl[facet_var],
                bbox=dict(
                    xy=(1+oneh, 0),
                    facecolor='lightgrey',
                    edgecolor='lightgrey',
                    height=1,
                    width=w,
                    transform=ax.transAxes),
                transform=ax.transAxes,
                fontdict=dict(rotation=-90,
                              verticalalignment="center",
                              horizontalalignment='left')
                )


def _is_identity(x):
    if x in colors.COLORS:
        return True
    elif x in shapes.SHAPES:
        return True
    elif isinstance(x, (float, int)):
        return True
    else:
        return False

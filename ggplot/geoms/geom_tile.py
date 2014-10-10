from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pandas as pd
import numpy as np
from .geom import geom
from matplotlib.patches import Rectangle
import matplotlib.colors as colors
import matplotlib.colorbar as colorbar

class geom_tile(geom):

    DEFAULT_AES = {}
    REQUIRED_AES = {'x', 'y', 'fill'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _aes_renames = {}
    _units = set()

    def _plot_unit(self, pinfo, ax):
        x = pinfo.pop('x')
        y = pinfo.pop('y')
        fill = pinfo.pop('fill')

        # TODO: Fix this hack!
        # Currently, if the fill is specified in the ggplot aes wrapper, ggplot
        # will assign colors without regard to the fill values. This is okay for
        # categorical maps but not heatmaps. At this stage in the pipeline the
        # geom can't recover the original values.
        #
        # However, if the fill is specified in the geom_tile aes wrapper, the
        # original fill values are sent unaltered, so we can make a heat map
        # with the values.

        # Was the fill specified in geom wrapper only? (i.e. not in ggplot)
        if 'fill' in self.aes_unique_to_geom:
            # Determine if there are non-numeric values.
            if False in [isinstance(v, (int, long, float, complex)) for v in set(fill)]:
                # No need to handle this case. Instruct the user to put categorical
                # values in the ggplot wrapper.
                raise Exception('For categorical fill values specify fill in the ggplot aes instead of the geom_tile aes.')

            # All values are numeric so determine fill using colormap.
            else:
                fill_min  = np.min(fill)
                fill_max  = np.max(fill)

                if np.isnan(fill_min):
                    raise Exception('Fill values cannot contain NaN values.')

                fill_rng  = float(fill_max - fill_min)
                fill_vals = (fill - fill_min) / fill_rng

                cmap = self.gg.colormap(fill_vals.tolist())
                fill      = [colors.rgb2hex(c) for c in cmap[::, :3]]

        df = pd.DataFrame(
            {'x': x, 'y': y, 'fill': fill}).set_index(['x', 'y']).unstack(0)

        # Setup axes.
        x_ticks   = range(2*len(set(x)) + 1)
        y_ticks   = range(2*len(set(y)) + 1)

        x_indices = sorted(set(x))
        y_indices = sorted(set(y))

        # Setup box plotting parameters.
        x_start   = 0
        y_start   = 0
        x_step    = 2
        y_step    = 2

        # Plot grid.
        on_y = y_start
        for yi in xrange(len(y_indices)):
            on_x = x_start
            for xi in xrange(len(x_indices)):
                color = df.iloc[yi,xi]
                if not isinstance(color, float):
                    ax.add_patch(Rectangle((on_x, on_y), x_step, y_step, facecolor=color))
                on_x += x_step
            on_y += y_step

        # Draw the colorbar scale if drawing a heat map.
        if 'cmap' in locals():
            norm = colors.Normalize(vmin = fill_min, vmax = fill_max)
            cax, kw = colorbar.make_axes(ax)
            cax.hold(True)
            colorbar.ColorbarBase(cax, cmap = self.gg.colormap, norm = norm)

        # Set axis labels and ticks.
        x_labels = ['']*(len(x_indices)+1)
        for i,v in enumerate(x_indices): x_labels.insert(2*i+1, v)
        y_labels = ['']*(len(y_indices)+1)
        for i,v in enumerate(y_indices): y_labels.insert(2*i+1, v)

        ax.set_xticklabels(x_labels)
        ax.set_xticks(x_ticks)
        ax.set_yticklabels(y_labels)
        ax.set_yticks(y_ticks)

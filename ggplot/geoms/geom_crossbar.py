from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import matplotlib.lines as mlines
from matplotlib.patches import Rectangle

from ..scales.utils import resolution
from ..utils.exceptions import gg_warn
from ..utils import to_rgba
from .geom import geom
from .geom_polygon import geom_polygon
from .geom_segment import geom_segment


class geom_crossbar(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'fill': None,
                   'linetype': 'solid', 'size': 1.5}
    REQUIRED_AES = {'x', 'y', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'width': 0.5, 'fatten': 2}

    def setup_data(self, data):
        if 'width' not in data:
            if self.params['width']:
                data['width'] = self.params['width']
            else:
                data['width'] = resolution(data['x'], False) * 0.9

        data['xmin'] = data['x'] - data['width']/2
        data['xmax'] = data['x'] + data['width']/2
        del data['width']
        return data

    @staticmethod
    def draw_group(pinfo, panel_scales, coord, ax, **params):
        y = pinfo['y']
        xmin = np.array(pinfo['xmin'])
        xmax = np.array(pinfo['xmax'])
        ymin = np.array(pinfo['ymin'])
        ymax = np.array(pinfo['ymax'])
        notchwidth = pinfo.get('notchwidth')
        ynotchupper = pinfo.get('ynotchupper')
        ynotchlower = pinfo.get('ynotchlower')

        keys = ['alpha', 'color', 'fill', 'size',
                'linetype', 'zorder']

        def copy_keys(d):
            for k in keys:
                d[k] = pinfo[k]

        def flat(*args):
            """Flatten list-likes"""
            return [i for arg in args for i in arg]

        middle = {'x': xmin,
                  'y': y,
                  'xend': xmax,
                  'yend': y,
                  'group': pinfo['group']}
        copy_keys(middle)
        middle['size'] = np.asarray(middle['size'])*params['fatten'],

        has_notch = ynotchlower is not None and ynotchupper is not None
        if has_notch:  # 10 points + 1 closing
            ynotchlower = np.array(ynotchlower)
            ynotchupper = np.array(ynotchupper)
            if (any(ynotchlower < ymin) or any(ynotchupper > ymax)):
                msg = ("Notch went outside hinges."
                       " Try setting notch=False.")
                gg_warn(msg)

            notchindent = (1 - notchwidth) * (xmax-xmin)/2

            middle['x'] = np.array(middle['x']) + notchindent
            middle['xend'] = np.array(middle['xend']) - notchindent
            box = {
                'x': flat(xmin, xmin, xmin+notchindent, xmin, xmin,
                          xmax, xmax, xmax-notchindent, xmax, xmax,
                          xmin),
                'y': flat(ymax, ynotchupper, y, ynotchlower, ymin,
                          ymin, ynotchlower, y, ynotchupper, ymax,
                          ymax),
                'group': np.tile(np.arange(1, len(pinfo['group'])+1), 11)}
        else:
            # No notch, 4 points + 1 closing
            box = {
                'x': flat(xmin, xmin, xmax, xmax, xmin),
                'y': flat(ymax, ymax, ymax, ymin, ymin),
                'group': np.tile(np.arange(1, len(pinfo['group'])+1), 5)}
        copy_keys(box)

        geom_polygon.draw_group(box, panel_scales, coord, ax, **params)
        geom_segment.draw_group(middle, panel_scales, coord, ax, **params)

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw a rectangle with a horizontal strike in the box

        Parameters
        ----------
        data : dataframe
        da : DrawingArea
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        # background
        facecolor = to_rgba(data['fill'], data['alpha'])
        if facecolor is None:
            facecolor = 'none'

        bg = Rectangle((da.width*.125, da.height*.25),
                       width=da.width*.75,
                       height=da.height*.5,
                       linewidth=data['size'],
                       facecolor=facecolor,
                       edgecolor=data['color'],
                       linestyle=data['linetype'],
                       capstyle='projecting',
                       antialiased=False)
        da.add_artist(bg)

        strike = mlines.Line2D([da.width*.125, da.width*.875],
                               [da.height*.5, da.height*.5],
                               linestyle=data['linetype'],
                               linewidth=data['size'],
                               color=data['color'])
        da.add_artist(strike)
        return da

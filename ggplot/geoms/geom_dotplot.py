from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import matplotlib.collections as mcoll
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

from ..utils import groupby_apply, make_rgba
from ..utils.exceptions import gg_warn
from ..scales.utils import resolution
from .geom import geom


class geom_dotplot(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'fill': 'black'}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'bindot', 'position': 'identity',
                      'stackdir': 'up', 'stackratio': 1,
                      'dotsize': 1, 'stackgroups': False}

    _extra_requires = {'width'}

    @classmethod
    def _verify(cls, **params):
        """
        Issue warnings when parameters don't make sense
        """
        if params['position'] == 'stack':
            gg_warn("position='stack' doesn't work properly with "
                    "geom_dotplot. Use stackgroups=True instead.")
        if (params['stackgroups'] and
                params['method'] == 'dotdensity' and
                params['binpositions'] == 'bygroup'):
            gg_warn("geom_dotplot called with stackgroups=TRUE and "
                    "method='dotdensity'. You probably want to set "
                    "binpositions='all'")

    def reparameterise(self, data):
        gp = self.params
        sp = self._stat.params

        if 'width' not in data:
            if sp['width']:
                data['width'] = sp['width']
            else:
                data['width'] = resolution(data['x'], False) * 0.9

        # Set up the stacking function and range
        if gp['stackdir'] in (None, 'up'):
            def stackdots(a):
                return a - .5
            stackaxismin = 0
            stackaxismax = 1
        elif gp['stackdir'] == 'down':
            def stackdots(a):
                return -a + .5
            stackaxismin = -1
            stackaxismax = 0
        elif gp['stackdir'] == 'center':
            def stackdots(a):
                return a - 1 - np.max(a-1)/2
            stackaxismin = -.5
            stackaxismax = .5
        elif gp['stackdir'] == 'centerwhole':
            def stackdots(a):
                return a - 1 - np.floor(np.max(a-1)/2)
            stackaxismin = -.5
            stackaxismax = .5

        # Fill the bins: at a given x (or y),
        # if count=3, make 3 entries at that x
        idx = [i for i, c in enumerate(data['count'])
               for j in range(int(c))]
        data = data.iloc[idx]
        data.reset_index(inplace=True, drop=True)
        data.is_copy = None
        # Next part will set the position of each dot within each stack
        # If stackgroups=TRUE, split only on x (or y) and panel;
        # if not stacking, also split by group
        groupvars = [sp['binaxis'], 'PANEL']
        if not gp['stackgroups']:
            groupvars.append('group')

        # Within each x, or x+group, set countidx=1,2,3,
        # and set stackpos according to stack function
        def func(df):
            df['countidx'] = range(1, len(df)+1)
            df['stackpos'] = stackdots(df['countidx'])
            return df

        # Within each x, or x+group, set countidx=1,2,3, and set
        # stackpos according to stack function
        data = groupby_apply(data, groupvars, func)

        # Set the bounding boxes for the dots
        if sp['binaxis'] == 'x':
            # ymin, ymax, xmin, and xmax define the bounding
            # rectangle for each stack. Can't do bounding box per dot,
            # because y position isn't real.
            # After position code is rewritten, each dot should have
            # its own bounding box.
            data['xmin'] = data['x'] - data['binwidth']/2
            data['xmax'] = data['x'] + data['binwidth']/2
            data['ymin'] = stackaxismin
            data['ymax'] = stackaxismax
            data['y'] = 0
        elif sp['binaxis'] == 'y':
            # ymin, ymax, xmin, and xmax define the bounding
            # rectangle for each stack. Can't do bounding box per dot,
            # because x position isn't real.
            # xmin and xmax aren't really the x bounds. They're just
            # set to the standard x +- width/2 so that dot clusters
            # can be dodged like other geoms.
            # After position code is rewritten, each dot should have
            # its own bounding box.
            def func(df):
                df['ymin'] = df['y'].min() - data['binwidth'][0]/2
                df['ymax'] = df['y'].max() + data['binwidth'][0]/2
                return df
            data = groupby_apply(data, 'group', func)
            data['xmin'] = data['x'] + data['width'] * stackaxismin
            data['xmax'] = data['x'] + data['width'] * stackaxismax

        return data

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **params):
        geom_dotplot._verify(**params)

        pinfo['fill'] = make_rgba(pinfo['fill'],
                                  pinfo['alpha'])
        x = np.asarray(pinfo['x'])
        y = np.asarray(pinfo['y'])
        # For perfect circles the width/height of the circle(ellipse)
        # should factor in the figure dimensions
        fw, fh = ax.figure.get_figwidth(), ax.figure.get_figheight()
        factor = ((fw/fh) *
                  np.ptp(scales['y_range'])/np.ptp(scales['x_range']))
        size = pinfo['binwidth'][0] * params['dotsize']
        offsets = np.asarray(pinfo['stackpos']) * params['stackratio']

        if params['binaxis'] == 'x':
            width, height = size, size*factor
            xpos, ypos = x, y + height*offsets
        elif params['binaxis'] == 'y':
            width, height = size/factor, size
            xpos, ypos = x + width*offsets, y

        circles = []
        for xy in zip(xpos, ypos):
            patch = mpatches.Ellipse(xy, width=width, height=height)
            circles.append(patch)
        coll = mcoll.PatchCollection(circles,
                                     edgecolors=pinfo['color'],
                                     facecolors=pinfo['fill'])
        ax.add_collection(coll)

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw a point in the box

        Parameters
        ----------
        data : dataframe
        params : dict
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        key = mlines.Line2D([0.5*da.width],
                            [0.5*da.height],
                            alpha=data['alpha'],
                            marker='o',
                            markersize=da.width/2,
                            markerfacecolor=data['fill'],
                            markeredgecolor=data['color'])
        da.add_artist(key)
        return da

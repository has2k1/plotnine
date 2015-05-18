from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from collections import Counter

import numpy as np
import pandas as pd
import matplotlib.collections as mcoll
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.path as mpath

from ..utils.exceptions import gg_warning
from ..utils import make_color_tuples, make_iterable_ntimes
from .geom import geom


class geom_path(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'linetype': 'solid',
                   'size': 1.0}

    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'lineend': 'butt', 'linejoin': 'round',
                      'arrow': None}
    guide_geom = 'path'

    _aes_renames = {'color': 'edgecolor', 'size': 'linewidth',
                    'linetype': 'linestyle'}

    def draw_groups(self, data, scales, coordinates, ax, **kwargs):
        if not any(data['group'].duplicated()):
            msg = ("geom_path: Each group consist of only one",
                   "observation. Do you need to adjust the",
                   "group aesthetic?")
            gg_warning(msg)

        # dataframe mergesort is stable, we rely on that here
        data.sort(columns=['group'], kind='mergesort', inplace=True)
        data.reset_index(drop=True, inplace=True)

        # drop lines with less than two points
        c = Counter(data['group'])
        counts = np.array([c[v] for v in data['group']])
        data = data[counts >= 2]
        data.is_copy = None

        if len(data) < 2:
            return

        # When the parameters of the path are not constant
        # with in the group, then the lines that make the paths
        # can be drawn as separate segments
        cols = {'color', 'size', 'linetype', 'alpha', 'group'}
        cols = cols & set(data.columns)
        df = data.drop_duplicates(cols)
        constant = len(df) == len(data['group'].unique())
        kwargs['constant'] = constant

        if not constant:
            pinfos = self._make_pinfos(data, kwargs)
            assert len(pinfos) == 1
            self.draw(pinfos[0], scales, coordinates, ax, **kwargs)
        else:
            geom.draw_groups(self, data, scales, coordinates, ax, **kwargs)

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **kwargs):
        try:
            if kwargs['linejoin'] == 'mitre':
                kwargs['linejoin'] = 'miter'
        except KeyError:
            pass

        try:
            if kwargs['lineend'] == 'square':
                kwargs['lineend'] = 'projecting'
        except KeyError:
            pass

        pinfo['edgecolor'] = make_color_tuples(pinfo['edgecolor'],
                                               pinfo['alpha'])

        constant = kwargs.pop('constant', False)
        if not constant:
            _draw_segments(pinfo, ax, **kwargs)
        else:
            _draw_lines(pinfo, ax, **kwargs)

        try:
            kwargs['arrow'].draw(
                pinfo, scales, coordinates, ax, constant=constant)
        except AttributeError:
            # Arrow is None
            pass
        except KeyError:
            # some geoms draw with this method but they
            # do not know about the arrow parameter
            pass

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw a horizontal line in the box

        Parameters
        ----------
        data : dataframe
        da : DrawingArea
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        x = [0, da.width]
        y = [0.5 * da.height] * 2
        key = mlines.Line2D(x,
                            y,
                            alpha=data['alpha'],
                            linestyle=data['linestyle'],
                            linewidth=data['linewidth'],
                            color=data['edgecolor'],
                            solid_capstyle='butt',
                            antialiased=False)
        da.add_artist(key)
        return da


class arrow(object):
    def __init__(self, angle=30, length=0.25,
                 ends='last', type='open'):
        """
        Define arrow (actually an arrowhead)

        Parameters:
        -----------
        angle : int | float
            angle in degrees between the tail a
            single edge.
        length : int | float
            of the edge in "inches"
        ends : 'last' | 'first' | 'both'
            At which end of the line to draw the
            arrowhead
        type : 'open' | 'closed'
            When it is closed, it is also filled
        """
        self.angle = angle
        self.length = length
        self.ends = ends
        self.type = type
        self._cache = {}

    def _init(self, scales, coordinates, ax):
        """
        Calculate and cache the arrow edge lengths along both axes
        """
        try:
            if scales is self._cache['scales'] and ax is self._cache['ax']:
                return
        except KeyError:
            pass
        # A length for each dimension, makes the edges of
        # all arrowheads to be drawn have the same length.
        # i.e a perfect isosceles arrowhead
        # The rotation angle calculation is also scaled with
        # these values
        fig = ax.get_figure()
        width, height = fig.get_size_inches()
        ranges = coordinates.range(scales)
        width_ = np.ptp(ranges.x)
        height_ = np.ptp(ranges.y)

        self._cache['scales'] = scales
        self._cache['ax'] = ax
        self._cache['lx'] = self.length * width_/width
        self._cache['ly'] = self.length * height_/height

    def draw(self, pinfo, scales, coordinates, ax, constant=True):
        """
        Draw arrows at the end(s) of the lines

        Parameters
        ----------
        pinfo : dict
            plot information as required by geom.draw
        scales : dict
            x scale, y scale
        ax : axes
            On which to draw
        constant: bool
            If the path attributes vary along the way. If false,
            the arrows are per segment of the path
        """
        self._init(scales, coordinates, ax)
        Path = mpath.Path

        first = self.ends in ('first', 'both')
        last = self.ends in ('last', 'both')
        if self.type == 'open':
            pinfo['facecolor'] = 'none'
        else:
            pinfo['facecolor'] = pinfo['edgecolor']

        # Create reusable lists of vertices and codes
        paths = []
        num = first + last         # No. of arrowheads per line
        verts = [None] * 3 * num   # arrowhead path has 3 vertices
        verts.append((0, 0))       # Dummy vertex for the STOP code
        # codes list remains the same after initialization
        codes = [Path.MOVETO, Path.LINETO, Path.LINETO] * num
        codes.append(Path.STOP)
        # Slices into the vertices list
        slc1 = slice(0, 3)
        slc2 = slice(3, 6) if first else slc1

        def get_param(param, indices):
            out = pinfo[param]
            try:
                if len(out) == len(pinfo['x']):
                    out = [pinfo[param][i] for i in indices]
            except TypeError:
                pass
            return out

        if not constant:
            indices = []
            df = pd.DataFrame({'group': pinfo['group']})
            for _, _df in df.groupby('group'):
                idx = _df.index.tolist()
                indices[:-1] += idx  # One line from two points
                for i1, i2 in zip(idx[:-1], idx[1:]):
                    x1, x2 = pinfo['x'][i1], pinfo['x'][i2]
                    y1, y2 = pinfo['y'][i1], pinfo['y'][i2]
                    if first:
                        verts[slc1] = self._vertices(x1, x2, y1, y2)
                    if last:
                        verts[slc2] = self._vertices(x2, x1, y2, y1)
                    paths.append(Path(verts, codes))
            edgecolor = get_param('edgecolor', indices)
            facecolor = get_param('facecolor', indices)
            linewidth = get_param('linewidth', indices)
            linestyle = get_param('linestyle', indices)
            coll = mcoll.PathCollection(paths,
                                        edgecolor=edgecolor,
                                        facecolor=facecolor,
                                        linewidth=linewidth,
                                        linestyle=linestyle)

            ax.add_collection(coll)
        else:
            if first:
                x1, x2 = pinfo['x'][0:2]
                y1, y2 = pinfo['y'][0:2]
                verts[slc1] = self._vertices(x1, x2, y1, y2)
            if last:
                x1, x2 = pinfo['x'][-2:]
                y1, y2 = pinfo['y'][-2:]
                verts[slc2] = self._vertices(x2, x1, y2, y1)
            patch = mpatches.PathPatch(Path(verts, codes),
                                       edgecolor=pinfo['edgecolor'],
                                       facecolor=pinfo['facecolor'],
                                       linewidth=pinfo['linewidth'],
                                       linestyle=pinfo['linestyle'],
                                       joinstyle='round',
                                       capstyle='butt')
            ax.add_artist(patch)

    def _vertices(self, x1, x2, y1, y2):
        """
        Return the vertices that define the arrowhead

        The line is assumed to run from (x1, y1) to
        (x2, y2) and the vertices returned put the
        arrowhead at (x1, y1)
        """
        lx, ly = self._cache['lx'], self._cache['ly']
        a = self.angle * np.pi / 180
        yc = y2 - y1
        xc = x2 - x1
        rot = np.arctan2(yc/ly, xc/lx)

        v1x = x1 + lx * np.cos(rot + a)
        v1y = y1 + ly * np.sin(rot + a)
        v2x = x1 + lx * np.cos(rot - a)
        v2y = y1 + ly * np.sin(rot - a)

        return [(v1x, v1y), (x1, y1), (v2x, v2y)]


def _draw_segments(pinfo, ax, **kwargs):
    """
    Draw independent line segments between all the
    points
    """
    # All we do is line-up all the points in a group
    # into segments, all in a single list.
    # Along the way the other parameters are put in
    # sequences accordingly
    group = make_iterable_ntimes(pinfo['group'], len(pinfo['x']))
    df = pd.DataFrame({'group': group})

    def get_param(param, indices):
        """
        Return values for a given parameter
        """
        out = pinfo[param]
        try:
            if len(out) == len(pinfo['x']):
                out = [pinfo[param][i] for i in indices]
        except TypeError:
            pass
        return out

    indices = []
    segments = []
    for _, _df in df.groupby('group'):
        idx = _df.index.tolist()
        indices[:-1] += idx  # One line from two points
        for i1, i2 in zip(idx[:-1], idx[1:]):
            x1, x2 = pinfo['x'][i1], pinfo['x'][i2]
            y1, y2 = pinfo['y'][i1], pinfo['y'][i2]
            segments.append(((x1, y1), (x2, y2)))

    edgecolor = get_param('edgecolor', indices)
    linewidth = get_param('linewidth', indices)
    linestyle = get_param('linestyle', indices)
    coll = mcoll.LineCollection(segments,
                                edgecolor=edgecolor,
                                linewidth=linewidth,
                                linestyle=linestyle,
                                zorder=pinfo['zorder'])
    ax.add_collection(coll)


def _draw_lines(pinfo, ax, **kwargs):
    """
    Draw a path with the same characteristics from the
    first point to the last point
    """
    joinstyle = kwargs.get('linejoin', 'miter')
    capstyle = kwargs.get('lineend', 'butt')
    d = {}
    if pinfo['linestyle'] == 'solid':
        d['solid_joinstyle'] = joinstyle
        d['solid_capstyle'] = capstyle
    elif pinfo['linestyle'] == 'dashed':
        d['dash_joinstyle'] = joinstyle
        d['dash_capstyle'] = capstyle

    lines = mlines.Line2D(pinfo['x'],
                          pinfo['y'],
                          color=pinfo['edgecolor'],
                          linewidth=pinfo['linewidth'],
                          linestyle=pinfo['linestyle'],
                          zorder=pinfo['zorder'],
                          **d)
    pinfo.update(d)
    ax.add_artist(lines)

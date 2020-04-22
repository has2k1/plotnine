from collections import Counter
from warnings import warn
from contextlib import suppress

import numpy as np
import matplotlib.collections as mcoll
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.path as mpath

from ..exceptions import PlotnineWarning
from ..doctools import document
from ..utils import to_rgba, make_line_segments
from ..utils import SIZE_FACTOR, match
from .geom import geom


@document
class geom_path(geom):
    """
    Connected points

    {usage}

    Parameters
    ----------
    {common_parameters}
    lineend : str (default: butt)
        Line end style, of of *butt*, *round* or *projecting.*
        This option is applied for solid linetypes.
    linejoin : str (default: round)
        Line join style, one of *round*, *miter* or *bevel*.
        This option is applied for solid linetypes.
    arrow : plotnine.geoms.geom_path.arrow (default: None)
        Arrow specification. Default is no arrow.

    See Also
    --------
    plotnine.geoms.arrow : for adding arrowhead(s) to paths.
    """
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'linetype': 'solid',
                   'size': 0.5}

    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False,
                      'lineend': 'butt', 'linejoin': 'round',
                      'arrow': None}

    def handle_na(self, data):
        def keep(x):
            # first non-missing to last non-missing
            first = match([False], x, nomatch=1, start=0)[0]
            last = len(x) - match([False], x[::-1], nomatch=1, start=0)[0]
            bool_idx = np.hstack([np.repeat(False, first),
                                  np.repeat(True, last-first),
                                  np.repeat(False, len(x)-last)])
            return bool_idx

        # Get indices where any row for the select aesthetics has
        # NaNs at the beginning or the end. Those we drop
        bool_idx = (data[['x', 'y', 'size', 'color', 'linetype']]
                    .isnull()             # Missing
                    .apply(keep, axis=0))  # Beginning or the End
        bool_idx = np.all(bool_idx, axis=1)  # Across the aesthetics

        # return data
        n1 = len(data)
        data = data[bool_idx]
        data.reset_index(drop=True, inplace=True)
        n2 = len(data)

        if (n2 != n1 and not self.params['na_rm']):
            msg = "geom_path: Removed {} rows containing missing values."
            warn(msg.format(n1-n2), PlotnineWarning)

        return data

    def draw_panel(self, data, panel_params, coord, ax, **params):
        if not any(data['group'].duplicated()):
            warn("geom_path: Each group consist of only one "
                 "observation. Do you need to adjust the "
                 "group aesthetic?", PlotnineWarning)

        # drop lines with less than two points
        c = Counter(data['group'])
        counts = np.array([c[v] for v in data['group']])
        data = data[counts >= 2]

        if len(data) < 2:
            return

        # dataframe mergesort is stable, we rely on that here
        data = data.sort_values('group', kind='mergesort')
        data.reset_index(drop=True, inplace=True)

        # When the parameters of the path are not constant
        # with in the group, then the lines that make the paths
        # can be drawn as separate segments
        cols = {'color', 'size', 'linetype', 'alpha', 'group'}
        cols = cols & set(data.columns)
        df = data.drop_duplicates(cols)
        constant = len(df) == data['group'].nunique()
        params['constant'] = constant

        if not constant:
            self.draw_group(data, panel_params, coord, ax, **params)
        else:
            for _, gdata in data.groupby('group'):
                gdata.reset_index(inplace=True, drop=True)
                self.draw_group(gdata, panel_params, coord, ax, **params)

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        data = coord.transform(data, panel_params, munch=True)
        data['size'] *= SIZE_FACTOR
        constant = params.pop('constant', data['group'].nunique() == 1)

        if not constant:
            _draw_segments(data, ax, **params)
        else:
            _draw_lines(data, ax, **params)

        if 'arrow' in params and params['arrow']:
            params['arrow'].draw(
                data, panel_params, coord,
                ax, zorder=params['zorder'], constant=constant)

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
        data['size'] *= SIZE_FACTOR
        x = [0, da.width]
        y = [0.5 * da.height] * 2
        key = mlines.Line2D(x,
                            y,
                            alpha=data['alpha'],
                            linestyle=data['linetype'],
                            linewidth=data['size'],
                            color=data['color'],
                            solid_capstyle='butt',
                            antialiased=False)
        da.add_artist(key)
        return da


class arrow:
    """
    Define arrow (actually an arrowhead)

    This is used to define arrow heads for
    :class:`.geom_path`.

    Parameters
    ----------
    angle : int | float
        angle in degrees between the tail a
        single edge.
    length : int | float
        of the edge in "inches"
    ends : str in ``['last', 'first', 'both']``
        At which end of the line to draw the
        arrowhead
    type : str in ``['open', 'closed']``
        When it is closed, it is also filled
    """

    def __init__(self, angle=30, length=0.2,
                 ends='last', type='open'):
        self.angle = angle
        self.length = length
        self.ends = ends
        self.type = type

    def draw(self, data, panel_params, coord, ax, zorder, constant=True):
        """
        Draw arrows at the end(s) of the lines

        Parameters
        ----------
        data : dict
            plot information as required by geom.draw
        scales : dict
            x scale, y scale
        ax : axes
            On which to draw
        constant: bool
            If the path attributes vary along the way. If false,
            the arrows are per segment of the path
        """
        first = self.ends in ('first', 'both')
        last = self.ends in ('last', 'both')

        data = data.sort_values('group', kind='mergesort')
        data['color'] = to_rgba(data['color'], data['alpha'])

        if self.type == 'open':
            data['facecolor'] = 'none'
        else:
            data['facecolor'] = data['color']

        if not constant:
            # Get segments/points (x1, y1) -> (x2, y2)
            # for which to calculate the arrow heads
            idx1, idx2 = [], []
            for _, df in data.groupby('group'):
                idx1.extend(df.index[:-1])
                idx2.extend(df.index[1:])

            d = dict(
                zorder=zorder,
                edgecolor=data.loc[idx1, 'color'],
                facecolor=data.loc[idx1, 'facecolor'],
                linewidth=data.loc[idx1, 'size'],
                linestyle=data.loc[idx1, 'linetype'])

            x1 = data.loc[idx1, 'x'].values
            y1 = data.loc[idx1, 'y'].values
            x2 = data.loc[idx2, 'x'].values
            y2 = data.loc[idx2, 'y'].values

            if first:
                paths = self.get_paths(x1, y1, x2, y2,
                                       panel_params, coord, ax)
                coll = mcoll.PathCollection(paths, **d)
                ax.add_collection(coll)
            if last:
                x1, y1, x2, y2 = x2, y2, x1, y1
                paths = self.get_paths(x1, y1, x2, y2,
                                       panel_params, coord, ax)
                coll = mcoll.PathCollection(paths, **d)
                ax.add_collection(coll)
        else:
            d = dict(
                zorder=zorder,
                edgecolor=data['color'].iloc[0],
                facecolor=data['facecolor'].iloc[0],
                linewidth=data['size'].iloc[0],
                linestyle=data['linetype'].iloc[0],
                joinstyle='round',
                capstyle='butt')

            if first:
                x1, x2 = data['x'].iloc[0:2]
                y1, y2 = data['y'].iloc[0:2]
                x1, y1, x2, y2 = [np.array([i])
                                  for i in (x1, y1, x2, y2)]
                paths = self.get_paths(x1, y1, x2, y2,
                                       panel_params, coord, ax)
                patch = mpatches.PathPatch(paths[0], **d)
                ax.add_artist(patch)

            if last:
                x1, x2 = data['x'].iloc[-2:]
                y1, y2 = data['y'].iloc[-2:]
                x1, y1, x2, y2 = x2, y2, x1, y1
                x1, y1, x2, y2 = [np.array([i])
                                  for i in (x1, y1, x2, y2)]
                paths = self.get_paths(x1, y1, x2, y2,
                                       panel_params, coord, ax)
                patch = mpatches.PathPatch(paths[0], **d)
                ax.add_artist(patch)

    def get_paths(self, x1, y1, x2, y2, panel_params, coord, ax):
        """
        Compute paths that create the arrow heads

        Parameters
        ----------
        x1, y1, x2, y2 : array_like
            List of points that define the tails of the arrows.
            The arrow heads will be at x1, y1. If you need them
            at x2, y2 reverse the input.

        Returns
        -------
        out : list of Path
            Paths that create arrow heads
        """
        Path = mpath.Path

        # Create reusable lists of vertices and codes
        # arrowhead path has 3 vertices (Nones),
        # plus dummy vertex for the STOP code
        verts = [None, None, None,
                 (0, 0)]

        # codes list remains the same after initialization
        codes = [Path.MOVETO, Path.LINETO, Path.LINETO,
                 Path.STOP]

        # Slices into the vertices list
        slc = slice(0, 3)

        # We need the axes dimensions so that we can
        # compute scaling factors
        width, height = _axes_get_size_inches(ax)
        ranges = coord.range(panel_params)
        width_ = np.ptp(ranges.x)
        height_ = np.ptp(ranges.y)

        # scaling factors to prevent skewed arrowheads
        lx = self.length * width_/width
        ly = self.length * height_/height

        # angle in radians
        a = self.angle * np.pi / 180

        # direction of arrow head
        xdiff, ydiff = x2 - x1, y2 - y1
        rotations = np.arctan2(ydiff/ly, xdiff/lx)

        # Arrow head vertices
        v1x = x1 + lx * np.cos(rotations + a)
        v1y = y1 + ly * np.sin(rotations + a)
        v2x = x1 + lx * np.cos(rotations - a)
        v2y = y1 + ly * np.sin(rotations - a)

        # create a path for each arrow head
        paths = []
        for t in zip(v1x, v1y, x1, y1, v2x, v2y):
            verts[slc] = [t[:2], t[2:4], t[4:]]
            paths.append(Path(verts, codes))

        return paths


def _draw_segments(data, ax, **params):
    """
    Draw independent line segments between all the
    points
    """
    color = to_rgba(data['color'], data['alpha'])
    # All we do is line-up all the points in a group
    # into segments, all in a single list.
    # Along the way the other parameters are put in
    # sequences accordingly
    indices = []  # for attributes of starting point of each segment
    segments = []
    for _, df in data.groupby('group'):
        idx = df.index
        indices.extend(idx[:-1])  # One line from two points
        x = data['x'].iloc[idx]
        y = data['y'].iloc[idx]
        segments.append(make_line_segments(x, y, ispath=True))

    segments = np.vstack(segments)

    if color is None:
        edgecolor = color
    else:
        edgecolor = [color[i] for i in indices]

    linewidth = data.loc[indices, 'size']
    linestyle = data.loc[indices, 'linetype']

    coll = mcoll.LineCollection(segments,
                                edgecolor=edgecolor,
                                linewidth=linewidth,
                                linestyle=linestyle,
                                zorder=params['zorder'])
    ax.add_collection(coll)


def _draw_lines(data, ax, **params):
    """
    Draw a path with the same characteristics from the
    first point to the last point
    """
    color = to_rgba(data['color'].iloc[0], data['alpha'].iloc[0])
    join_style = _get_joinstyle(data, params)
    lines = mlines.Line2D(data['x'],
                          data['y'],
                          color=color,
                          linewidth=data['size'].iloc[0],
                          linestyle=data['linetype'].iloc[0],
                          zorder=params['zorder'],
                          **join_style)
    ax.add_artist(lines)


def _get_joinstyle(data, params):
    with suppress(KeyError):
        if params['linejoin'] == 'mitre':
            params['linejoin'] = 'miter'

    with suppress(KeyError):
        if params['lineend'] == 'square':
            params['lineend'] = 'projecting'

    joinstyle = params.get('linejoin', 'miter')
    capstyle = params.get('lineend', 'butt')
    d = {}
    if data['linetype'].iloc[0] == 'solid':
        d['solid_joinstyle'] = joinstyle
        d['solid_capstyle'] = capstyle
    elif data['linetype'].iloc[0] == 'dashed':
        d['dash_joinstyle'] = joinstyle
        d['dash_capstyle'] = capstyle
    return d


def _axes_get_size_inches(ax):
    """
    Size of axes in inches

    Parameters
    ----------
    ax : axes
        Axes

    Returns
    -------
    out : tuple[float, float]
        (width, height) of ax in inches
    """
    fig = ax.get_figure()
    bbox = ax.get_window_extent().transformed(
        fig.dpi_scale_trans.inverted()
    )
    return bbox.width, bbox.height

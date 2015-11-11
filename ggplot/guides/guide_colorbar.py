from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import hashlib

import six
import numpy as np
import pandas as pd
import matplotlib.collections as mcoll
import matplotlib.text as mtext
import matplotlib.transforms as mtransforms
from matplotlib.ticker import MaxNLocator
from matplotlib.offsetbox import (TextArea, HPacker, VPacker)
from matplotlib.offsetbox import AuxTransformBox
from matplotlib.colors import ListedColormap

from ..utils import ColoredDrawingArea
from ..utils.exceptions import gg_warn
from ..scales.utils import rescale
from ..scales.scale import scale_continuous
from .guide import guide


class guide_colorbar(guide):
    # bar
    barwidth = None
    barheight = None
    nbin = 20  # maximum number of bins
    raster = True

    # ticks
    ticks = True
    draw_ulim = True
    draw_llim = True

    # parameter
    available_aes = {'colour', 'color', 'fill'}

    def train(self, scale):
        # Do nothing if scales are inappropriate
        if set(scale.aesthetics) & {'color', 'colour', 'fill'} == 0:
            gg_warn('colorbar guide needs color or fill scales.')
            return None

        if not issubclass(scale.__class__, scale_continuous):
            gg_warn('colorbar guide needs continuous scales')
            return None

        # value = breaks (numeric) is used for determining the
        # position of ticks
        breaks = scale.scale_breaks(can_waive=False)
        breaks = np.asarray(breaks)
        breaks = breaks[~np.isnan(breaks)]

        if not len(breaks):
            return None

        self.key = pd.DataFrame({
            scale.aesthetics[0]: scale.map(breaks),
            'label': scale.scale_labels(breaks, can_waive=False),
            'value': breaks})

        if self.draw_ulim and self.draw_llim:
            prune = None
        elif not self.draw_ulim and not self.draw_llim:
            prune = 'both'
        elif not self.draw_ulim:
            prune = 'upper'
        elif not self.draw_llim:
            prune = 'lower'
        bar = MaxNLocator(self.nbin,
                          steps=[1, 2, 5, 10],
                          prune=prune).tick_values(*scale.limits)
        # discard locations in bar not in scale.limits
        bar = [x for x in bar if scale.limits[0] <= x <= scale.limits[1]]
        self.bar = pd.DataFrame({
            'color': scale.map(bar),
            'value': bar})

        labels = ' '.join(six.text_type(x) for x in self.key['label'])
        info = '\n'.join([self.title, labels,
                          ' '.join(self.bar['color'].tolist()),
                          self.__class__.__name__])
        self.hash = hashlib.md5(info.encode('utf-8')).hexdigest()
        return self

    def merge(self, other):
        """
        Simply discards the other guide
        """
        return self

    def create_geoms(self, plot):
        """
        This guide is not geom based
        """
        self.glayers = []
        return self

    def _set_defaults(self, theme):
        guide._set_defaults(self, theme)
        if self.barwidth is None:
            self.barwidth = 23
        if self.barheight is None:
            self.barheight = self.barwidth*5

    def draw(self, theme):
        """
        Draw guide

        Parameters
        ----------
        theme : theme

        Returns
        -------
        out : matplotlib.offsetbox.Offsetbox
            A drawing of this legend
        """
        obverse = slice(0, None)
        reverse = slice(None, None, -1)
        sep = 0.3 * 20  # gap between the keys, .3 lines
        width = self.barwidth
        height = self.barheight
        nbars = len(self.bar)
        length = height
        direction = self.direction
        colors = self.bar['color'].tolist()
        labels = self.key['label'].tolist()
        themeable = theme.figure._themeable

        # .5 puts the ticks in the middle of the bars when
        # raster=False. So when raster=True the ticks are
        # in between interpolation points and the matching is
        # close though not exactly right.
        _from = self.bar['value'].min(), self.bar['value'].max()
        tick_locations = rescale(self.key['value'],
                                 (.5, nbars-.5),
                                 _from) * length/nbars

        if direction == 'horizontal':
            width, height = height, width
            length = width

        if self.reverse:
            colors = colors[::-1]
            labels = labels[::-1]
            tick_locations = length - tick_locations[::-1]

        # title #
        title_box = TextArea(
            self.title, textprops=dict(color='k', weight='bold'))
        themeable['legend_title'] = title_box

        # colorbar and ticks #
        da = ColoredDrawingArea(width, height, 0, 0)
        if self.raster:
            add_interpolated_colorbar(da, colors, direction)
        else:
            add_segmented_colorbar(da, colors, direction)

        if self.ticks:
            add_ticks(da, tick_locations, direction)

        # labels #
        if self.label:
            labels_da, _themeable = create_labels(da, labels,
                                                  tick_locations,
                                                  direction)
            themeable.update(_themeable)
        else:
            labels_da = ColoredDrawingArea(0, 0)

        # colorbar + labels #
        if direction == 'vertical':
            packer, align = HPacker, 'bottom'
            align = 'center'
        else:
            packer, align = VPacker, 'right'
            align = 'center'
        slc = obverse if self.label_position == 'right' else reverse
        if self.label_position in ('right', 'bottom'):
            slc = obverse
        else:
            slc = reverse
        main_box = packer(children=[da, labels_da][slc],
                          align=align, pad=0, sep=sep)

        # title + colorbar(with labels) #
        lookup = {
            'right': (HPacker, reverse),
            'left': (HPacker, obverse),
            'bottom': (VPacker, reverse),
            'top': (VPacker, obverse)}
        packer, slc = lookup[self.title_position]
        children = [title_box, main_box][slc]
        box = packer(children=children, pad=0, sep=sep,
                     align=self._title_align)
        return box


def add_interpolated_colorbar(da, colors, direction):
    """
    Add 'rastered' colorbar to DrawingArea
    """
    # Special case that arises due to not so useful
    # aesthetic mapping.
    if len(colors) == 1:
        colors = [colors[0], colors[0]]

    # Number of horizontal egdes(breaks) in the grid
    # No need to create more nbreak than colors, provided
    # no. of colors = no. of breaks = no. of cmap colors
    # the shading does a perfect interpolation
    nbreak = len(colors)

    if direction == 'vertical':
        mesh_width = 1
        mesh_height = nbreak-1
        linewidth = da.height/mesh_height
        # Construct rectangular meshgrid
        # The values(Z) at each vertex are just the
        # normalized (onto [0, 1]) vertical distance
        x = np.array([0, da.width])
        y = np.arange(0, nbreak) * linewidth
        X, Y = np.meshgrid(x, y)
        Z = Y/y.max()
    else:
        mesh_width = nbreak-1
        mesh_height = 1
        linewidth = da.width/mesh_width
        x = np.arange(0, nbreak) * linewidth
        y = np.array([0, da.height])
        X, Y = np.meshgrid(x, y)
        Z = X/x.max()

    # As a 2D coordinates array
    coordinates = np.zeros(
        ((mesh_width+1)*(mesh_height+1), 2),
        dtype=float)
    coordinates[:, 0] = X.ravel()
    coordinates[:, 1] = Y.ravel()

    cmap = ListedColormap(colors)
    coll = mcoll.QuadMesh(mesh_width, mesh_height,
                          coordinates,
                          antialiased=False,
                          shading='gouraud',
                          linewidth=0,
                          cmap=cmap,
                          array=Z.ravel())
    da.add_artist(coll)


def add_segmented_colorbar(da, colors, direction):
    """
    Add 'non-rastered' colorbar to DrawingArea
    """
    nbreak = len(colors)
    if direction == 'vertical':
        linewidth = da.height/nbreak
        verts = [None] * nbreak
        x1, x2 = 0, da.width
        for i, color in enumerate(colors):
            y1 = i * linewidth
            y2 = y1 + linewidth
            verts[i] = ((x1, y1), (x1, y2), (x2, y2), (x2, y1))
    else:
        linewidth = da.width/nbreak
        verts = [None] * nbreak
        y1, y2 = 0, da.height
        for i, color in enumerate(colors):
            x1 = i * linewidth
            x2 = x1 + linewidth
            verts[i] = ((x1, y1), (x1, y2), (x2, y2), (x2, y1))

    coll = mcoll.PolyCollection(verts,
                                facecolors=colors,
                                linewidth=0,
                                antialiased=False)
    da.add_artist(coll)


def add_ticks(da, locations, direction):
    segments = [None] * (len(locations)*2)
    if direction == 'vertical':
        x1, x2, x3, x4 = np.array([0.0, 1/5, 4/5, 1.0]) * da.width
        for i, y in enumerate(locations):
            segments[i*2:i*2+2] = [((x1, y), (x2, y)),
                                   ((x3, y), (x4, y))]
    else:
        y1, y2, y3, y4 = np.array([0.0, 1/5, 4/5, 1.0]) * da.height
        for i, x in enumerate(locations):
            segments[i*2:i*2+2] = [((x, y1), (x, y2)),
                                   ((x, y3), (x, y4))]

    coll = mcoll.LineCollection(segments,
                                color='#CCCCCC',
                                linewidth=1,
                                antialiased=False)
    da.add_artist(coll)


def create_labels(da, labels, locations, direction):
    """
    Return an OffsetBox with label texts
    """
    # The box dimensions are determined by the size of
    # the text objects. We put two dummy children at
    # either end to gaurantee that when center packed
    # the labels in the labels_box matchup with the ticks.
    fontsize = 9
    aux_transform = mtransforms.IdentityTransform()
    labels_box = AuxTransformBox(aux_transform)
    xs, ys = [0]*len(labels), locations
    ha, va = 'left', 'center'

    x1, y1 = 0, 0
    x2, y2 = 0, da.height
    if direction == 'horizontal':
        xs, ys = ys, xs
        ha, va = 'center', 'top'
        x2, y2 = da.width, 0
    txt1 = mtext.Text(x1, y1, '',
                      horizontalalignment=ha,
                      verticalalignment=va)
    txt2 = mtext.Text(x2, y2, '',
                      horizontalalignment=ha,
                      verticalalignment=va)
    labels_box.add_artist(txt1)
    labels_box.add_artist(txt2)

    legend_text = []
    for i, (x, y, text) in enumerate(zip(xs, ys, labels)):
        txt = mtext.Text(x, y, text,
                         size=fontsize,
                         horizontalalignment=ha,
                         verticalalignment=va)
        labels_box.add_artist(txt)
        legend_text.append(txt)
    return labels_box, {'legend_text': legend_text}


guide_colourbar = guide_colorbar

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd
from matplotlib.offsetbox import (AnchoredOffsetbox, TextArea,
                                  DrawingArea, HPacker, VPacker)

from .guide import guide as guide_class
from ..utils import is_string, gg_import, is_waive
from ..utils.exceptions import GgplotError

"""
Terminology
-----------
- A guide is either a legend or colorbar.

- A guide definition (gdef) is an instantiated guide as it
  is used in the process of creating the legend

- The guides class holds all guides that will appear in the
  plot

- A guide box is a fully drawn out guide.
  It is of subclass matplotlib.offsetbox.Offsetbox
"""


class guides(dict):

    def __init__(self, **kwargs):
        aes_names = {'alpha', 'color', 'fill',
                     'shape', 'size'}
        if 'colour' in kwargs:
            kwargs['color'] = kwargs.pop('colour')

        for ae in kwargs:
            if ae in aes_names:
                self[ae] = kwargs[ae]

    def __radd__(self, gg):
        gg.guides.update(self)
        return gg

    def build(self, plot, position):
        params = plot.theme._params

        def set_if_none(d, key, val):
            if d[key] is None:
                d[key] = val

        # by default, guide boxes are vertically aligned
        set_if_none(params, 'legend_box', 'vertical')

        # size of key (also used for bar in colorbar guide)
        set_if_none(params, 'legend_key_width', params['legend_key_size'])
        set_if_none(params, 'legend_key_height', params['legend_key_size'])
        set_if_none(params, 'legend_box', 'vertical')

        # by default, direction of each guide depends on
        # the position of the guide_
        if position in {'top', 'bottom'}:
            set_if_none(params, 'legend_direction', 'horizontal')
        else:  # left, right, (default)
            set_if_none(params, 'legend_direction', 'vertical')

        # justification of legend boxes
        if position in {'top', 'bottom'}:
            set_if_none(params, 'legend_box_just', ('center', 'top'))
        elif position in {'left', 'right'}:
            set_if_none(params, 'legend_box_just', ('left', 'top'))
        else:
            set_if_none(params, 'legend_box_just', ('center', 'center'))

        gdefs = self.train(plot)
        if not gdefs:
            return

        gdefs = self.merge(gdefs)
        gdefs = self.create_geoms(gdefs, plot)

        if not gdefs:
            return

        gboxes = self.draw(gdefs, plot.theme)
        bigbox = self.assemble(gboxes)
        return bigbox

    def train(self, plot):
        gdefs = []

        for scale in plot.scales:
            # guides(XXX) is stored in guides[XXX],
            # which is prior to scale_ZZZ(guide=XXX)
            # guide is determined in order of:
            #   + guides(XXX)
            #      > + scale_ZZZ(guide=XXX)
            #      > default(i.e., legend)
            output = scale.aesthetics[0]
            guide = self.get(output, scale.guide)

            if guide is None or guide is False:
                continue

            # check the validity of guide.
            # if guide is character, then find the guide object
            guide = self.validate(guide)
            # check the consistency of the guide and scale.
            if (guide.available_aes != 'any' and
                    scale.aesthetics[0] not in guide.available_aes):
                raise GgplotError(
                    "{} cannot be used for {}".format(
                        guide.__class__.__name__, scale.aesthetics))

            # title
            if is_waive(guide.title):
                if scale.name:
                    guide.title = scale.name
                else:
                    guide.title = plot.labels[output]

            # direction
            if guide.direction is None:
                guide.direction = plot.theme._params['legend_direction']

            # each guide object trains scale within the object,
            # so Guides (i.e., the container of guides)
            # need not to know about them
            guide.train(scale)

            if guide is not None:
                gdefs.append(guide)

        return gdefs

    def validate(self, guide):
        """
        Validate guide object
        """
        if is_string(guide):
            guide = 'guide_{}'.format(guide)
            obj = gg_import(guide)
            guide = obj()

        if not issubclass(obj, guide_class):
            raise GgplotError(
                "Unknown guide: {}".format(guide))
        return guide

    def merge(self, gdefs):
        """
        Merge overlapped guides
        """
        # group guide definitions by hash, and
        # reduce each group to a single guide
        # using the guide.merge method
        df = pd.DataFrame({
            'gdef': gdefs,
            'hash': [g.hash for g in gdefs]})
        grouped = df.groupby('hash')
        gdefs = []
        for name, group in grouped:
            gdef = reduce(
                lambda g1, g2: g1.merge(g2),
                group['gdef'])
            gdefs.append(gdef)
        return gdefs

    def create_geoms(self, gdefs, plot):
        """
        Add geoms to the guide definitions
        """
        new_gdefs = []
        for gdef in gdefs:
            gdef.create_geoms(plot)
            if gdef.geoms:
                new_gdefs.append(gdef)

        return new_gdefs

    def draw(self, gdefs, theme):
        """
        Draw out each guide definition

        Parameters
        ----------
        gdefs : list of guide_legend|guide_colorbar
            guide definitions
        theme : theme

        Returns
        -------
        out : list of matplotlib.offsetbox.Offsetbox
            A drawing of each legend
        """
        valid_positions = {'top', 'bottom', 'left', 'right'}

        def verify_title_position(g):
            if g.title_position is None:
                if g.direction == 'vertical':
                    g.title_position = 'top'
                elif g.direction == 'horizontal':
                    g.title_position = 'left'
            if g.title_position not in valid_positions:
                msg = 'title position "{}" is invalid'
                raise GgplotError(msg.format(g.title_position))
            return g

        gdefs = [verify_title_position(g) for g in gdefs]
        return [g.draw(theme) for g in gdefs]

    def assemble(self, gboxes):
        """
        Put together all the guide boxes
        """
        box = VPacker(children=gboxes, align="left", pad=0, sep=5)
        return box

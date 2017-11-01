from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from copy import deepcopy
from warnings import warn

import pandas as pd
import numpy as np
from matplotlib.offsetbox import (HPacker, VPacker)

from .guide import guide as guide_class
from ..utils import is_string, is_waive, Registry, suppress
from ..exceptions import PlotnineError


# Terminology
# -----------
# - A guide is either a legend or colorbar.
#
# - A guide definition (gdef) is an instantiated guide as it
#   is used in the process of creating the legend
#
# - The guides class holds all guides that will appear in the
#   plot
#
# - A guide box is a fully drawn out guide.
#   It is of subclass matplotlib.offsetbox.Offsetbox


class guides(dict):
    """
    Guides for each scale

    Used to assign a particular guide to an aesthetic(s).

    Parameters
    ----------
    kwargs : dict
        aesthetic - guide pairings. e.g
        ``color=guide_colorbar()``
    """

    def __init__(self, **kwargs):
        aes_names = {'alpha', 'color', 'fill',
                     'linetype', 'shape', 'size',
                     'stroke'}
        if 'colour' in kwargs:
            kwargs['color'] = kwargs.pop('colour')

        dict.__init__(self, ((ae, kwargs[ae]) for ae in kwargs
                             if ae in aes_names))

        # Determined from the theme when the guides are
        # getting built
        self.position = None
        self.box_direction = None
        self.box_align = None
        self.box_margin = None
        self.spacing = None

    def __radd__(self, gg, inplace=False):
        """
        Add guides to the plot

        Parameters
        ----------
        gg : ggplot
            ggplot object being created
        inplace : bool
            If **False**, the guides are added to
            a copy of the the ggplot object.

        Returns
        -------
        out : gglot
            ggplot object with guides. If *inplace*
            is **False** this is a copy of the original
            ggplot object.
        """
        gg = gg if inplace else deepcopy(gg)
        new_guides = {}
        for k in self:
            new_guides[k] = deepcopy(self[k])
        gg.guides.update(new_guides)
        return gg

    def build(self, plot):
        """
        Build the guides

        Parameters
        ----------
        plot : ggplot
            ggplot object being drawn

        Returns
        -------
        box : matplotlib.offsetbox.Offsetbox | None
            A box that contains all the guides for the plot.
            If there are no guides, **None** is returned.
        """
        get_property = plot.theme.themeables.property

        # by default, guide boxes are vertically aligned
        with suppress(KeyError):
            self.box_direction = get_property('legend_box')
        if self.box_direction is None:
            self.box_direction = 'vertical'

        with suppress(KeyError):
            self.position = get_property('legend_position')
        if self.position is None:
            self.position = 'right'

        # justification of legend boxes
        with suppress(KeyError):
            self.box_align = get_property('legend_box_just')
        if self.box_align is None:
            if self.position in {'left', 'right'}:
                tmp = 'left'
            else:
                tmp = 'center'
            self.box_align = tmp

        with suppress(KeyError):
            self.box_margin = get_property('legend_box_margin')
        if self.box_margin is None:
            self.box_margin = 10

        with suppress(KeyError):
            self.spacing = get_property('legend_spacing')
        if self.spacing is None:
            self.spacing = 10

        gdefs = self.train(plot)
        if not gdefs:
            return

        gdefs = self.merge(gdefs)
        gdefs = self.create_geoms(gdefs, plot)

        if not gdefs:
            return

        gboxes = self.draw(gdefs, plot.theme)
        bigbox = self.assemble(gboxes, gdefs, plot.theme)
        return bigbox

    def train(self, plot):
        """
        Compute all the required guides

        Parameters
        ----------
        plot : ggplot
            ggplot object

        Returns
        -------
        gdefs : list
            Guides for the plots
        """
        gdefs = []

        for scale in plot.scales:
            # The guide for aesthetic 'xxx' is stored
            # in plot.guides['xxx']. The priority for
            # the guides depends on how they are created
            # 1. ... + guides(xxx=guide_blah())
            # 2. ... + scale_xxx(guide=guide_blah())
            # 3. default(either guide_legend or guide_colorbar
            #            depending on the scale type)
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
                raise PlotnineError(
                    "{} cannot be used for {}".format(
                        guide.__class__.__name__, scale.aesthetics))

            # title
            if is_waive(guide.title):
                if scale.name:
                    guide.title = scale.name
                else:
                    try:
                        guide.title = str(plot.labels[output])
                    except KeyError:
                        warn("Cannot generate legend for the {!r} "
                             "aesthetic. Make sure you have mapped a "
                             "variable to it".format(output))
                        continue

            # each guide object trains scale within the object,
            # so Guides (i.e., the container of guides)
            # need not to know about them
            guide = guide.train(scale)

            if guide is not None:
                gdefs.append(guide)

        return gdefs

    def validate(self, guide):
        """
        Validate guide object
        """
        if is_string(guide):
            guide = Registry['guide_{}'.format(guide)]()

        if not isinstance(guide, guide_class):
            raise PlotnineError(
                "Unknown guide: {}".format(guide))
        return guide

    def merge(self, gdefs):
        """
        Merge overlapped guides

        For example::

            from plotnine import *
            gg = ggplot(mtcars, aes(y='wt', x='mpg', colour='factor(cyl)'))
            gg = gg + stat_smooth(aes(fill='factor(cyl)'), method='lm')
            gg = gg + geom_point()
            gg

        This would create two guides with the same hash
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
            # merge
            gdef = group['gdef'].iloc[0]
            for g in group['gdef'].iloc[1:]:
                gdef = gdef.merge(g)
            gdefs.append(gdef)
        return gdefs

    def create_geoms(self, gdefs, plot):
        """
        Add geoms to the guide definitions
        """
        new_gdefs = []
        for gdef in gdefs:
            gdef = gdef.create_geoms(plot)
            if gdef:
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
            Plot theme

        Returns
        -------
        out : list of matplotlib.offsetbox.Offsetbox
            A drawing of each legend
        """
        for g in gdefs:
            g.theme = theme
            g._set_defaults()
        return [g.draw() for g in gdefs]

    def assemble(self, gboxes, gdefs, theme):
        """
        Put together all the guide boxes

        Parameters
        ----------
        gboxes : list
            List of :class:`~matplotlib.offsetbox.Offsetbox`,
            where each item is a legend for a single aesthetic.
        gdefs : list of guide_legend|guide_colorbar
            guide definitions
        theme : theme
            Plot theme

        Returns
        -------
        box : OffsetBox
            A box than can be placed onto a plot
        """
        # place the guides according to the guide.order
        # 0 do not sort
        # 1-99 sort
        for gdef in gdefs:
            if gdef.order == 0:
                gdef.order = 100
            elif not 0 <= gdef.order <= 99:
                raise PlotnineError(
                    "'order' for a guide should be "
                    "between 0 and 99")
        orders = [gdef.order for gdef in gdefs]
        idx = np.argsort(orders)
        gboxes = [gboxes[i] for i in idx]

        # direction when more than legend
        if self.box_direction == 'vertical':
            packer = VPacker
        elif self.box_direction == 'horizontal':
            packer = HPacker
        else:
            raise PlotnineError(
                "'legend_box' should be either "
                "'vertical' or 'horizontal'")

        box = packer(children=gboxes, align=self.box_align,
                     pad=self.box_margin, sep=self.spacing)
        return box

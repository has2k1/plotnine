from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd
from matplotlib.cbook import Bunch
from matplotlib.offsetbox import (AnchoredOffsetbox, TextArea,
                                  DrawingArea, HPacker, VPacker)

from ..utils import gg_import, ColoredDrawingArea
from ..utils.exceptions import gg_warning, GgplotError
from .guide import guide

# See guides.py for terminology


class guide_legend(guide):
    # general
    nrow = None
    ncol = None
    byrow = False

    # parameter
    available_aes = 'any'

    def merge(self, other):
        """
        Merge overlapped guides
        e.g
        >>> from ggplot import *
        >>> gg = ggplot(aes(x='cut', fill='cut', color='cut'), data=diamonds)
        >>> gg = gg + stat_bin()
        >>> gg

        This would create similar guides for fill and color where only
        a single guide would do
        """
        self.key = pd.merge(self.key, other.key)
        duplicated = set(self.override_aes) & set(other.override_aes)
        if duplicated:
            gg_warning("Duplicated override_aes is ignored.")
        self.override_aes.update(other.override_aes)
        for ae in duplicated:
            self.override_aes.pop(ae)
        return self

    def create_geoms(self, plot):
        """
        Make information needed to draw a legend for each of the layers.

        For each layer, that information is a dictionary with the geom
        to draw the guide together with the data and the parameters that
        will be used in the call to geom.
        """
        lst = []
        for l in plot.layers:
            all_ae = [ae for d in [l.mapping, plot.mapping,
                                   l.stat.DEFAULT_AES]
                      for ae in d]
            geom_ae = [ae for d in [l.geom.REQUIRED_AES,
                                    l.geom.DEFAULT_AES]
                       for ae in d]
            matched = set(all_ae) & set(geom_ae) & set(self.key.columns)
            matched = matched - set(l.geom.manual_aes)

            if len(matched):
                # This layer contributes to the legend
                if l.show_guide is None or l.show_guide:
                    # Default is to include it
                    tmp = self.key[list(matched)].copy()
                    data = l.use_defaults(tmp)
                else:
                    continue
            else:
                # This layer does not contribute to the legend
                if l.show_guide is None or not l.show_guide:
                    continue
                else:
                    zeros = [0] * len(self.key)
                    data = l.use_defaults(pd.DataFrame())[zeros]

            # override.aes in guide_legend manually changes the geom
            for ae in set(self.override_aes) & set(data.columns):
                data[ae] = self.override_aes[ae]

            geom = gg_import('geom_' + l.geom.guide_geom)
            params = l.geom.manual_aes.copy()
            params.update(l.stat.params)
            lst.append(Bunch(geom=geom, data=data, params=params))

        self.geoms = lst
        return self

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
        # default setting
        if self.label_position is None:
            label_position = 'right'
        if label_position not in ['top', 'bottom', 'left', 'right']:
            msg = 'label position {} is invalid'
            raise GgplotError(msg.format(label_position))

        nbreak = len(self.key)

        # gap between the keys
        hgap = 0.3 * 20  # .3 lines
        vgap = hgap

        # title
        # TODO: theme me
        title = TextArea("  %s" % self.title, textprops=dict(color="k"))
        lst = [title]
        for i in range(nbreak):
            # TODO: theme me
            da = ColoredDrawingArea(20, 20, 0, 0, color='#E5E5E5')
            # overlay geoms
            for g in self.geoms:
                g.data.rename(columns=g.geom._aes_renames, inplace=True)
                lst.append(g.geom.draw_legend(g.data.iloc[i], g.params, da))

        # TODO: theme me
        box = VPacker(children=lst, align='center', pad=0, sep=vgap)
        return box

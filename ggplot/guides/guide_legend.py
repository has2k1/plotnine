from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import hashlib
from itertools import islice

import numpy as np
import pandas as pd
from matplotlib.cbook import Bunch
from matplotlib.offsetbox import (TextArea, HPacker, VPacker)

from ..scales.scale import scale_continuous
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

    def train(self, scale):
        """
        Create the key for the guide

        The key is a dataframe with two columns:
            - scale name : values
            - label : labels for each value

        scale name is one of the aesthetics
        ['x', 'y', 'color', 'fill', 'size', 'shape', 'alpha']
        """
        breaks = scale.scale_breaks(can_waive=False)
        try:
            breaks = list(breaks.keys())
        except AttributeError:
            pass

        key = pd.DataFrame({
            scale.aesthetics[0]: scale.map(breaks),
            'label': scale.scale_labels(breaks, can_waive=False)})

        # Drop out-of-range values for continuous scale
        # (should use scale$oob?)

        # Currently, numpy does not deal with NA (Not available)
        # When they are introduced, the block below should be
        # adjusted likewise, see ggplot2, guide-lengend.r
        if isinstance(scale, scale_continuous):
            limits = scale.limits
            b = np.asarray(breaks)
            noob = np.logical_and(limits[0] <= b,
                                  b <= limits[1])
            key = key[noob]

        if len(key) == 0:
            return None

        self.key = key

        # create a hash of the important information in the guide
        labels = ' '.join(str(x) for x in self.key['label'])
        info = '\n'.join([self.title, labels, str(self.direction),
                          self.__class__.__name__])
        self.hash = hashlib.md5(info).hexdigest()

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
        # A layer either contributes to the guide, or it does not. The
        # guide entries may be ploted in the layers
        self.glayers = []
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

            geom = gg_import('geom_{}'.format(l.geom.guide_geom))
            self.glayers.append(Bunch(geom=geom, data=data, layer=l))

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
            self.label_position = 'right'
        if self.label_position not in ['top', 'bottom', 'left', 'right']:
            msg = 'label position {} is invalid'
            raise GgplotError(msg.format(self.label_position))

        nbreak = len(self.key)

        # rows and columns
        if self.nrow is not None and self.ncol is not None:
            if guide.nrow * guide.ncol < nbreak:
                raise GgplotError(
                    "nrow x ncol need to be larger",
                    "than the number of breaks")

        if self.nrow is None:
            if self.ncol is not None:
                self.nrow = int(np.ceil(nbreak/self.ncol))
            elif self.direction == 'horizontal':
                self.nrow = 1
            else:
                self.nrow = nbreak

        if self.ncol is None:
            if self.nrow is not None:
                self.ncol = int(np.ceil(nbreak/self.nrow))
            elif self.direction == 'horizontal':
                self.ncol = nbreak
            else:
                self.ncol = 1

        # gap between the keys
        hgap = 0.3 * 20  # .3 lines
        vgap = hgap

        # title
        # TODO: theme me
        title_box = TextArea(
            self.title, textprops=dict(color='k', weight='bold'))
        title_align = theme._params['legend_title_align']
        if title_align is None:
            if self.direction == 'vertical':
                title_align = 'left'
            else:
                title_align = 'center'

        # labels
        # TODO: theme me
        labels = []
        for item in self.key['label']:
            if isinstance(item, np.float) and np.float.is_integer(item):
                item = np.int(item)  # 1.0 to 1
            ta = TextArea(item, textprops=dict(color='k'))
            labels.append(ta)
        # Drawings
        # TODO: theme me
        drawings = []
        for gl in self.glayers:
            gl.data.rename(columns=gl.geom._aes_renames, inplace=True)
        for i in range(nbreak):
            da = ColoredDrawingArea(20, 20, 0, 0, color='#E5E5E5')
            # overlay geoms
            for gl in self.glayers:
                da = gl.geom.draw_legend(gl.data.iloc[i], da, gl.layer)
            drawings.append(da)

        # Match Drawings with labels to create the entries
        # TODO: theme me
        lookup = {
            'right': (HPacker, slice(None, None, -1)),
            'left': (HPacker, slice(0, None)),
            'bottom': (VPacker, slice(None, None, -1)),
            'top': (VPacker, slice(0, None))}
        packer, slc = lookup[self.label_position]
        entries = []
        # matplotlib adds a baseline padding below the text
        # which leads to a bigger gap when the label is on top
        sep = hgap*.2 if self.label_position == 'top' else hgap
        for d, l in zip(drawings, labels):
            e = packer(children=[l, d][slc], align='left', pad=0, sep=sep)
            entries.append(e)

        # Put the entries together in rows or columns
        # A chunk is either a row or a column of entries
        # for a single legend
        if self.byrow:
            chunk_size, packers = self.ncol, [HPacker, VPacker]
            seps = [hgap, vgap]
        else:
            chunk_size, packers = self.nrow, [VPacker, HPacker]
            seps = [vgap, hgap]

        if self.reverse:
            entries = entries[::-1]
        chunks = []
        for i in range(len(entries)):
            start = i*chunk_size
            stop = i*chunk_size + chunk_size
            s = islice(entries, start, stop)
            chunks.append(list(s))
            if stop >= len(entries):
                break

        chunk_boxes = []
        for chunk in chunks:
            d1 = packers[0](children=chunk,
                            align='left', pad=0, sep=seps[0])
            chunk_boxes.append(d1)

        # Put all the entries (row & columns) together
        entries_box = packers[1](children=chunk_boxes,
                                 align='baseline',
                                 pad=0,
                                 sep=seps[1])
        # TODO: theme me
        # Put the title and entries together
        packer, slc = lookup[self.title_position]
        children = [title_box, entries_box][slc]
        box = packer(children=children, align=title_align, pad=0, sep=hgap)
        return box

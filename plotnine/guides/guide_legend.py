from __future__ import annotations

import hashlib
import types
import typing
from contextlib import suppress
from itertools import islice
from warnings import warn

import numpy as np
import pandas as pd

from ..exceptions import PlotnineError, PlotnineWarning
from ..geoms import geom_text
from ..mapping.aes import rename_aesthetics
from ..utils import SIZE_FACTOR, remove_missing
from .guide import guide

if typing.TYPE_CHECKING:
    from typing import Optional

    from plotnine.typing import TupleInt2


# See guides.py for terminology


class guide_legend(guide):
    """
    Legend guide

    Parameters
    ----------
    nrow : int
        Number of rows of legends.
    ncol : int
        Number of columns of legends.
    byrow : bool
        Whether to fill the legend row-wise or column-wise.
    keywidth : float
        Width of the legend key.
    keyheight : float
        Height of the legend key.
    kwargs : dict
        Parameters passed on to :class:`.guide`
    """

    # general
    nrow: int = -1
    ncol: int = -1
    byrow = False

    # key
    keywidth: Optional[int] = None
    keyheight: Optional[int] = None

    # parameter
    available_aes = {"any"}

    def train(self, scale, aesthetic=None):
        """
        Create the key for the guide

        The key is a dataframe with two columns:
            - scale name : values
            - label : labels for each value

        scale name is one of the aesthetics
        ['x', 'y', 'color', 'fill', 'size', 'shape', 'alpha',
         'stroke']

        Returns this guide if trainning is successful and None
        if it fails
        """
        if aesthetic is None:
            aesthetic = scale.aesthetics[0]

        breaks = scale.get_bounded_breaks()
        if not breaks:
            return None

        key = pd.DataFrame(
            {aesthetic: scale.map(breaks), "label": scale.get_labels(breaks)}
        )

        if len(key) == 0:
            return None

        self.key = key

        # create a hash of the important information in the guide
        labels = " ".join(str(x) for x in self.key["label"])
        info = "\n".join(
            [self.title, labels, str(self.direction), self.__class__.__name__]
        )
        self.hash = hashlib.md5(info.encode("utf-8")).hexdigest()
        return self

    def merge(self, other):
        """
        Merge overlapped guides

        For example::

            from ggplot import *
            gg = ggplot(aes(x='cut', fill='cut', color='cut'), data=diamonds)
            gg + stat_bin()

        This would create similar guides for fill and color where only
        a single guide would do
        """
        self.key = pd.merge(self.key, other.key)
        duplicated = set(self.override_aes) & set(other.override_aes)
        if duplicated:
            warn("Duplicated override_aes is ignored.", PlotnineWarning)
        self.override_aes.update(other.override_aes)
        for ae in duplicated:
            del self.override_aes[ae]
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
            exclude = set()
            if isinstance(l.show_legend, dict):
                l.show_legend = rename_aesthetics(l.show_legend)
                exclude = {ae for ae, val in l.show_legend.items() if not val}
            elif l.show_legend not in (None, True):
                continue

            matched = self.legend_aesthetics(l, plot)

            # This layer does not contribute to the legend
            if not set(matched) - exclude:
                continue

            data = self.key[matched].copy()

            # Modify aesthetics
            try:
                data = l.use_defaults(data)
            except PlotnineError:
                warn(
                    "Failed to apply `after_scale` modifications "
                    "to the legend.",
                    PlotnineWarning,
                )
                data = l.use_defaults(data, aes_modifiers={})

            # override.aes in guide_legend manually changes the geom
            for ae in set(self.override_aes) & set(data.columns):
                data[ae] = self.override_aes[ae]

            data = remove_missing(
                data,
                l.geom.params["na_rm"],
                list(l.geom.REQUIRED_AES | l.geom.NON_MISSING_AES),
                f"{l.geom.__class__.__name__} legend",
            )
            self.glayers.append(
                types.SimpleNamespace(geom=l.geom, data=data, layer=l)
            )
        if not self.glayers:
            return None
        return self

    def _calculate_rows_and_cols(self) -> TupleInt2:
        nrow, ncol = -1, -1
        nbreak = len(self.key)

        if hasattr(self, "nrow"):
            nrow = self.nrow

        if hasattr(self, "ncol"):
            ncol = self.ncol

        if nrow != -1 and ncol != -1:
            if nrow * ncol < nbreak:
                raise PlotnineError(
                    "nrow x ncol need to be larger "
                    "than the number of breaks"
                )
            return nrow, ncol

        if nrow == -1 and ncol == -1:
            if self.direction == "horizontal":
                nrow = int(np.ceil(nbreak / 5))
            else:
                ncol = int(np.ceil(nbreak / 20))

        if nrow == -1:
            nrow = int(np.ceil(nbreak / ncol))
        elif ncol == -1:
            ncol = int(np.ceil(nbreak / nrow))

        return nrow, ncol

    def _set_defaults(self, theme):
        guide._set_defaults(self, theme)
        _property = theme.themeables.property
        self.nrow, self.ncol = self._calculate_rows_and_cols()
        nbreak = len(self.key)

        # key width and key height for each legend entry
        #
        # Take a peak into data['size'] to make sure the
        # legend dimensions are big enough
        """
        >>> gg = ggplot(diamonds, aes(x='cut', y='clarity'))
        >>> gg = gg + stat_sum(aes(group='cut'))
        >>> gg + scale_size(range=(3, 25))

        Note the different height sizes for the entries
        """

        # FIXME: This should be in the geom instead of having
        # special case conditional branches
        def determine_side_length(initial_size):
            default_pad = initial_size * 0.5
            # default_pad = 0
            size = np.ones(nbreak) * initial_size
            for i in range(nbreak):
                for gl in self.glayers:
                    _size = 0
                    pad = default_pad
                    # Full size of object to appear in the
                    # legend key
                    with suppress(IndexError):
                        if "size" in gl.data:
                            _size = gl.data["size"].iloc[i] * SIZE_FACTOR
                            if "stroke" in gl.data:
                                _size += (
                                    2 * gl.data["stroke"].iloc[i] * SIZE_FACTOR
                                )

                        # special case, color does not apply to
                        # border/linewidth
                        if isinstance(gl.geom, geom_text):
                            pad = 0
                            if _size < initial_size:
                                continue

                        try:
                            # color(edgecolor) affects size(linewidth)
                            # When the edge is not visible, we should
                            # not expand the size of the keys
                            if gl.data["color"].iloc[i] is not None:
                                size[i] = np.max([_size + pad, size[i]])
                        except KeyError:
                            break

            return size

        # keysize
        if self.keywidth is None:
            width = determine_side_length(_property("legend_key_width"))
            if self.direction == "vertical":
                width[:] = width.max()
            self._keywidth = width
        else:
            self._keywidth = [self.keywidth] * nbreak

        if self.keyheight is None:
            height = determine_side_length(_property("legend_key_height"))
            if self.direction == "horizontal":
                height[:] = height.max()
            self._keyheight = height
        else:
            self._keyheight = [self.keyheight] * nbreak

    def draw(self):
        """
        Draw guide

        Returns
        -------
        out : matplotlib.offsetbox.Offsetbox
            A drawing of this legend
        """
        from matplotlib.offsetbox import HPacker, TextArea, VPacker

        from .._mpl.offsetbox import ColoredDrawingArea

        obverse = slice(0, None)
        reverse = slice(None, None, -1)
        nbreak = len(self.key)
        _targets = self.theme._targets

        # When there is more than one guide, we keep
        # record of all of them using lists
        if "legend_title" not in _targets:
            _targets["legend_title"] = []
        if "legend_text_legend" not in _targets:
            _targets["legend_key"] = []
            _targets["legend_text_legend"] = []

        # title
        title_box = TextArea(self.title, textprops={"color": "black"})
        _targets["legend_title"].append(title_box)

        # labels
        labels = []
        for item in self.key["label"]:
            if isinstance(item, float) and float.is_integer(item):
                item = int(item)  # 1.0 to 1
            va = "center" if self.label_position == "top" else "baseline"
            ta = TextArea(item, textprops={"color": "black", "va": va})
            labels.append(ta)
            _targets["legend_text_legend"].extend(labels)

        # Drawings
        drawings = []
        for i in range(nbreak):
            da = ColoredDrawingArea(
                self._keywidth[i], self._keyheight[i], 0, 0, color="white"
            )
            # overlay geoms
            for gl in self.glayers:
                with suppress(IndexError):
                    data = gl.data.iloc[i]
                    da = gl.geom.draw_legend(data, da, gl.layer)
            drawings.append(da)
        _targets["legend_key"].append(drawings)

        # Match Drawings with labels to create the entries
        lookup = {
            "right": (HPacker, reverse),
            "left": (HPacker, obverse),
            "bottom": (VPacker, reverse),
            "top": (VPacker, obverse),
        }
        packer, slc = lookup[self.label_position]
        entries = []
        for d, l in zip(drawings, labels):
            e = packer(
                children=[l, d][slc],
                sep=self._label_margin,
                align="center",
                pad=0,
            )
            entries.append(e)

        # Put the entries together in rows or columns
        # A chunk is either a row or a column of entries
        # for a single legend
        if self.byrow:
            chunk_size, packers = self.ncol, [HPacker, VPacker]
            sep1 = self._legend_entry_spacing_x
            sep2 = self._legend_entry_spacing_y
        else:
            chunk_size, packers = self.nrow, [VPacker, HPacker]
            sep1 = self._legend_entry_spacing_y
            sep2 = self._legend_entry_spacing_x

        if self.reverse:
            entries = entries[::-1]
        chunks = []
        for i in range(len(entries)):
            start = i * chunk_size
            stop = start + chunk_size
            s = islice(entries, start, stop)
            chunks.append(list(s))
            if stop >= len(entries):
                break

        chunk_boxes = []
        for chunk in chunks:
            d1 = packers[0](children=chunk, align="left", sep=sep1, pad=0)
            chunk_boxes.append(d1)

        # Put all the entries (row & columns) together
        entries_box = packers[1](
            children=chunk_boxes, align="baseline", sep=sep2, pad=0
        )

        # Put the title and entries together
        packer, slc = lookup[self.title_position]
        children = [title_box, entries_box][slc]
        box = packer(
            children=children,
            sep=self._title_margin,
            align=self._title_align,
            pad=self._legend_margin,
        )

        return box

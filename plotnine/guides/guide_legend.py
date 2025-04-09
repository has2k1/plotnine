from __future__ import annotations

import hashlib
from contextlib import suppress
from dataclasses import dataclass, field
from functools import cached_property
from itertools import islice
from types import SimpleNamespace as NS
from typing import TYPE_CHECKING, cast
from warnings import warn

import numpy as np
import pandas as pd

from .._utils import remove_missing
from ..exceptions import PlotnineError, PlotnineWarning
from ..mapping.aes import rename_aesthetics
from .guide import GuideElements, guide

if TYPE_CHECKING:
    from typing import Any, Optional

    from matplotlib.artist import Artist
    from matplotlib.offsetbox import PackerBase

    from plotnine.geoms.geom import geom
    from plotnine.layer import layer
    from plotnine.typing import Side


# See guides.py for terminology


@dataclass
class LayerParameters:
    geom: geom
    data: pd.DataFrame
    layer: layer


@dataclass
class guide_legend(guide):
    """
    Legend guide
    """

    nrow: Optional[int] = None
    """Number of rows of legends."""

    ncol: Optional[int] = None
    """Number of columns of legends."""

    byrow: bool = False
    """Whether to fill the legend row-wise or column-wise."""

    override_aes: dict[str, Any] = field(default_factory=dict)
    """Aesthetic parameters of legend key."""

    # Non-Parameter Attributes
    available_aes: set[str] = field(
        init=False, default_factory=lambda: {"any"}
    )
    """Aesthetics for which this guide can be used"""

    _layer_parameters: list[LayerParameters] = field(
        init=False, default_factory=list
    )

    def __post_init__(self):
        self._elements_cls = GuideElementsLegend
        self.elements: GuideElementsLegend

    def train(self, scale, aesthetic=None):
        """
        Create the key for the guide

        The key is a dataframe with two columns:

        - scale name : values
        - label : labels for each value

        scale name is one of the aesthetics: `x`, `y`, `color`,
        `fill`, `size`, `shape`, `alpha`, `stroke`.

        Returns this guide if training is successful and None
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
            [
                str(self.title),
                labels,
                str(self.direction),
                self.__class__.__name__,
            ]
        )
        self.hash = hashlib.sha256(info.encode("utf-8")).hexdigest()
        return self

    def merge(self, other):
        """
        Merge overlapped guides

        For example:

        ```python
        from ggplot import *
        p = (
            ggplot(aes(x="cut", fill="cut", color="cut"), data=diamonds)
            + stat_bin()
        )
        ```

        Would create similar guides for fill and color where only
        a single guide would do
        """
        self.key = self.key.merge(other.key)
        duplicated = set(self.override_aes) & set(other.override_aes)
        if duplicated:
            msg = f"Duplicated override_aes, `{duplicated}`, are  ignored."
            warn(msg, PlotnineWarning)
        self.override_aes.update(other.override_aes)
        for ae in duplicated:
            del self.override_aes[ae]
        return self

    def create_geoms(self):
        """
        Make information needed to draw a legend for each of the layers.

        For each layer, that information is a dictionary with the geom
        to draw the guide together with the data and the parameters that
        will be used in the call to geom.
        """
        # A layer either contributes to the guide, or it does not. The
        # guide entries may be plotted in the layers
        for l in self.plot_layers:
            exclude = set()
            if isinstance(l.show_legend, dict):
                l.show_legend = rename_aesthetics(l.show_legend)
                exclude = {ae for ae, val in l.show_legend.items() if not val}
            elif l.show_legend not in (None, True):
                continue

            matched = self.legend_aesthetics(l)
            matched_set = set(matched)

            # This layer does not contribute to the legend
            if not matched_set - exclude:
                continue

            data = self.key[matched].copy()

            # Modify aesthetics

            # When doing after_scale evaluations, we only consider those
            # for the aesthetics that are valid for this layer/geom.
            aes_modifiers = {
                ae: l.mapping._scaled[ae]
                for ae in l.geom.aesthetics() & l.mapping._scaled.keys()
            }

            try:
                data = l.use_defaults(data, aes_modifiers)
            except PlotnineError:
                warn(
                    "Failed to apply `after_scale` modifications to the "
                    "legend. This probably should not happen. Help us "
                    "discover why, please open and issue at "
                    "https://github.com/has2k1/plotnine/issues",
                    PlotnineWarning,
                )
                data = l.use_defaults(data, {})

            # override.aes in guide_legend manually changes the geom
            for ae in set(self.override_aes) & set(data.columns):
                data[ae] = self.override_aes[ae]

            data = remove_missing(
                data,
                l.geom.params["na_rm"],
                list(l.geom.REQUIRED_AES | l.geom.NON_MISSING_AES),
                f"{l.geom.__class__.__name__} legend",
            )
            self._layer_parameters.append(LayerParameters(l.geom, data, l))

        if not self._layer_parameters:
            return None
        return self

    def _calculate_rows_and_cols(
        self, elements: GuideElementsLegend
    ) -> tuple[int, int]:
        nrow, ncol = self.nrow, self.ncol
        nbreak = len(self.key)

        if nrow and ncol:
            if nrow * ncol < nbreak:
                raise PlotnineError(
                    "nrow x ncol needs to be larger than the number of breaks"
                )
            return nrow, ncol

        if (nrow, ncol) == (None, None):
            if elements.is_horizontal:
                nrow = int(np.ceil(nbreak / 5))
            else:
                ncol = int(np.ceil(nbreak / 15))

        if nrow is None:
            ncol = cast("int", ncol)
            nrow = int(np.ceil(nbreak / ncol))
        elif ncol is None:
            nrow = cast("int", nrow)
            ncol = int(np.ceil(nbreak / nrow))

        return nrow, ncol

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
        targets = self.theme.targets
        keys_order = reverse if self.reverse else obverse
        elements = self.elements

        # title
        title = cast("str", self.title)
        title_box = TextArea(title)
        targets.legend_title = title_box._text  # type: ignore

        # labels
        props = {"ha": elements.text.ha, "va": elements.text.va}
        labels = [TextArea(s, textprops=props) for s in self.key["label"]]
        _texts = [l._text for l in labels]  # type: ignore
        targets.legend_text_legend = _texts

        # Drawings
        drawings: list[ColoredDrawingArea] = []
        for i in range(nbreak):
            da = ColoredDrawingArea(
                elements.key_widths[i], elements.key_heights[i], 0, 0
            )

            # overlay geoms
            for params in self._layer_parameters:
                with suppress(IndexError):
                    key_data = params.data.iloc[i]
                    params.geom.draw_legend(key_data, da, params.layer)

            drawings.append(da)
        targets.legend_key = drawings

        # Match Drawings with labels to create the entries
        lookup: dict[Side, tuple[type[PackerBase], slice]] = {
            "right": (HPacker, reverse),
            "left": (HPacker, obverse),
            "bottom": (VPacker, reverse),
            "top": (VPacker, obverse),
        }
        packer, slc = lookup[elements.text_position]
        if self.elements.text.is_blank:
            key_boxes = [d for d in drawings][keys_order]
        else:
            key_boxes = [
                packer(
                    children=[l, d][slc],
                    sep=elements.text.margin,
                    align=elements.text.align,
                    pad=0,
                )
                for d, l in zip(drawings, labels)
            ][keys_order]

        # Put the entries together in rows or columns
        # A chunk is either a row or a column of entries
        # for a single legend
        nrow, ncol = self._calculate_rows_and_cols(elements)
        if self.byrow:
            chunk_size = ncol
            packer_dim1, packer_dim2 = (HPacker, VPacker)
            sep1 = elements.key_spacing_x
            sep2 = elements.key_spacing_y
        else:
            chunk_size = nrow
            packer_dim1, packer_dim2 = (VPacker, HPacker)
            sep1 = elements.key_spacing_y
            sep2 = elements.key_spacing_x

        chunks = []
        for i in range(len(key_boxes)):
            start = i * chunk_size
            stop = start + chunk_size
            s = islice(key_boxes, start, stop)
            chunks.append(list(s))
            if stop >= len(key_boxes):
                break

        chunk_boxes: list[Artist] = [
            packer_dim1(children=chunk, align="left", sep=sep1, pad=0)
            for chunk in chunks
        ]

        # Put all the entries (row & columns) together
        entries_box = packer_dim2(
            children=chunk_boxes, align="baseline", sep=sep2, pad=0
        )

        # Put the title and entries together
        packer, slc = lookup[elements.title_position]

        if elements.title.is_blank:
            children: list[Artist] = [entries_box]
        else:
            children = [title_box, entries_box][slc]

        box = packer(
            children=children,
            sep=elements.title.margin,
            align=elements.title.align,
            pad=elements.margin,
        )

        return box


class GuideElementsLegend(GuideElements):
    """
    Access & calculate theming for the legend
    """

    @cached_property
    def text(self):
        size = self.theme.getp(("legend_text_legend", "size"))
        ha = self.theme.getp(("legend_text_legend", "ha"), "center")
        va = self.theme.getp(("legend_text_legend", "va"), "center")
        is_blank = self.theme.T.is_blank("legend_text_legend")

        # The original ha & va values are used by the HPacker/VPacker
        # to align the TextArea with the DrawingArea.
        # We set ha & va to values that combine best with the aligning
        # for the text area.
        align = va if self.text_position in {"left", "right"} else ha
        return NS(
            margin=self._text_margin,
            align=align,
            fontsize=size,
            ha="center",
            va="baseline",
            is_blank=is_blank,
        )

    @cached_property
    def text_position(self) -> Side:
        if not (pos := self.theme.getp("legend_text_position")):
            pos = "right"
        return pos

    @cached_property
    def key_spacing_x(self) -> float:
        return self.theme.getp("legend_key_spacing_x", 0)

    @cached_property
    def key_spacing_y(self) -> float:
        return self.theme.getp("legend_key_spacing_y", 0)

    @cached_property
    def _key_dimensions(self) -> list[tuple[float, float]]:
        """
        key width and key height for each legend entry

        Take a peak into data['size'] to make sure the legend key
        dimensions are big enough.
        """
        #  Note the different height sizes for the entries
        guide = cast("guide_legend", self.guide)
        min_size = (
            self.theme.getp("legend_key_width"),
            self.theme.getp("legend_key_height"),
        )

        # Find the size that fits each key in the legend,
        sizes: list[list[tuple[float, float]]] = []
        for params in guide._layer_parameters:
            sizes.append([])
            get_key_size = params.geom.legend_key_size
            for i in range(len(params.data)):
                key_data = params.data.iloc[i]
                sizes[-1].append(
                    get_key_size(key_data, min_size, params.layer)
                )

        # The maximum size across each layer
        arr = np.max(sizes, axis=0)
        return [(row[0], row[1]) for row in arr]

    @cached_property
    def key_widths(self) -> list[float]:
        """
        Widths of the keys

        If legend is vertical, key widths must be equal, so we use the
        maximum. So a plot like

           (ggplot(diamonds, aes(x="cut", y="clarity"))
            + stat_sum(aes(group="cut"))
            + scale_size(range=(3, 25))
           )

        would have keys with variable heights, but fixed width.
        """
        ws = [w for w, _ in self._key_dimensions]
        if self.is_vertical:
            return [max(ws)] * len(ws)
        return ws

    @cached_property
    def key_heights(self) -> list[float]:
        """
        Heights of the keys

        If legend is horizontal, then key heights must be equal, so we
        use the maximum
        """
        hs = [h for _, h in self._key_dimensions]
        if self.is_horizontal:
            return [max(hs)] * len(hs)
        return hs

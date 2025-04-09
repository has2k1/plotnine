from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from functools import cached_property
from types import SimpleNamespace as NS
from typing import TYPE_CHECKING, cast
from warnings import warn

import numpy as np
import pandas as pd
from mizani.bounds import rescale

from .._utils import get_opposite_side
from ..exceptions import PlotnineError, PlotnineWarning
from ..mapping.aes import rename_aesthetics
from ..scales.scale_continuous import scale_continuous
from .guide import GuideElements, guide

if TYPE_CHECKING:
    from typing import Literal, Optional, Sequence

    from matplotlib.artist import Artist
    from matplotlib.collections import LineCollection
    from matplotlib.offsetbox import AuxTransformBox, PackerBase
    from matplotlib.text import Text

    from plotnine import theme
    from plotnine.scales.scale import scale
    from plotnine.typing import Side


@dataclass
class guide_colorbar(guide):
    """
    Guide colorbar

    Notes
    -----
    To correctly place a rasterized colorbar when saving the plot as an `svg`
    or `pdf`, you should set the `dpi` to 72 i.e. `theme(dpi=72)`{.py}.
    """

    nbin: Optional[int] = None
    """
    Number of bins for drawing a colorbar. A larger value yields
    a smoother colorbar
    """

    display: Literal["gradient", "rectangles", "raster"] = "gradient"
    """How to render the colorbar."""

    alpha: Optional[float] = None
    """
    Opacity (in the range `[0, 1]`) of the colorbar. The default
    `None`, is to use the opacity of the plot.
    """

    draw_ulim: bool = True
    """Whether to show the upper limit tick marks."""

    draw_llim: bool = True
    """Whether to show the lower limit tick marks. """

    # Non-Parameter Attributes
    available_aes: set[str] = field(
        init=False, default_factory=lambda: {"colour", "color", "fill"}
    )

    def __post_init__(self):
        self._elements_cls = GuideElementsColorbar
        self.elements: GuideElementsColorbar

        if self.nbin is None:
            self.nbin = 300  # if self.display == "gradient" else 300

    def train(self, scale: scale, aesthetic=None):
        self.nbin = cast("int", self.nbin)
        self.title = cast("str", self.title)

        if not isinstance(scale, scale_continuous):
            warn("colorbar guide needs continuous scales", PlotnineWarning)
            return None

        if aesthetic is None:
            aesthetic = scale.aesthetics[0]

        # Do nothing if scales are inappropriate
        if set(scale.aesthetics) & self.available_aes == 0:
            warn("colorbar guide needs appropriate scales.", PlotnineWarning)
            return None

        # value = breaks (numeric) is used for determining the
        # position of ticks
        limits = scale.final_limits
        breaks = scale.get_bounded_breaks()

        if not len(breaks):
            return None

        self.key = pd.DataFrame(
            {
                aesthetic: scale.map(breaks),
                "label": scale.get_labels(breaks),
                "value": breaks,
            }
        )

        bar = np.linspace(limits[0], limits[1], self.nbin)
        self.bar = pd.DataFrame({"color": scale.map(bar), "value": bar})

        labels = " ".join(str(x) for x in self.key["label"])
        info = "\n".join(
            [
                self.title,
                labels,
                " ".join(self.bar["color"].tolist()),
                self.__class__.__name__,
            ]
        )
        self.hash = hashlib.sha256(info.encode("utf-8")).hexdigest()
        return self

    def merge(self, other):
        """
        Simply discards the other guide
        """
        return self

    def create_geoms(self):
        """
        Return self if colorbar will be drawn and None if not

        This guide is not geom based
        """
        for l in self.plot_layers:
            exclude = set()
            if isinstance(l.show_legend, dict):
                l.show_legend = rename_aesthetics(l.show_legend)
                exclude = {ae for ae, val in l.show_legend.items() if not val}
            elif l.show_legend not in (None, True):
                continue

            matched = self.legend_aesthetics(l)

            # layer uses guide
            if set(matched) - exclude:
                break
        # no break, no layer uses this guide
        else:
            return None

        return self

    def draw(self):
        """
        Draw guide

        Returns
        -------
        out : matplotlib.offsetbox.Offsetbox
            A drawing of this legend
        """
        from matplotlib.offsetbox import (
            HPacker,
            TextArea,
            VPacker,
        )
        from matplotlib.transforms import IdentityTransform

        from .._mpl.offsetbox import DPICorAuxTransformBox

        self.theme = cast("theme", self.theme)

        obverse = slice(0, None)
        reverse = slice(None, None, -1)
        nbars = len(self.bar)
        elements = self.elements
        raster = self.display == "raster"

        colors = self.bar["color"].tolist()
        labels = self.key["label"].tolist()
        targets = self.theme.targets

        # .5 puts the ticks in the middle of the bars when
        # raster=False. So when raster=True the ticks are
        # in between interpolation points and the matching is
        # close though not exactly right.
        _from = self.bar["value"].min(), self.bar["value"].max()
        tick_locations = (
            rescale(self.key["value"], (0.5, nbars - 0.5), _from)
            * elements.key_height
            / nbars
        )

        # With many bins, the ticks approach the edges of the colorbar.
        # This may look odd if there is a border and the top & bottom ticks
        # partly overlap the border only because of floating point arithmetic.
        # This eliminates some of those cases so that user does no have to
        # use llim and ulim
        if nbars >= 150 and len(tick_locations) >= 2:
            tick_locations = [
                np.floor(tick_locations[0]),
                *np.round(tick_locations[1:-1]),
                np.ceil(tick_locations[-1]),
            ]

        if self.reverse:
            colors = colors[::-1]
            labels = labels[::-1]
            tick_locations = elements.key_height - tick_locations[::-1]

        auxbox = DPICorAuxTransformBox(IdentityTransform())

        # title
        title = cast("str", self.title)
        props = {"ha": elements.title.ha, "va": elements.title.va}
        title_box = TextArea(title, textprops=props)
        targets.legend_title = title_box._text  # type: ignore

        # labels
        if not self.elements.text.is_blank:
            texts = add_labels(auxbox, labels, tick_locations, elements)
            targets.legend_text_colorbar = texts

        # colorbar
        if self.display == "rectangles":
            add_segmented_colorbar(auxbox, colors, elements)
        else:
            add_gradient_colorbar(auxbox, colors, elements, raster)

        # ticks
        visible = slice(
            None if self.draw_llim else 1,
            None if self.draw_ulim else -1,
        )
        coll = add_ticks(auxbox, tick_locations[visible], elements)
        targets.legend_ticks = coll

        # frame
        frame = add_frame(auxbox, elements)
        targets.legend_frame = frame

        # title + colorbar(with labels)
        lookup: dict[Side, tuple[type[PackerBase], slice]] = {
            "right": (HPacker, reverse),
            "left": (HPacker, obverse),
            "bottom": (VPacker, reverse),
            "top": (VPacker, obverse),
        }
        packer, slc = lookup[elements.title_position]

        if elements.title.is_blank:
            children: list[Artist] = [auxbox]
        else:
            children = [title_box, auxbox][slc]

        box = packer(
            children=children,
            sep=elements.title.margin,
            align=elements.title.align,
            pad=0,
        )
        return box


guide_colourbar = guide_colorbar


def add_gradient_colorbar(
    auxbox: AuxTransformBox,
    colors: Sequence[str],
    elements: GuideElementsColorbar,
    raster: bool = False,
):
    """
    Add an interpolated gradient colorbar to DrawingArea
    """
    from matplotlib.collections import QuadMesh
    from matplotlib.colors import ListedColormap

    # Special case that arises due to not so useful
    # aesthetic mapping.
    if len(colors) == 1:
        colors = [colors[0], colors[0]]

    # Number of horizontal edges(breaks) in the grid
    # No need to create more nbreak than colors, provided
    # no. of colors = no. of breaks = no. of cmap colors
    # the shading does a perfect interpolation
    nbreak = len(colors)

    if elements.is_vertical:
        colorbar_height = elements.key_height
        colorbar_width = elements.key_width

        mesh_width = 1
        mesh_height = nbreak - 1
        linewidth = colorbar_height / mesh_height
        # Construct rectangular meshgrid
        # The values(Z) at each vertex are just the
        # normalized (onto [0, 1]) vertical distance
        x = np.array([0, colorbar_width])
        y = np.arange(0, nbreak) * linewidth
        X, Y = np.meshgrid(x, y)
        Z = Y / y.max()
    else:
        colorbar_width = elements.key_height
        colorbar_height = elements.key_width

        mesh_width = nbreak - 1
        mesh_height = 1
        linewidth = colorbar_width / mesh_width
        x = np.arange(0, nbreak) * linewidth
        y = np.array([0, colorbar_height])
        X, Y = np.meshgrid(x, y)
        Z = X / x.max()

    # As a 3D (mesh_width x mesh_height x 2) coordinates array
    coordinates = np.stack([X, Y], axis=-1)
    cmap = ListedColormap(colors)
    coll = QuadMesh(
        coordinates,
        antialiased=False,
        shading="gouraud",
        cmap=cmap,
        array=Z.ravel(),
        rasterized=raster,
    )
    auxbox.add_artist(coll)


def add_segmented_colorbar(
    auxbox: AuxTransformBox,
    colors: Sequence[str],
    elements: GuideElementsColorbar,
):
    """
    Add 'non-rastered' colorbar to AuxTransformBox
    """
    from matplotlib.collections import PolyCollection

    nbreak = len(colors)
    if elements.is_vertical:
        colorbar_height = elements.key_height
        colorbar_width = elements.key_width

        linewidth = colorbar_height / nbreak
        verts = []
        x1, x2 = 0, colorbar_width
        for i in range(nbreak):
            y1 = i * linewidth
            y2 = y1 + linewidth
            verts.append(((x1, y1), (x1, y2), (x2, y2), (x2, y1)))
    else:
        colorbar_width = elements.key_height
        colorbar_height = elements.key_width

        linewidth = colorbar_width / nbreak
        verts = []
        y1, y2 = 0, colorbar_height
        for i in range(nbreak):
            x1 = i * linewidth
            x2 = x1 + linewidth
            verts.append(((x1, y1), (x1, y2), (x2, y2), (x2, y1)))

    coll = PolyCollection(
        verts,
        facecolors=colors,
        linewidth=0,
        antialiased=False,
    )
    auxbox.add_artist(coll)


def add_ticks(auxbox, locations, elements) -> LineCollection:
    """
    Add ticks to colorbar
    """
    from matplotlib.collections import LineCollection

    segments = []
    l = elements.ticks_length
    tick_stops = np.array([0.0, l, 1 - l, 1]) * elements.key_width
    if elements.is_vertical:
        x1, x2, x3, x4 = tick_stops
        for y in locations:
            segments.extend(
                [
                    ((x1, y), (x2, y)),
                    ((x3, y), (x4, y)),
                ]
            )
    else:
        y1, y2, y3, y4 = tick_stops
        for x in locations:
            segments.extend(
                [
                    ((x, y1), (x, y2)),
                    ((x, y3), (x, y4)),
                ]
            )

    coll = LineCollection(segments)
    auxbox.add_artist(coll)
    return coll


def add_labels(
    auxbox: AuxTransformBox,
    labels: Sequence[str],
    ys: Sequence[float],
    elements: GuideElementsColorbar,
) -> list[Text]:
    """
    Return Texts added to the auxbox
    """
    from matplotlib.text import Text

    n = len(labels)
    sep = elements.text.margin
    texts: list[Text] = []
    props = {"ha": elements.text.ha, "va": elements.text.va}

    # The horizontal and vertical alignments are set in the theme
    # or dynamically calculates in GuideElements and added to the
    # themeable properties dict
    if elements.is_vertical:
        if elements.text_position == "right":
            xs = [elements.key_width + sep] * n
        else:
            xs = [-sep] * n
    else:
        xs = ys
        if elements.text_position == "bottom":
            ys = [-sep] * n
        else:
            ys = [elements.key_width + sep] * n

    for x, y, s in zip(xs, ys, labels):
        t = Text(x, y, s, **props)
        auxbox.add_artist(t)
        texts.append(t)

    return texts


def add_frame(auxbox, elements):
    """
    Add frame to colorbar
    """
    from matplotlib.patches import Rectangle
    # from .._mpl.patches import InsideStrokedRectangle as Rectangle

    width = elements.key_width
    height = elements.key_height

    if elements.is_horizontal:
        width, height = height, width

    rect = Rectangle((0, 0), width, height, facecolor="none")
    auxbox.add_artist(rect)
    return rect


class GuideElementsColorbar(GuideElements):
    """
    Access & calculate theming for the colobar
    """

    @cached_property
    def text(self):
        size = self.theme.getp(("legend_text_colorbar", "size"))
        ha = self.theme.getp(("legend_text_colorbar", "ha"))
        va = self.theme.getp(("legend_text_colorbar", "va"))
        is_blank = self.theme.T.is_blank("legend_text_colorbar")

        # Default text alignment depends on the direction of the
        # colorbar
        _loc = get_opposite_side(self.text_position)
        if self.is_vertical:
            ha = ha or _loc
            va = va or "center"
        else:
            va = va or _loc
            ha = ha or "center"

        return NS(
            margin=self._text_margin,
            align=None,
            fontsize=size,
            ha=ha,
            va=va,
            is_blank=is_blank,
        )

    @cached_property
    def text_position(self) -> Side:
        if not (position := self.theme.getp("legend_text_position")):
            position = "right" if self.is_vertical else "bottom"

        if self.is_vertical and position not in ("right", "left"):
            msg = (
                "The text position for a vertical legend must be "
                "either left or right."
            )
            raise PlotnineError(msg)
        elif self.is_horizontal and position not in ("bottom", "top"):
            msg = (
                "The text position for a horizonta legend must be "
                "either top or bottom."
            )
            raise PlotnineError(msg)
        return position

    @cached_property
    def key_width(self):
        # We scale up the width only if it inherited its value
        dim = (self.is_vertical and "width") or "height"
        legend_key_dim = f"legend_key_{dim}"
        inherited = self.theme.T.get(legend_key_dim) is None
        scale = 1.45 if inherited else 1
        return np.round(self.theme.getp(legend_key_dim) * scale)

    @cached_property
    def key_height(self):
        # We scale up the height only if it inherited its value
        dim = (self.is_vertical and "height") or "width"
        legend_key_dim = f"legend_key_{dim}"
        inherited = self.theme.T.get(legend_key_dim) is None
        scale = (1.45 * 5) if inherited else 1
        return np.round(self.theme.getp(legend_key_dim) * scale)

    @cached_property
    def frame(self):
        lw = self.theme.getp(("legend_frame", "linewidth"), 0)
        return NS(linewidth=lw)

    @cached_property
    def ticks_length(self):
        return self.theme.getp("legend_ticks_length")

    @cached_property
    def ticks(self):
        lw = self.theme.getp(("legend_ticks", "linewidth"))
        return NS(linewidth=lw)

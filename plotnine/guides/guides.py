from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, fields
from functools import cached_property
from typing import TYPE_CHECKING, Literal, cast
from warnings import warn

import numpy as np
import pandas as pd

from .._utils import ensure_xy_location
from .._utils.registry import Registry
from ..exceptions import PlotnineError, PlotnineWarning
from ..iapi import (
    inside_legend,
    legend_artists,
    legend_justifications_view,
    outside_legend,
)
from ..mapping.aes import rename_aesthetics
from .guide import guide

if TYPE_CHECKING:
    from typing import Literal, Optional, Protocol, Sequence, TypeAlias

    from matplotlib.figure import Figure
    from matplotlib.offsetbox import OffsetBox, PackerBase

    from plotnine import ggplot, guide_colorbar, guide_legend, theme
    from plotnine.iapi import labels_view
    from plotnine.scales.scale import scale
    from plotnine.scales.scales import Scales
    from plotnine.themes.targets import ThemeTargets
    from plotnine.themes.theme import theme as Theme
    from plotnine.typing import (
        Justification,
        LegendPosition,
        NoGuide,
        Orientation,
        ScaledAestheticsName,
        Side,
    )

    LegendOrColorbar: TypeAlias = (
        guide_legend | guide_colorbar | Literal["legend", "colorbar"]
    )
    LegendOnly: TypeAlias = guide_legend | Literal["legend"]

    class LegendOwner(Protocol):
        """
        Anything that can render and host legends

        A `LegendOwner` is the rendering context for a set of guides:
        it provides the theme that styles them and the figure they
        are attached to. Both `ggplot` and `Compose` satisfy this
        contract.

        The properties are declared read-only so Protocol matching
        stays covariant on the attribute types (e.g. `p9Figure`
        satisfies `Figure`).
        """

        @property
        def theme(self) -> Theme: ...

        @property
        def figure(self) -> Figure: ...


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


@dataclass
class guides:
    """
    Guides for each scale

    Used to assign or remove a particular guide to the scale
    of an aesthetic.
    """

    alpha: Optional[LegendOrColorbar | NoGuide] = None
    """Guide for alpha scale."""

    color: Optional[LegendOrColorbar | NoGuide] = None
    """Guide for color scale."""

    fill: Optional[LegendOrColorbar | NoGuide] = None
    """Guide for fill scale."""

    linetype: Optional[LegendOnly | NoGuide] = None
    """Guide for linetype scale."""

    shape: Optional[LegendOnly | NoGuide] = None
    """Guide for shape scale."""

    size: Optional[LegendOnly | NoGuide] = None
    """Guide for size scale."""

    stroke: Optional[LegendOnly | NoGuide] = None
    """Guide for stroke scale."""

    colour: Optional[LegendOnly | NoGuide] = None
    """Guide for colour scale."""

    def __post_init__(self):
        self.plot: ggplot
        self.plot_scales: Scales
        self.plot_labels: labels_view
        self.elements: GuidesElements
        self._lookup: dict[
            tuple[str, ScaledAestheticsName], tuple[scale, guide]
        ] = {}
        if self.colour is not None and self.color is not None:
            raise ValueError("Got a guide for color and colour, choose one.")
        rename_aesthetics(self)

    def __radd__(self, other: ggplot):
        """
        Add guides to the plot

        Parameters
        ----------
        plot :
            ggplot object being created

        Returns
        -------
        :
            ggplot object with guides.
        """
        for f in fields(self):
            if (g := getattr(self, f.name)) is not None:
                setattr(other.guides, f.name, g)

        return other

    def _build(self) -> Sequence[guide]:
        """
        Build the guides

        Returns
        -------
        :
            The individual guides for which the geoms that draw them have
            have been created.
        """
        return self._create_geoms(self._merge(self._train()))

    def _bind_source(self, plot: ggplot):
        """
        Bind to the source plot

        Resolves which guide applies to which aesthetic by inspecting
        the plot's scales, then captures each resolved guide's
        data-source state (layers, mapping).

        Parameters
        ----------
        plot :
            The plot whose scales decide which guides to draw.
        """
        self.plot = plot

        guide_lookup = {
            f.name: g
            for f in fields(self)
            if (g := getattr(self, f.name)) is not None
        }

        for scale in self.plot.scales:
            for ae in scale.aesthetics:
                # The guide for aesthetic 'xxx' is stored
                # in plot.guides['xxx']. The priority for
                # the guides depends on how they are created
                # 1. ... + guides(xxx=guide_blah())
                # 2. ... + scale_xxx(guide=guide_blah())
                # 3. default(either guide_legend or guide_colorbar
                #            depending on the scale type)
                # ae = scale.aesthetics[0]

                # No guide
                if (g := guide_lookup.get(ae)) in ("none", False) or (
                    g is None and (g := scale.guide) is None
                ):
                    continue

                # check the validity of guide.
                # if guide is str, then find the guide object
                if isinstance(g, str):
                    g = Registry[f"guide_{g}"]()
                elif not isinstance(g, guide):
                    raise PlotnineError(f"Unknown guide: {g}")

                g._bind_source(plot)
                self._lookup[(scale.__class__.__name__, ae)] = (scale, g)

    def _bind_owner(self, owner: LegendOwner):
        """
        Bind to the rendering owner

        Captures the rendering context (theme, figure) and propagates
        the owner-binding to every resolved guide.

        Parameters
        ----------
        owner :
            Whoever renders these guides — its theme and figure
            drive layout and attachment.
        """
        self.elements = GuidesElements(owner.theme)
        self._owner_theme = owner.theme
        self._owner_figure = owner.figure
        for _, g in self._lookup.values():
            g.guides_elements = self.elements
            g._bind_owner(owner)

    def _setup(self, plot: ggplot):
        """
        Setup all guides that will be active
        """
        self._bind_source(plot)
        self._bind_owner(plot)

    def _train(self) -> Sequence[guide]:
        """
        Compute all the required guides

        Returns
        -------
        gdefs : list
            Guides for the plots
        """
        gdefs: list[guide] = []
        for (_, ae), (scale, g) in self._lookup.items():
            # Guide turned off
            if not g.elements.position:
                continue

            # check the consistency of the guide and scale.
            if (
                "any" not in g.available_aes
                and scale.aesthetics[0] not in g.available_aes
            ):
                raise PlotnineError(
                    f"{g.__class__.__name__} cannot be used for "
                    f"{scale.aesthetics}"
                )

            # title
            if g.title is None:
                if scale.name:
                    g.title = scale.name
                else:
                    g.title = getattr(self.plot.labels, ae)
                    if g.title is None:
                        warn(
                            f"Cannot generate legend for the {ae!r} "
                            "aesthetic. Make sure you have mapped a "
                            "variable to it",
                            PlotnineWarning,
                        )

            # each guide object trains scale within the object,
            # so Guides (i.e., the container of guides)
            # need not to know about them
            g = g.train(scale, ae)

            if g is not None:
                gdefs.append(g)

        return gdefs

    def _merge(self, gdefs: Sequence[guide]) -> Sequence[guide]:
        """
        Merge overlapped guides

        For example:

        ```python
         from plotnine import *
         p = (
            ggplot(mtcars, aes(y="wt", x="mpg", colour="factor(cyl)"))
            + stat_smooth(aes(fill="factor(cyl)"), method="lm")
            + geom_point()
         )
        ```

        would create two guides with the same hash
        """
        if not gdefs:
            return []

        # group guide definitions by hash, and
        # reduce each group to a single guide
        # using the guide.merge method
        definitions = pd.DataFrame(
            {"gdef": gdefs, "hash": [g.hash for g in gdefs]}
        )
        grouped = definitions.groupby("hash", sort=False)
        gdefs = []
        for name, group in grouped:
            # merge
            gdef = group["gdef"].iloc[0]
            for g in group["gdef"].iloc[1:]:
                gdef = gdef.merge(g)
            gdefs.append(gdef)
        return gdefs

    def _create_geoms(
        self,
        gdefs: Sequence[guide],
    ) -> Sequence[guide]:
        """
        Add geoms to the guide definitions
        """
        return [_g for g in gdefs if (_g := g.create_geoms())]

    def _apply_guide_themes(self, gdefs: list[guide]):
        """
        Apply the theme for each guide
        """
        for g in gdefs:
            g.theme.apply()

    def draw(self) -> Optional[OffsetBox]:
        """
        Draw guides onto the figure

        Returns
        -------
        :matplotlib.offsetbox.Offsetbox | None
            A box that contains all the guides for the plot.
            If there are no guides, **None** is returned.
        """
        if self.elements.position == "none":
            return

        if not (gdefs := self._build()):
            return

        # Order of guides
        # 0 do not sort, any other sorts
        # place the guides according to the guide.order
        default = max(g.order for g in gdefs) + 1
        orders = [default if g.order == 0 else g.order for g in gdefs]
        idx = cast("Sequence[int]", np.argsort(orders))
        gdefs = [gdefs[i] for i in idx]

        # Draw each guide into a box
        # Because we can have more than one guide, we keep record of
        # the drawn artists using lists
        guide_boxes = [g.draw() for g in gdefs]

        self._apply_guide_themes(gdefs)
        legends = assemble_legend_artists(
            gdefs, guide_boxes, self.elements, self._owner_figure
        )
        attach_legend_artists(
            legends, self._owner_figure, self._owner_theme.targets
        )


def assemble_legend_artists(
    gdefs: list[guide],
    boxes: list[PackerBase],
    elements: GuidesElements,
    figure: Figure,
) -> legend_artists:
    """
    Assemble guides into AnchoredOffsetboxes depending on location

    Parameters
    ----------
    gdefs :
        Trained guides whose `_resolved_position_justification`
        decides which side group each lands in.
    boxes :
        The per-guide drawn boxes, one per `gdefs` entry.
    elements :
        Theme-resolved layout elements (direction, box justification,
        margins, spacing).
    figure :
        The figure the offsetboxes will be anchored to.
    """
    from matplotlib.font_manager import FontProperties
    from matplotlib.offsetbox import HPacker, VPacker

    from .._mpl.offsetbox import FlexibleAnchoredOffsetbox

    # Combine all the guides into a single box
    # The direction matters only when there is more than legend
    lookup: dict[Orientation, type[PackerBase]] = {
        "horizontal": HPacker,
        "vertical": VPacker,
    }

    def _anchored_offset_box(boxes: list[PackerBase]):
        """
        Put a group of guides into a single box for drawing
        """
        packer = lookup[elements.box]

        box = packer(
            children=boxes,  # type: ignore
            align=elements.box_just,
            pad=elements.box_margin,
            sep=elements.spacing,
        )

        return FlexibleAnchoredOffsetbox(
            xy_loc=(0.5, 0.5),
            child=box,
            pad=1,
            frameon=False,
            prop=FontProperties(size=1, stretch=0),
            bbox_to_anchor=(0, 0),
            bbox_transform=figure.transFigure,
            borderpad=0.0,
        )

    # Group together guides for each position
    groups: dict[
        tuple[Side, float] | tuple[tuple[float, float], tuple[float, float]],
        list[PackerBase],
    ] = defaultdict(list)

    for g, b in zip(gdefs, boxes):
        groups[g._resolved_position_justification].append(b)

    legends = legend_artists()

    # Create an anchoredoffsetbox for each group/position
    for (position, just), group in groups.items():
        aob = _anchored_offset_box(group)
        if isinstance(position, str) and isinstance(just, (float, int)):
            setattr(legends, position, outside_legend(aob, just))
        else:
            position = cast("tuple[float, float]", position)
            just = cast("tuple[float, float]", just)
            legends.inside.append(inside_legend(aob, just, position))

    return legends


def attach_legend_artists(
    legends: legend_artists,
    figure: Figure,
    theme_targets: ThemeTargets,
):
    """
    Attach legend offsetboxes to the figure and register them

    Parameters
    ----------
    legends :
        The assembled legend artists to attach.
    figure :
        The matplotlib figure to add the offsetboxes to.
    theme_targets :
        Theme targets where the `legends` record is stored for the
        layout engine to pick up.
    """
    for aob in legends.boxes:
        figure.add_artist(aob)
    theme_targets.legends = legends


VALID_JUSTIFICATION_WORDS = {"left", "right", "top", "bottom", "center"}


@dataclass
class GuidesElements:
    """
    Theme elements used when assembling the guides object

    This class is meant to provide convenient access to all the required
    elements having worked out good defaults for the unspecified values.
    """

    theme: theme

    @cached_property
    def box(self) -> Orientation:
        """
        The direction to layout the guides
        """
        if not (box := self.theme.getp("legend_box")):
            box = (
                "vertical"
                if self.position in {"left", "right"}
                else "horizontal"
            )
        return box

    @cached_property
    def position(self) -> LegendPosition | Literal["none"]:
        if (pos := self.theme.getp("legend_position", "right")) == "inside":
            pos = self._position_inside
        return pos

    @cached_property
    def _position_inside(self) -> LegendPosition:
        # We return the position inside the panels when it is explicitly
        # set. Otherwise we return the justification inside the panels.
        # We convert the string (left, right, ...) justifications into
        # locations which justify the legend along the edges of the panel
        # area.
        # Overall when only the inside position is set, the same value is
        # applied to the justification and vice-versa. Always defaulting
        # to a center justification can have the legends close to the
        # edge go out of bounds.
        pos = self.theme.getp("legend_position_inside")
        if isinstance(pos, tuple):
            return pos

        just = self.theme.getp("legend_justification_inside", (0.5, 0.5))
        return ensure_xy_location(just)

    @cached_property
    def box_just(self) -> Justification | Literal["baseline"]:
        if not (box_just := self.theme.getp("legend_box_just")):
            box_just = (
                "left" if self.position in {"left", "right"} else "right"
            )
        return box_just

    @cached_property
    def box_margin(self) -> int:
        return self.theme.getp("legend_box_margin")

    @cached_property
    def spacing(self) -> float:
        return self.theme.getp("legend_spacing")

    @cached_property
    def justification(self) -> legend_justifications_view:
        # Don't bother, the legend has been turned off
        if self.position == "none":
            return legend_justifications_view()

        dim_lookup = {"left": 1, "right": 1, "top": 0, "bottom": 0}

        # Process justification for legend on left, right, top & bottom
        def _lrtb(pos):
            just = self.theme.getp(f"legend_justification_{pos}")
            idx = dim_lookup[pos]
            if just is None:
                just = (0.5, 0.5)
            elif just in VALID_JUSTIFICATION_WORDS:
                just = ensure_xy_location(just)
            elif isinstance(just, (float, int)):
                just = (just, just)
            return just[idx]

        # Process justification for legend inside the panels
        def _inside():
            just = self.theme.getp("legend_justification_inside")
            if just is None:
                return None
            return ensure_xy_location(just)

        # For legends outside the panels, the default justification is
        # the center (0.5). For legends inside the panels, the default
        # is the position. The final value of the position comes from
        # the guide._final_position.
        return legend_justifications_view(
            left=_lrtb("left"),
            right=_lrtb("right"),
            top=_lrtb("top"),
            bottom=_lrtb("bottom"),
            inside=_inside(),
        )

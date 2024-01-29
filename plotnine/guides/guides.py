from __future__ import annotations

from dataclasses import dataclass, fields
from functools import cached_property
from typing import TYPE_CHECKING, cast
from warnings import warn

import numpy as np
import pandas as pd

from .._utils.registry import Registry
from ..exceptions import PlotnineError, PlotnineWarning
from ..mapping.aes import rename_aesthetics
from ..themes import theme
from .guide import guide

if TYPE_CHECKING:
    from typing import Optional, Sequence

    from matplotlib.offsetbox import OffsetBox, PackerBase

    from plotnine import ggplot
    from plotnine.iapi import labels_view
    from plotnine.scales.scales import Scales
    from plotnine.typing import (
        Justification,
        LegendOnly,
        LegendOrColorbar,
        Orientation,
        SidePosition,
        Theme,
    )

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

    Used to assign a particular guide to an aesthetic(s).

    Parameters
    ----------
    kwargs : dict
        aesthetic - guide pairings. e.g
        ```python
        guides(color=guide_colorbar())
        ```
    """

    alpha: Optional[LegendOrColorbar] = None
    color: Optional[LegendOrColorbar] = None
    fill: Optional[LegendOrColorbar] = None
    linetype: Optional[LegendOnly] = None
    shape: Optional[LegendOnly] = None
    size: Optional[LegendOnly] = None
    stroke: Optional[LegendOnly] = None
    colour: Optional[LegendOnly] = None

    def __post_init__(self):
        self.plot: ggplot
        self.plot_scales: Scales
        self.plot_labels: labels_view

        if self.colour and self.color:
            raise ValueError("Got a guide for color and colour, choose one.")

    def __radd__(self, plot: ggplot):
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
            if g := getattr(self, f.name):
                setattr(plot.guides, f.name, g)

        return plot

    def _guide_lookup(self) -> dict[str, guide]:
        """
        Lookup dict for guides that have been set
        """
        return {
            f.name: g for f in fields(self) if (g := getattr(self, f.name))
        }

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

    def _train(self) -> Sequence[guide]:
        """
        Compute all the required guides

        Returns
        -------
        gdefs : list
            Guides for the plots
        """
        gdefs: list[guide] = []
        rename_aesthetics(self)
        guide_lookup = self._guide_lookup()

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
                if not (g := guide_lookup.get(ae, scale.guide)):
                    continue

                # check the validity of guide.
                # if guide is str, then find the guide object
                g = self._setup(g)
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

    def _setup(self, g: str | guide) -> guide:
        """
        Validate guide object
        """
        if isinstance(g, str):
            g = Registry[f"guide_{g}"]()

        if not isinstance(g, guide):
            raise PlotnineError(f"Unknown guide: {g}")

        g.setup(self.plot)
        return g

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
            g.theme = cast(theme, g.theme)
            g.theme.apply()

    def draw(self, plot: ggplot) -> Optional[OffsetBox]:
        """
        Draw guides onto the figure

        Parameters
        ----------
        plot :
            ggplot object

        Returns
        -------
        :matplotlib.offsetbox.Offsetbox | None
            A box that contains all the guides for the plot.
            If there are no guides, **None** is returned.
        """
        from matplotlib.font_manager import FontProperties
        from matplotlib.offsetbox import AnchoredOffsetbox, HPacker, VPacker

        self.plot = plot

        if not (gdefs := self._build()):
            return

        elements = GuidesElements(plot.theme)
        targets = plot.theme.targets

        # Order of guides
        # 0 do not sort, any other sorts
        # place the guides according to the guide.order
        default = max(g.order for g in gdefs) + 1
        orders = [default if g.order == 0 else g.order for g in gdefs]
        idx = np.argsort(orders)
        gdefs = [gdefs[i] for i in idx]

        # Draw each guide into a box
        # Because we can have more than one guide, we keep record of
        # the drawn artists using lists
        guide_boxes = [g.draw() for g in gdefs]

        self._apply_guide_themes(gdefs)

        # Combine all the guides into a single box
        # Direction. It only matters when there is more than legend
        lookup: dict[Orientation, type[PackerBase]] = {
            "horizontal": HPacker,
            "vertical": VPacker,
        }

        packer = lookup[elements.box]
        guides_box = packer(
            children=guide_boxes,
            align=elements.box_just,
            pad=elements.box_margin,
            sep=elements.spacing,
        )

        # Wrap the guides for addition to the figure
        anchored_box = AnchoredOffsetbox(
            loc="center",
            child=guides_box,
            pad=1,
            frameon=False,
            prop=FontProperties(size=0, stretch=0),
            bbox_to_anchor=(0, 0),
            bbox_transform=plot.figure.transFigure,
            borderpad=0.0,
            zorder=99.1,
        )
        targets.legend_background = anchored_box
        plot.figure.add_artist(anchored_box)


@dataclass
class GuidesElements:
    """
    Theme elements used when assembling the guides object

    This class is meant to provide convenient access to all the required
    elements having worked out good defaults for the unspecified values.
    """

    theme: Theme

    @cached_property
    def box(self) -> Orientation:
        """
        The direction to layout the guides
        """
        if not (box := self.theme.getp("legend_box")):
            box = (
                "vertical"
                if self.position in ("right", "left")
                else "horizontal"
            )
        return box

    @cached_property
    def position(self) -> Optional[SidePosition]:
        position = self.theme.getp("legend_position")
        return None if position == "none" else position

    @cached_property
    def box_just(self) -> Justification:
        if not (box_just := self.theme.getp("legend_box_just")):
            box_just = (
                "left" if self.position in ("right", "left") else "right"
            )
        return box_just

    @cached_property
    def box_margin(self) -> int:
        return self.theme.getp("legend_box_margin")

    @cached_property
    def spacing(self) -> float:
        return self.theme.getp("legend_spacing")

"""
Internal API

Specifications for containers that will hold different kinds
of objects with data created when the plot is being built.
"""

from __future__ import annotations

import itertools
from copy import copy
from dataclasses import dataclass, field, fields
from functools import cached_property
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Iterator, Optional, Sequence

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from plotnine.scales.scale import scale
    from plotnine.themes.elements.margin import margin
    from plotnine.typing import (
        CoordRange,
        FloatArrayLike,
        HorizontalJustification,
        ScaledAestheticsName,
        StripPosition,
        VerticalJustification,
    )

    from ._mpl.offsetbox import FlexibleAnchoredOffsetbox


@dataclass
class scale_view:
    """
    Scale information after it has been trained
    """

    scale: scale
    aesthetics: Sequence[ScaledAestheticsName]
    name: Optional[str]
    # Trained limits of the scale
    limits: tuple[float, float] | Sequence[str]
    # Physical size of scale, including expansions
    range: CoordRange
    breaks: Sequence[float] | Sequence[str]
    minor_breaks: FloatArrayLike
    labels: Sequence[str]


@dataclass
class range_view:
    """
    Range information after training
    """

    range: tuple[float, float]
    range_coord: tuple[float, float]


@dataclass
class labels_view:
    """
    Scale labels (incl. caption & title) for the plot
    """

    x: Optional[str] = None
    y: Optional[str] = None
    alpha: Optional[str] = None
    color: Optional[str] = None
    colour: Optional[str] = None
    fill: Optional[str] = None
    linetype: Optional[str] = None
    shape: Optional[str] = None
    size: Optional[str] = None
    stroke: Optional[str] = None
    title: Optional[str] = None
    caption: Optional[str] = None
    subtitle: Optional[str] = None
    tag: Optional[str] = None

    def update(self, other: labels_view):
        """
        Update the labels with those in other
        """
        for name, value in other.iter_set_fields():
            setattr(self, name, value)

    def add_defaults(self, other: labels_view):
        """
        Update labels that are missing with those in other
        """
        for name, value in other.iter_set_fields():
            cur_value = getattr(self, name)
            if cur_value is None:
                setattr(self, name, value)

    def iterfields(self) -> Iterator[tuple[str, Optional[str]]]:
        """
        Return an iterator of all (field, value) pairs
        """
        return ((f.name, getattr(self, f.name)) for f in fields(self))

    def iter_set_fields(self) -> Iterator[tuple[str, str]]:
        """
        Return an iterator of (field, value) pairs of none None values
        """
        return ((k, v) for k, v in self.iterfields() if v is not None)

    def get(self, name: str, default: str) -> str:
        """
        Get label value, return default if value is None
        """
        value = getattr(self, name)
        return str(value) if value is not None else default

    def __contains__(self, name: str) -> bool:
        """
        Return True if name has been set (is not None)
        """
        return getattr(self, name) is not None

    def __repr__(self) -> str:
        """
        Representations without the None values
        """
        nv_pairs = ", ".join(
            f"{name}={repr(value)}" for name, value in self.iter_set_fields()
        )
        return f"{self.__class__.__name__}({nv_pairs})"


@dataclass
class panel_view:
    """
    Information from the trained position scales in a panel
    """

    x: scale_view
    y: scale_view


@dataclass
class panel_ranges:
    """
    Ranges for the panel
    """

    x: tuple[float, float]
    y: tuple[float, float]


@dataclass
class pos_scales:
    """
    Position Scales
    """

    x: scale
    y: scale


@dataclass
class mpl_save_view:
    """
    Everything required to save a matplotlib figure
    """

    figure: Figure
    kwargs: dict[str, Any]

    def __post_init__(self):
        # If savefig.dpi rcparam has been set, it will override
        # the figure dpi which is set in the theme. We make sure
        # our call to savefig will contain the figure dpi.
        if "dpi" not in self.kwargs:
            self.kwargs["dpi"] = self.figure.get_dpi()


@dataclass
class layout_details:
    """
    Layout information
    """

    panel_index: int
    panel: int
    row: int
    col: int
    scale_x: int
    scale_y: int
    axis_x: bool
    axis_y: bool
    variables: dict[str, Any]
    nrow: int
    ncol: int

    @property
    def is_left(self) -> bool:
        """
        Return True if panel is on the left
        """
        return self.col == 1

    @property
    def is_right(self) -> bool:
        """
        Return True if panel is on the right
        """
        return self.col == self.ncol

    @property
    def is_top(self) -> bool:
        """
        Return True if panel is at the top
        """
        return self.row == 1

    @property
    def is_bottom(self) -> bool:
        """
        Return True if Panel is at the bottom
        """
        return self.row == self.nrow


@dataclass
class strip_draw_info:
    """
    Information required to draw strips
    """

    bg_x: float
    """Left of the strip background in transAxes"""

    bg_y: float
    """Bottom of the strip background in transAxes"""

    ha: HorizontalJustification | float
    """Horizontal justification of strip text within the background"""

    va: VerticalJustification | float
    """Vertical justification of strip text within the background"""

    bg_width: float
    """Width of the strip background in transAxes"""

    bg_height: float
    """Height of the strip background in transAxes"""

    margin: margin
    """Strip text margin with the units in lines"""

    strip_align: float
    position: StripPosition
    label: str
    ax: Axes
    rotation: float
    layout: layout_details

    @cached_property
    def is_oneline(self) -> bool:
        """
        Whether the strip text is a single line
        """
        return len(self.label.split("\n")) == 1


@dataclass
class strip_label_details:
    """
    Strip Label Details
    """

    # facet variable: label for the value
    variables: dict[str, str]
    meta: dict[str, Any]  # TODO: use a typeddict

    @staticmethod
    def make(
        layout_info: layout_details,
        vars: Sequence[str],
        location: StripPosition,
    ) -> strip_label_details:
        variables: dict[str, Any] = {
            v: str(layout_info.variables[v]) for v in vars
        }
        meta: dict[str, Any] = {
            "dimension": "cols" if location == "top" else "rows"
        }
        return strip_label_details(variables, meta)

    def __len__(self) -> int:
        """
        Number of variables
        """
        return len(self.variables)

    def __copy__(self) -> strip_label_details:
        """
        Make a copy
        """
        return strip_label_details(self.variables.copy(), self.meta.copy())

    def copy(self) -> strip_label_details:
        """
        Make a copy
        """
        return copy(self)

    def text(self) -> str:
        """
        Strip text

        Join the labels for all the variables along a
        dimension
        """
        return "\n".join(list(self.variables.values()))

    def collapse(self) -> strip_label_details:
        """
        Concatenate all label values into one item
        """
        result = self.copy()
        result.variables = {"value": ", ".join(result.variables.values())}
        return result


@dataclass
class legend_justifications_view:
    """
    Global holder for how the legends should be justified
    """

    left: float = 0.5
    right: float = 0.5
    top: float = 0.5
    bottom: float = 0.5
    inside: Optional[tuple[float, float]] = None


@dataclass
class outside_legend:
    """
    What is required to layout an outside legend
    """

    box: FlexibleAnchoredOffsetbox
    justification: float


@dataclass
class inside_legend:
    """
    What is required to layout an inside legend
    """

    box: FlexibleAnchoredOffsetbox
    justification: tuple[float, float]
    position: tuple[float, float]


@dataclass
class legend_artists:
    """
    Legend artists that are drawn on the figure
    """

    left: Optional[outside_legend] = None
    right: Optional[outside_legend] = None
    top: Optional[outside_legend] = None
    bottom: Optional[outside_legend] = None
    inside: list[inside_legend] = field(default_factory=list)

    @property
    def boxes(self) -> list[FlexibleAnchoredOffsetbox]:
        """
        Return list of all AnchoredOffsetboxes for the legends
        """
        lrtb = (
            l.box for l in (self.left, self.right, self.top, self.bottom) if l
        )
        inside = (l.box for l in self.inside)
        return list(itertools.chain([*lrtb, *inside]))

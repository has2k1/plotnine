from __future__ import annotations

from dataclasses import dataclass, field
from itertools import cycle
from typing import TYPE_CHECKING, Literal, Sequence

from ..composition._types import ComposeAddable

if TYPE_CHECKING:
    from plotnine.typing import Side

    from ._compose import Compose

    GuidesMode = Literal["collect", "keep"]
    AxisMode = Literal["collect", "collect_x", "collect_y", "keep"]


@dataclass(kw_only=True)
class plot_layout(ComposeAddable):
    """
    Customise the layout of plots in a composition
    """

    nrow: int | None = None
    """
    Number of rows
    """

    ncol: int | None = None
    """
    Number of columns
    """

    byrow: bool | None = None
    """
    How to place plots into the grid.
    If None or True, they are placed row by row, left to right.
    If False, they are placed column by column, top to bottom.
    """

    widths: Sequence[float] | None = None
    """
    Relative widths of each column
    """

    heights: Sequence[float] | None = None
    """
    Relative heights of each column
    """

    design: str | None = None
    '''
    Text-grid layout specification

    Each line is one row of the grid; each character is one cell.
    Use `#`, `.`, or a space for empty cells; use any other character
    to label a region. Cells with the same label form a rectangular area that
    hosts one composition item.

    Areas are assigned to items in the sorted order of the label
    characters: the lexicographically first label gets the first
    composition item. Cannot be combined with `nrow` or `ncol`.
    `byrow` is silently ignored.

    Example::

        design = """
            #33#
            #2#4
            11#4
        """
    '''

    guides: GuidesMode | None = None
    """
    How to handle guides in this composition.

    - `"collect"`: dedupe and render guides from descendants once at
      this level.
    - `"keep"`: block any ancestor's collect from reaching this
      subtree.
    - `None` (default): neither collect nor block — propagate any
      ancestor's setting through unchanged.
    """

    axes: AxisMode | None = None
    """
    Axis collection mode for this composition

    Show only the outermost axis on each selected side. Hide the other
    axes with their ticks and tick labels. Plotnine does not verify that
    the plots share a scale.

    - `"collect"`: Collect axes on all four sides.
    - `"collect_x"`: Collect axes on the top and bottom.
    - `"collect_y"`: Collect axes on the left and right.
    - `"keep"` or `None` (default): Keep every plot's axes.
    """

    axis_title: AxisMode | None = None
    """
    Axis title collection mode for this composition

    Collect matching titles from plots that retain an axis on a selected
    side. Keep the title nearest that side and centre it across the panels
    it labels. A hidden axis loses its title; differing titles remain.

    Accepts the same modes as `axes`. `None` inherits the `axes` mode.
    Set a collection mode to collect titles when axes differ, or set
    `"keep"` to collect axes while retaining every title.
    """

    _cmp: Compose = field(init=False, repr=False)
    """
    Composition that this layout is attached to
    """

    def __post_init__(self):
        if self.design is not None and (
            self.nrow is not None or self.ncol is not None
        ):
            raise ValueError(
                "plot_layout(design=...) cannot be combined with nrow or ncol"
            )

    def __radd__(self, cmp: Compose) -> Compose:
        """
        Add plot layout to composition
        """
        cmp.layout = self
        return cmp

    def _setup(self, cmp: Compose):
        """
        Setup default parameters as they are expected by the layout manager

        - Ensure nrow and ncol have values
        - Ensure the widths & heights are set and normalised to mean=1
        """
        from . import Beside, Stack

        # setup nrow & ncol
        if self.design is not None:
            if self.nrow is not None or self.ncol is not None:
                raise ValueError(
                    "plot_layout(design=...) cannot be combined with "
                    "nrow or ncol"
                )
            from ._design import parse_design

            spec = parse_design(self.design)
            if spec.n_regions != len(cmp):
                raise ValueError(
                    f"plot_layout(design=...) has {spec.n_regions} "
                    f"regions but the composition has {len(cmp)} items"
                )
            self.nrow, self.ncol = spec.nrow, spec.ncol
            cmp._design_spec = spec
        elif isinstance(cmp, Beside):
            if self.ncol is None:
                self.ncol = len(cmp)
            elif self.ncol < len(cmp):
                raise ValueError(
                    "Composition has more items than the layout columns."
                )
            if self.nrow is None:
                self.nrow = 1
        elif isinstance(cmp, Stack):
            if self.nrow is None:
                self.nrow = len(cmp)
            elif self.nrow < len(cmp):
                raise ValueError(
                    "Composition has more items than the layout rows."
                )

            if self.ncol is None:
                self.ncol = 1
        else:
            from plotnine.facets.facet_wrap import wrap_dims

            self.nrow, self.ncol = wrap_dims(len(cmp), self.nrow, self.ncol)

        nrow, ncol = self.nrow, self.ncol

        # byrow
        if self.byrow is None:
            self.byrow = True

        # setup widths & heights
        ws, hs = self.widths, self.heights
        if ws is None:
            ws = (1 / ncol,) * ncol
        elif len(ws) != ncol:
            ws = repeat(ws, ncol)

        if hs is None:
            hs = (1 / nrow,) * nrow
        elif len(hs) != nrow:
            hs = repeat(hs, nrow)

        self.widths = normalise(ws)
        self.heights = normalise(hs)

    def update(self, other: plot_layout):
        """
        Update this layout with the contents of other
        """
        if other.design is not None:
            self.design = other.design
            # Re-_setup will populate these from the new design.
            self.nrow = None
            self.ncol = None
        if other.widths:
            self.widths = other.widths
        if other.heights:
            self.heights = other.heights
        if other.ncol:
            self.ncol = other.ncol
            self.design = None
        if other.nrow:
            self.nrow = other.nrow
            self.design = None
        if other.byrow is not None:
            self.byrow = other.byrow
        if other.guides is not None:
            self.guides = other.guides
        if other.axes is not None:
            self.axes = other.axes
        if other.axis_title is not None:
            self.axis_title = other.axis_title


def repeat(seq: Sequence[float], n: int) -> list[float]:
    """
    Ensure returned sequence has n values, repeat as necessary
    """
    return [val for _, val in zip(range(n), cycle(seq))]


def normalise(seq: Sequence[float]) -> list[float]:
    """
    Normalise seq so that the mean is 1
    """
    mean = sum(seq) / len(seq)
    if mean == 0:
        raise ValueError("Cannot rescale: mean is zero")
    return [x / mean for x in seq]


def collected_sides(mode: AxisMode | None) -> frozenset[Side]:
    """
    Return the sides selected by an axis collection mode

    Parameters
    ----------
    mode :
        Value of `plot_layout(axes=...)` or `plot_layout(axis_title=...)`.

    Returns
    -------
    :
        Sides to collect. Empty for `"keep"` and `None`.
    """
    if mode is None or mode == "keep":
        return frozenset()
    elif mode == "collect_x":
        return frozenset({"top", "bottom"})
    elif mode == "collect_y":
        return frozenset({"left", "right"})
    else:
        return frozenset({"top", "bottom", "left", "right"})

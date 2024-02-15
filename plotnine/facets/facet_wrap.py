from __future__ import annotations

import re
import typing
from warnings import warn

import numpy as np
import pandas as pd

from .._utils import join_keys, match
from ..exceptions import PlotnineError, PlotnineWarning
from .facet import (
    add_missing_facets,
    combine_vars,
    eval_facet_vars,
    facet,
    layout_null,
)
from .strips import Strips, strip

if typing.TYPE_CHECKING:
    from typing import Literal, Optional, Sequence

    from matplotlib.axes import Axes

    from plotnine.iapi import layout_details


class facet_wrap(facet):
    """
    Wrap 1D Panels onto 2D surface

    Parameters
    ----------
    facets :
        Variables to groupby and plot on different panels.
        If a string formula is used it should be right sided,
        e.g `"~ a + b"`, `("a", "b")`
    nrow : int, default=None
        Number of rows
    ncol : int, default=None
        Number of columns
    scales :
        Whether `x` or `y` scales should be allowed (free)
        to vary according to the data on each of the panel.
    shrink :
        Whether to shrink the scales to the output of the
        statistics instead of the raw data.
    labeller :
        How to label the facets. A string value if it should be
        one of `["label_value", "label_both", "label_context"]`{.py}.
    as_table :
        If `True`, the facets are laid out like a table with
        the highest values at the bottom-right. If `False`
        the facets are laid out like a plot with the highest
        value a the top-right
    drop :
        If `True`, all factor levels not used in the data
        will automatically be dropped. If `False`, all
        factor levels will be shown, regardless of whether
        or not they appear in the data.
    dir :
        Direction in which to layout the panels. `h` for
        horizontal and `v` for vertical.
    """

    def __init__(
        self,
        facets: Optional[str | Sequence[str]] = None,
        *,
        nrow: Optional[int] = None,
        ncol: Optional[int] = None,
        scales: Literal["fixed", "free", "free_x", "free_y"] = "fixed",
        shrink: bool = True,
        labeller: Literal[
            "label_value", "label_both", "label_context"
        ] = "label_value",
        as_table: bool = True,
        drop: bool = True,
        dir: Literal["h", "v"] = "h",
    ):
        super().__init__(
            scales=scales,
            shrink=shrink,
            labeller=labeller,
            as_table=as_table,
            drop=drop,
            dir=dir,
        )
        self.vars = parse_wrap_facets(facets)
        self._nrow, self._ncol = check_dimensions(nrow, ncol)

    def compute_layout(
        self,
        data: list[pd.DataFrame],
    ) -> pd.DataFrame:
        if not self.vars:
            self.nrow, self.ncol = 1, 1
            return layout_null()

        base = combine_vars(data, self.environment, self.vars, drop=self.drop)
        n = len(base)
        dims = wrap_dims(n, self._nrow, self._ncol)
        _id = np.arange(1, n + 1)

        if self.dir == "v":
            dims = dims[::-1]

        if self.as_table:
            row = (_id - 1) // dims[1] + 1
        else:
            row = dims[0] - (_id - 1) // dims[1]

        col = (_id - 1) % dims[1] + 1

        layout = pd.DataFrame(
            {
                "PANEL": pd.Categorical(range(1, n + 1)),
                "ROW": row.astype(int),
                "COL": col.astype(int),
            }
        )
        if self.dir == "v":
            layout.rename(columns={"ROW": "COL", "COL": "ROW"}, inplace=True)

        layout = pd.concat([layout, base], axis=1)
        self.nrow = layout["ROW"].nunique()
        self.ncol = layout["COL"].nunique()
        n = layout.shape[0]

        # Add scale identification
        layout["SCALE_X"] = range(1, n + 1) if self.free["x"] else 1
        layout["SCALE_Y"] = range(1, n + 1) if self.free["y"] else 1

        # Figure out where axes should go.
        # The bottom-most row of each column and the left most
        # column of each row
        x_idx = [df["ROW"].idxmax() for _, df in layout.groupby("COL")]
        y_idx = [df["COL"].idxmin() for _, df in layout.groupby("ROW")]
        layout["AXIS_X"] = False
        layout["AXIS_Y"] = False
        _loc = layout.columns.get_loc
        layout.iloc[x_idx, _loc("AXIS_X")] = True  # type: ignore
        layout.iloc[y_idx, _loc("AXIS_Y")] = True  # type: ignore

        if self.free["x"]:
            layout.loc[:, "AXIS_X"] = True

        if self.free["y"]:
            layout.loc[:, "AXIS_Y"] = True

        return layout

    def map(self, data: pd.DataFrame, layout: pd.DataFrame) -> pd.DataFrame:
        if not len(data):
            data["PANEL"] = pd.Categorical(
                [], categories=layout["PANEL"].cat.categories, ordered=True
            )
            return data

        facet_vals = eval_facet_vars(data, self.vars, self.environment)
        data, facet_vals = add_missing_facets(
            data, layout, self.vars, facet_vals
        )

        # assign each point to a panel
        if len(facet_vals) and len(facet_vals.columns):
            keys = join_keys(facet_vals, layout, self.vars)
            data["PANEL"] = match(keys["x"], keys["y"], start=1)
        else:
            # Special case of no facetting
            data["PANEL"] = 1

        # matching dtype
        data["PANEL"] = pd.Categorical(
            data["PANEL"],
            categories=layout["PANEL"].cat.categories,
            ordered=True,
        )

        data.reset_index(drop=True, inplace=True)
        return data

    def make_strips(self, layout_info: layout_details, ax: Axes) -> Strips:
        if not self.vars:
            return Strips([])

        s = strip(self.vars, layout_info, self, ax, "top")
        return Strips([s])


def check_dimensions(
    nrow: Optional[int], ncol: Optional[int]
) -> tuple[int | None, int | None]:
    """
    Verify dimensions of the facet
    """
    if nrow is not None:
        if nrow < 1:
            warn(
                "'nrow' must be greater than 0. "
                "Your value has been ignored.",
                PlotnineWarning,
            )
            nrow = None
        else:
            nrow = int(nrow)

    if ncol is not None:
        if ncol < 1:
            warn(
                "'ncol' must be greater than 0. "
                "Your value has been ignored.",
                PlotnineWarning,
            )
            ncol = None
        else:
            ncol = int(ncol)

    return nrow, ncol


def parse_wrap_facets(facets: Optional[str | Sequence[str]]) -> Sequence[str]:
    """
    Return list of facetting variables
    """
    if facets is None:
        return []
    elif isinstance(facets, str):
        if "~" in facets:
            return parse_wrap_facets_old(facets)  # formala
        else:
            return [facets]
    return facets


def parse_wrap_facets_old(facets: str | Sequence[str]) -> Sequence[str]:
    """
    Return list of facetting variables

    This handles the old & silently deprecated r-style formulas
    """
    valid_forms = ["~ var1", "~ var1 + var2"]
    error_msg = "Valid formula for 'facet_wrap' look like" f" {valid_forms}"

    if isinstance(facets, (list, tuple)):
        return facets

    if not isinstance(facets, str):
        raise PlotnineError(error_msg)

    if "~" in facets:
        variables_pattern = r"(\w+(?:\s*\+\s*\w+)*|\.)"
        pattern = rf"\s*~\s*{variables_pattern}\s*"
        match = re.match(pattern, facets)
        if not match:
            raise PlotnineError(error_msg)

        facets = [var.strip() for var in match.group(1).split("+")]
    elif re.match(r"\w+", facets):
        # allow plain string as the variable name
        facets = [facets]
    else:
        raise PlotnineError(error_msg)

    return facets


def wrap_dims(
    n: int, nrow: Optional[int] = None, ncol: Optional[int] = None
) -> tuple[int, int]:
    """
    Wrap dimensions
    """
    if nrow is None:
        if ncol is None:
            return n_to_nrow_ncol(n)
        else:
            nrow = int(np.ceil(n / ncol))

    if ncol is None:
        ncol = int(np.ceil(n / nrow))

    if not nrow * ncol >= n:
        raise PlotnineError(
            "Allocated fewer panels than are required. "
            "Make sure the number of rows and columns can "
            "hold all the plot panels."
        )
    return (nrow, ncol)


def n_to_nrow_ncol(n: int) -> tuple[int, int]:
    """
    Compute the rows and columns given the number of plots.
    """
    if n <= 3:
        nrow, ncol = 1, n
    elif n <= 6:
        nrow, ncol = 2, (n + 1) // 2
    elif n <= 12:
        nrow, ncol = 3, (n + 2) // 3
    else:
        ncol = int(np.ceil(np.sqrt(n)))
        nrow = int(np.ceil(n / ncol))
    return (nrow, ncol)

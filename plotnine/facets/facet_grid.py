from __future__ import annotations

import typing

import numpy as np
import pandas as pd

from .._utils import add_margins, cross_join, join_keys, match, ninteraction
from ..exceptions import PlotnineError
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
    from plotnine.typing import FacetSpaceRatios


class facet_grid(facet):
    """
    Wrap 1D Panels onto 2D surface

    Parameters
    ----------
    rows :
        Variable expressions along the rows of the facets/panels.
        Each expression is evaluated within the context of the dataframe.
    cols :
        Variable expressions along the columns of the facets/panels.
        Each expression is evaluated within the context of the dataframe.
    margins :
        variable names to compute margins for.
        True will compute all possible margins.
    space :
        Control the size of the  `x` or `y` sides of the panels.
        The size also depends to the `scales` parameter.

        If a string, it should be one of
        `['fixed', 'free', 'free_x', 'free_y']`{.py}.

        If a `dict`, it indicates the relative facet size ratios such as:

        ```python
        {"x": [1, 2], "y": [3, 1, 1]}
        ```

        This means that in the horizontal direction, the second panel
        will be twice the length of the first. In the vertical direction
        the top facet will be the 3 times longer then the second and
        third facets.

        Note that the number of dimensions in the list must equal the
        number of facets that will be produced.
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
    """

    def __init__(
        self,
        rows: Optional[str | Sequence[str]] = None,
        cols: Optional[str | Sequence[str]] = None,
        *,
        margins: bool | Sequence[str] = False,
        scales: Literal["fixed", "free", "free_x", "free_y"] = "fixed",
        space: (
            Literal["fixed", "free", "free_x", "free_y"] | FacetSpaceRatios
        ) = "fixed",
        shrink: bool = True,
        labeller: Literal[
            "label_value", "label_both", "label_context"
        ] = "label_value",
        as_table: bool = True,
        drop: bool = True,
    ):
        facet.__init__(
            self,
            scales=scales,
            shrink=shrink,
            labeller=labeller,
            as_table=as_table,
            drop=drop,
        )
        self.rows, self.cols = parse_grid_rows_cols(rows, cols)
        self.space = space
        self.margins = margins

    def _make_figure(self):
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec

        layout = self.layout
        space = self.space
        ratios = {}

        # Calculate the width (x) & height (y) ratios for space=free[xy]
        if isinstance(space, str):
            if space in {"free", "free_x"}:
                pidx: list[int] = (
                    layout.layout.sort_values("COL")
                    .drop_duplicates("COL")
                    .index.tolist()
                )
                panel_views = [layout.panel_params[i] for i in pidx]
                ratios["width_ratios"] = [
                    np.ptp(pv.x.range) for pv in panel_views
                ]

            if space in {"free", "free_y"}:
                pidx = (
                    layout.layout.sort_values("ROW")
                    .drop_duplicates("ROW")
                    .index.tolist()
                )
                panel_views = [layout.panel_params[i] for i in pidx]
                ratios["height_ratios"] = [
                    np.ptp(pv.y.range) for pv in panel_views
                ]

        if isinstance(self.space, dict):
            if len(self.space["x"]) != self.ncol:
                raise ValueError(
                    "The number of x-ratios for the facet space sizes "
                    "should match the number of columns."
                )

            if len(self.space["y"]) != self.nrow:
                raise ValueError(
                    "The number of y-ratios for the facet space sizes "
                    "should match the number of rows."
                )

            ratios["width_ratios"] = self.space.get("x")
            ratios["height_ratios"] = self.space.get("y")

        return plt.figure(), GridSpec(self.nrow, self.ncol, **ratios)

    def compute_layout(self, data: list[pd.DataFrame]) -> pd.DataFrame:
        if not self.rows and not self.cols:
            self.nrow, self.ncol = 1, 1
            return layout_null()

        base_rows = combine_vars(
            data, self.environment, self.rows, drop=self.drop
        )

        if not self.as_table:
            # Reverse the order of the rows
            base_rows = base_rows[::-1]
        base_cols = combine_vars(
            data, self.environment, self.cols, drop=self.drop
        )

        base = cross_join(base_rows, base_cols)

        if self.margins:
            base = add_margins(base, (self.rows, self.cols), self.margins)
            base = base.drop_duplicates().reset_index(drop=True)

        n = len(base)
        panel = ninteraction(base, drop=True)
        panel = pd.Categorical(panel, categories=range(1, n + 1))

        if self.rows:
            rows = ninteraction(base[self.rows], drop=True)
        else:
            rows = [1] * len(panel)

        if self.cols:
            cols = ninteraction(base[self.cols], drop=True)
        else:
            cols = [1] * len(panel)

        layout = pd.DataFrame(
            {
                "PANEL": panel,
                "ROW": rows,
                "COL": cols,
            }
        )
        layout = pd.concat([layout, base], axis=1)
        layout = layout.sort_values("PANEL")
        layout.reset_index(drop=True, inplace=True)

        # Relax constraints, if necessary
        layout["SCALE_X"] = layout["COL"] if self.free["x"] else 1
        layout["SCALE_Y"] = layout["ROW"] if self.free["y"] else 1
        layout["AXIS_X"] = layout["ROW"] == layout["ROW"].max()
        layout["AXIS_Y"] = layout["COL"] == layout["COL"].min()

        self.nrow = layout["ROW"].max()
        self.ncol = layout["COL"].max()
        return layout

    def map(self, data: pd.DataFrame, layout: pd.DataFrame) -> pd.DataFrame:
        if not len(data):
            data["PANEL"] = pd.Categorical(
                [], categories=layout["PANEL"].cat.categories, ordered=True
            )
            return data

        vars = (*self.rows, *self.cols)
        margin_vars: tuple[list[str], list[str]] = (
            list(data.columns.intersection(self.rows)),
            list(data.columns.intersection(self.cols)),
        )
        data = add_margins(data, margin_vars, self.margins)

        facet_vals = eval_facet_vars(data, vars, self.environment)
        data, facet_vals = add_missing_facets(data, layout, vars, facet_vals)

        # assign each point to a panel
        if len(facet_vals) and len(facet_vals.columns):
            keys = join_keys(facet_vals, layout, vars)
            data["PANEL"] = match(keys["x"], keys["y"], start=1)
        else:
            # Special case of no facetting
            data["PANEL"] = 1

        # matching dtype and
        # the categories(panel numbers) for the data should be in the
        # same order as the panels. i.e the panels are the reference,
        # they "know" the right order
        data["PANEL"] = pd.Categorical(
            data["PANEL"],
            categories=layout["PANEL"].cat.categories,
            ordered=True,
        )

        data.reset_index(drop=True, inplace=True)
        return data

    def make_strips(self, layout_info: layout_details, ax: Axes) -> Strips:
        lst = []
        if layout_info.is_top and self.cols:
            s = strip(self.cols, layout_info, self, ax, "top")
            lst.append(s)
        if layout_info.is_right and self.rows:
            s = strip(self.rows, layout_info, self, ax, "right")
            lst.append(s)
        return Strips(lst)


def parse_grid_rows_cols(
    rows: Optional[str | Sequence[str]] = None,
    cols: Optional[str | Sequence[str]] = None,
) -> tuple[list[str], list[str]]:
    """
    Return the rows & cols that make up the grid
    """
    if cols is None and isinstance(rows, str):  # formula
        return parse_grid_facets_old(rows)

    if cols is None:
        cols = []
    elif isinstance(cols, str):
        cols = [cols]

    if rows is None:
        rows = []
    elif isinstance(rows, str):
        rows = [rows]

    return list(rows), list(cols)


def parse_grid_facets_old(
    facets: str | tuple[str | Sequence[str], str | Sequence[str]],
) -> tuple[list[str], list[str]]:
    """
    Return two lists of facetting variables, for the rows & columns

    This parse the old & silently deprecated style.
    """
    valid_seqs = [
        "(var1,)",
        "('var1', '.')",
        "('var1', 'var2')",
        "('.', 'var1')",
        "((var1, var2), (var3, var4))",
    ]
    error_msg_s = (
        "Valid sequences for specifying 'facets' look like" f" {valid_seqs}"
    )

    valid_forms = [
        "var1",
        "var1 ~ .",
        "var1 ~ var2",
        ". ~ var1",
        "var1 + var2 ~ var3 + var4",
        ". ~ func(var1) + func(var2)",
        ". ~ func(var1+var3) + func(var2)",
    ] + valid_seqs
    error_msg_f = "Valid formula for 'facet_grid' look like" f" {valid_forms}"

    if not isinstance(facets, str):
        if len(facets) == 1:
            rows = ensure_list_spec(facets[0])
            cols = []
        elif len(facets) == 2:
            rows = ensure_list_spec(facets[0])
            cols = ensure_list_spec(facets[1])
        else:
            raise PlotnineError(error_msg_s)
        return list(rows), list(cols)

    if "~" not in facets:
        rows = ensure_list_spec(facets)
        return list(rows), []

    # Example of allowed formulae
    # "c ~ a + b'
    # '. ~ func(a) + func(b)'
    # 'func(c) ~ func(a+1) + func(b+2)'
    try:
        lhs, rhs = facets.split("~")
    except ValueError as e:
        raise PlotnineError(error_msg_f) from e
    else:
        lhs = lhs.strip()
        rhs = rhs.strip()

    rows = ensure_list_spec(lhs)
    cols = ensure_list_spec(rhs)
    return list(rows), list(cols)


def ensure_list_spec(term: Sequence[str] | str) -> Sequence[str]:
    """
    Convert a str specification to a list spec

    e.g.
    'a' -> ['a']
    'a + b' -> ['a', 'b']
    '.' -> []
    '' -> []
    """
    if isinstance(term, str):
        splitter = " + " if " + " in term else "+"
        if term in [".", ""]:
            return []
        return [var.strip() for var in term.split(splitter)]
    else:
        return term

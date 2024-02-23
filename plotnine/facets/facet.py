from __future__ import annotations

import itertools
import types
import typing
from copy import copy, deepcopy

import numpy as np
import pandas as pd
import pandas.api.types as pdtypes

from .._utils import cross_join, match
from ..exceptions import PlotnineError
from ..scales.scales import Scales
from .strips import Strips

if typing.TYPE_CHECKING:
    from typing import Any, Literal, Optional, Sequence

    import numpy.typing as npt
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from matplotlib.gridspec import GridSpec

    from plotnine import ggplot, theme
    from plotnine.coords.coord import coord
    from plotnine.facets.layout import Layout
    from plotnine.iapi import layout_details, panel_view
    from plotnine.layer import Layers
    from plotnine.mapping import Environment
    from plotnine.scales.scale import scale
    from plotnine.typing import CanBeStripLabellingFunc


class facet:
    """
    Base class for all facets

    Parameters
    ----------
    scales :
        Whether `x` or `y` scales should be allowed (free)
        to vary according to the data on each of the panel.
    shrink :
        Whether to shrink the scales to the output of the
        statistics instead of the raw data. Default is `True`.
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

    # number of columns
    ncol: int

    # number of rows
    nrow: int

    as_table = True
    drop = True
    shrink = True

    # Which axis scales are free
    free: dict[Literal["x", "y"], bool]

    # A dict of parameters created depending on the data
    # (Intended for extensions)
    params: dict[str, Any]

    # Theme object, automatically updated before drawing the plot
    theme: theme

    # Figure object on which the facet panels are created
    figure: Figure

    # coord object, automatically updated before drawing the plot
    coordinates: coord

    # layout object, automatically updated before drawing the plot
    layout: Layout

    # Axes
    axs: list[Axes]

    # ggplot object that the facet belongs to
    plot: ggplot

    # Facet strips
    strips: Strips

    grid_spec: GridSpec

    # The plot environment
    environment: Environment

    def __init__(
        self,
        scales: Literal["fixed", "free", "free_x", "free_y"] = "fixed",
        shrink: bool = True,
        labeller: CanBeStripLabellingFunc = "label_value",
        as_table: bool = True,
        drop: bool = True,
        dir: Literal["h", "v"] = "h",
    ):
        from .labelling import as_labeller

        self.shrink = shrink
        self.labeller = as_labeller(labeller)
        self.as_table = as_table
        self.drop = drop
        self.dir = dir
        self.free = {
            "x": scales in ("free_x", "free"),
            "y": scales in ("free_y", "free"),
        }

    def __radd__(self, plot: ggplot) -> ggplot:
        """
        Add facet to ggplot object
        """
        plot.facet = copy(self)
        plot.facet.environment = plot.environment
        return plot

    def setup(self, plot: ggplot):
        self.plot = plot
        self.layout = plot.layout

        if hasattr(plot, "figure"):
            self.figure, self.axs = plot.figure, plot.axs
        else:
            self.figure, self.axs = self.make_figure()

        self.coordinates = plot.coordinates
        self.theme = plot.theme
        self.layout.axs = self.axs
        self.strips = Strips.from_facet(self)
        return self.figure, self.axs

    def setup_data(self, data: list[pd.DataFrame]) -> list[pd.DataFrame]:
        """
        Allow the facet to manipulate the data

        Parameters
        ----------
        data :
            Data for each of the layers

        Returns
        -------
        :
            Data for each of the layers

        Notes
        -----
        This method will be called after [](`~plotnine.facet.setup_params`),
        therefore the `params` property will be set.
        """
        return data

    def setup_params(self, data: list[pd.DataFrame]):
        """
        Create facet parameters

        Parameters
        ----------
        data :
            Plot data and data for the layers
        """
        self.params = {}

    def init_scales(
        self,
        layout: pd.DataFrame,
        x_scale: Optional[scale] = None,
        y_scale: Optional[scale] = None,
    ) -> types.SimpleNamespace:
        scales = types.SimpleNamespace()

        if x_scale is not None:
            n = layout["SCALE_X"].max()
            scales.x = Scales([x_scale.clone() for i in range(n)])

        if y_scale is not None:
            n = layout["SCALE_Y"].max()
            scales.y = Scales([y_scale.clone() for i in range(n)])

        return scales

    def map(self, data: pd.DataFrame, layout: pd.DataFrame) -> pd.DataFrame:
        """
        Assign a data points to panels

        Parameters
        ----------
        data :
            Data for a layer
        layout :
            As returned by self.compute_layout

        Returns
        -------
        :
            Data with all points mapped to the panels
            on which they will be plotted.
        """
        msg = "{} should implement this method."
        raise NotImplementedError(msg.format(self.__class__.__name__))

    def compute_layout(
        self,
        data: list[pd.DataFrame],
    ) -> pd.DataFrame:
        """
        Compute layout

        Parameters
        ----------
        data :
            Dataframe for a each layer
        """
        msg = "{} should implement this method."
        raise NotImplementedError(msg.format(self.__class__.__name__))

    def finish_data(self, data: pd.DataFrame, layout: Layout) -> pd.DataFrame:
        """
        Modify data before it is drawn out by the geom

        The default is to return the data without modification.
        Subclasses should override this method as the require.

        Parameters
        ----------
        data :
            A single layer's data.
        layout :
            Layout

        Returns
        -------
        :
            Modified layer data
        """
        return data

    def train_position_scales(self, layout: Layout, layers: Layers) -> facet:
        """
        Compute ranges for the x and y scales
        """
        _layout = layout.layout
        panel_scales_x = layout.panel_scales_x
        panel_scales_y = layout.panel_scales_y

        # loop over each layer, training x and y scales in turn
        for layer in layers:
            data = layer.data
            match_id = match(data["PANEL"], _layout["PANEL"])
            if panel_scales_x:
                x_vars = list(
                    set(panel_scales_x[0].aesthetics) & set(data.columns)
                )
                # the scale index for each data point
                SCALE_X = _layout["SCALE_X"].iloc[match_id].tolist()
                panel_scales_x.train(data, x_vars, SCALE_X)

            if panel_scales_y:
                y_vars = list(
                    set(panel_scales_y[0].aesthetics) & set(data.columns)
                )
                # the scale index for each data point
                SCALE_Y = _layout["SCALE_Y"].iloc[match_id].tolist()
                panel_scales_y.train(data, y_vars, SCALE_Y)

        return self

    def make_strips(self, layout_info: layout_details, ax: Axes) -> Strips:
        """
        Create strips for the facet

        Parameters
        ----------
        layout_info :
            Layout information. Row from the layout table

        ax :
            Axes to label
        """
        return Strips()

    def set_limits_breaks_and_labels(self, panel_params: panel_view, ax: Axes):
        """
        Add limits, breaks and labels to the axes

        Parameters
        ----------
        panel_params :
            range information for the axes
        ax :
            Axes
        """
        from .._mpl.ticker import MyFixedFormatter

        def _inf_to_none(
            t: tuple[float, float],
        ) -> tuple[float | None, float | None]:
            """
            Replace infinities with None
            """
            a = t[0] if np.isfinite(t[0]) else None
            b = t[1] if np.isfinite(t[1]) else None
            return (a, b)

        theme = self.theme

        # limits
        ax.set_xlim(*_inf_to_none(panel_params.x.range))
        ax.set_ylim(*_inf_to_none(panel_params.y.range))

        if typing.TYPE_CHECKING:
            assert callable(ax.set_xticks)
            assert callable(ax.set_yticks)

        # breaks, labels
        ax.set_xticks(panel_params.x.breaks, panel_params.x.labels)
        ax.set_yticks(panel_params.y.breaks, panel_params.y.labels)

        # minor breaks
        ax.set_xticks(panel_params.x.minor_breaks, minor=True)
        ax.set_yticks(panel_params.y.minor_breaks, minor=True)

        # When you manually set the tick labels MPL changes the locator
        # so that it no longer reports the x & y positions
        # Fixes https://github.com/has2k1/plotnine/issues/187
        ax.xaxis.set_major_formatter(MyFixedFormatter(panel_params.x.labels))
        ax.yaxis.set_major_formatter(MyFixedFormatter(panel_params.y.labels))

        margin = theme.getp(("axis_text_x", "margin"))
        pad_x = margin.get_as("t", "pt")

        margin = theme.getp(("axis_text_y", "margin"))
        pad_y = margin.get_as("r", "pt")

        ax.tick_params(axis="x", which="major", pad=pad_x)
        ax.tick_params(axis="y", which="major", pad=pad_y)

    def __deepcopy__(self, memo: dict[Any, Any]) -> facet:
        """
        Deep copy without copying the dataframe and environment
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        # don't make a deepcopy of the figure & the axes
        shallow = {"figure", "axs", "first_ax", "last_ax"}
        for key, item in old.items():
            if key in shallow:
                new[key] = item
                memo[id(new[key])] = new[key]
            else:
                new[key] = deepcopy(item, memo)

        return result

    def _make_figure(self) -> tuple[Figure, GridSpec]:
        """
        Create figure & gridspec
        """
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec

        return plt.figure(), GridSpec(self.nrow, self.ncol)

    def make_figure(self) -> tuple[Figure, list[Axes]]:
        """
        Create and return Matplotlib figure and subplot axes
        """
        num_panels = len(self.layout.layout)
        axsarr = np.empty((self.nrow, self.ncol), dtype=object)

        # Create figure & gridspec
        figure, gs = self._make_figure()
        self.grid_spec = gs

        # Create axes
        it = itertools.product(range(self.nrow), range(self.ncol))
        for i, (row, col) in enumerate(it):
            axsarr[row, col] = figure.add_subplot(gs[i])

        # axsarr = np.array([
        #     figure.add_subplot(gs[i])
        #     for i in range(self.nrow * self.ncol)
        # ]).reshape((self.nrow, self.ncol))

        # Rearrange axes
        # They are ordered to match the positions in the layout table
        if self.dir == "h":
            order: Literal["C", "F"] = "C"
            if not self.as_table:
                axsarr = axsarr[::-1]
        elif self.dir == "v":
            order = "F"
            if not self.as_table:
                axsarr = np.array([row[::-1] for row in axsarr])
        else:
            raise ValueError(f'Bad value `dir="{self.dir}"` for direction')

        axs = axsarr.ravel(order)

        # Delete unused axes
        for ax in axs[num_panels:]:
            figure.delaxes(ax)
        axs = axs[:num_panels]
        return figure, list(axs)

    def _aspect_ratio(self) -> Optional[float]:
        """
        Return the aspect_ratio
        """
        aspect_ratio = self.theme.getp("aspect_ratio")
        if aspect_ratio == "auto":
            # If the panels have different limits the coordinates
            # cannot compute a common aspect ratio
            if not self.free["x"] and not self.free["y"]:
                aspect_ratio = self.coordinates.aspect(
                    self.layout.panel_params[0]
                )
            else:
                aspect_ratio = None

        return aspect_ratio


def combine_vars(
    data: list[pd.DataFrame],
    environment: Environment,
    vars: Sequence[str],
    drop: bool = True,
) -> pd.DataFrame:
    """
    Generate all combinations of data needed for facetting

    The first data frame in the list should be the default data
    for the plot. Other data frames in the list are ones that are
    added to the layers.
    """
    if len(vars) == 0:
        return pd.DataFrame()

    # For each layer, compute the facet values
    values = [
        eval_facet_vars(df, vars, environment) for df in data if df is not None
    ]

    # Form the base data frame which contains all combinations
    # of facetting variables that appear in the data
    has_all = [x.shape[1] == len(vars) for x in values]
    if not any(has_all):
        raise PlotnineError(
            "At least one layer must contain all variables "
            "used for facetting"
        )
    base = pd.concat([x for i, x in enumerate(values) if has_all[i]], axis=0)
    base = base.drop_duplicates()

    if not drop:
        base = unique_combs(base)

    # sorts according to order of factor levels
    base = base.sort_values(base.columns.tolist())

    # Systematically add on missing combinations
    for i, value in enumerate(values):
        if has_all[i] or len(value.columns) == 0:
            continue
        old = base.loc[:, list(base.columns.difference(value.columns))]
        new = value.loc[
            :, list(base.columns.intersection(value.columns))
        ].drop_duplicates()

        if not drop:
            new = unique_combs(new)

        base = pd.concat([base, cross_join(old, new)], ignore_index=True)

    if len(base) == 0:
        raise PlotnineError("Faceting variables must have at least one value")

    base = base.reset_index(drop=True)
    return base


def unique_combs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate all possible combinations of the values in the columns
    """

    def _unique(s: pd.Series[Any]) -> npt.NDArray[Any] | pd.Index:
        if isinstance(s.dtype, pdtypes.CategoricalDtype):
            return s.cat.categories
        return s.unique()

    # List of unique values from every column
    lst = (_unique(x) for _, x in df.items())
    rows = list(itertools.product(*lst))
    _df = pd.DataFrame(rows, columns=df.columns)

    # preserve the column dtypes
    for col in df:
        t = df[col].dtype
        _df[col] = _df[col].astype(t, copy=False)
    return _df


def layout_null() -> pd.DataFrame:
    """
    Layout Null
    """
    layout = pd.DataFrame(
        {
            "PANEL": pd.Categorical([1]),
            "ROW": 1,
            "COL": 1,
            "SCALE_X": 1,
            "SCALE_Y": 1,
            "AXIS_X": True,
            "AXIS_Y": True,
        }
    )
    return layout


def add_missing_facets(
    data: pd.DataFrame,
    layout: pd.DataFrame,
    vars: Sequence[str],
    facet_vals: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Add missing facets
    """
    # When in a dataframe some layer does not have all
    # the facet variables, add the missing facet variables
    # and create new data where the points(duplicates) are
    # present in all the facets
    missing_facets = list(set(vars) - set(facet_vals.columns.tolist()))
    if missing_facets:
        to_add = layout.loc[:, missing_facets].drop_duplicates()
        to_add.reset_index(drop=True, inplace=True)

        # a point for each facet, [0, 1, ..., n-1, 0, 1, ..., n-1, ...]
        data_rep = np.tile(np.arange(len(data)), len(to_add))
        # a facet for each point, [0, 0, 0, 1, 1, 1, ... n-1, n-1, n-1]
        facet_rep = np.repeat(np.arange(len(to_add)), len(data))

        data = data.iloc[data_rep, :].reset_index(drop=True)
        facet_vals = facet_vals.iloc[data_rep, :].reset_index(drop=True)
        to_add = to_add.iloc[facet_rep, :].reset_index(drop=True)
        facet_vals = pd.concat(
            [facet_vals, to_add], axis=1, ignore_index=False
        )

    return data, facet_vals


def eval_facet_vars(
    data: pd.DataFrame, vars: Sequence[str], env: Environment
) -> pd.DataFrame:
    """
    Evaluate facet variables

    Parameters
    ----------
    data :
        Factet dataframe
    vars :
        Facet variables
    env :
        Plot environment

    Returns
    -------
    :
        Facet values that correspond to the specified
        variables.
    """

    # To allow expressions in facet formula
    def I(value: Any) -> Any:
        return value

    env = env.with_outer_namespace({"I": I})
    facet_vals = pd.DataFrame(index=data.index)

    for name in vars:
        if name in data:
            # This is a limited solution. If a keyword is
            # part of an expression it will fail in the
            # else statement below
            res = data[name]
        elif str.isidentifier(name):
            # All other non-statements
            continue
        else:
            # Statements
            try:
                res = env.eval(name, inner_namespace=data)
            except NameError:
                continue
        facet_vals[name] = res

    return facet_vals

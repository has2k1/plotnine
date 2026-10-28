from __future__ import annotations

import itertools
import types
import typing
from copy import copy, deepcopy

import narwhals as nw
import numpy as np

from .._mpl.axes import p9Axes
from .._utils import cross_join, frame, match
from .._utils.frame import native_io
from ..exceptions import PlotnineError
from ..mapping.evaluation import eval_string
from ..scales.scales import Scales
from .strips import Strips

if typing.TYPE_CHECKING:
    from typing import Any, Literal, Optional, Sequence

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from plotnine import ggplot, theme
    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine._utils.frame import DataFrame
    from plotnine.coords.coord import coord
    from plotnine.facets.labelling import CanBeStripLabellingFunc
    from plotnine.facets.layout import Layout
    from plotnine.iapi import layout_details
    from plotnine.layer import Layers
    from plotnine.mapping import Environment
    from plotnine.scales.scale import scale


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
        allowed_scales = ["fixed", "free", "free_x", "free_y"]
        if scales not in allowed_scales:
            raise ValueError(
                f"Argument `scales` must be one of {allowed_scales}."
            )
        self.free = {
            "x": scales in ("free_x", "free"),
            "y": scales in ("free_y", "free"),
        }

    def __radd__(self, other: ggplot) -> ggplot:
        """
        Add facet to ggplot object
        """
        other.facet = copy(self)
        other.facet.environment = other.environment
        return other

    def setup(self, plot: ggplot):
        self.plot = plot
        self.layout = plot.built.layout
        self.figure = plot.figure

        if hasattr(plot, "axs"):
            gs, self.axs = plot._sub_gridspec, plot.axs
        else:
            gs, self.axs = self._make_axes()

        self.coordinates = plot.coordinates
        self.theme = plot.theme
        self.layout.axs = self.axs
        self.strips = Strips.from_facet(self)
        return gs, self.axs

    def setup_data(self, data: list[DataFrame]) -> list[DataFrame]:
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

    def setup_params(self, data: list[DataFrame]):
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
        layout: DataFrame,
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

    def map(self, data: DataFrame, layout: DataFrame) -> DataFrame:
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
        data: list[DataFrame],
        scales: Scales,
    ) -> DataFrame:
        """
        Compute layout

        Parameters
        ----------
        data :
            Dataframe for a each layer
        scales :
            The plot's scales
        """
        msg = "{} should implement this method."
        raise NotImplementedError(msg.format(self.__class__.__name__))

    def finish_data(self, data: DataFrame, layout: Layout) -> DataFrame:
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
        layout_panels = _layout["PANEL"].to_list()
        layout_scale_x = _layout["SCALE_X"].to_numpy()
        layout_scale_y = _layout["SCALE_Y"].to_numpy()

        # loop over each layer, training x and y scales in turn
        for layer in layers:
            data = layer.data
            columns = set(frame.to_frame(data).columns)
            asis = layer.asis
            match_id = match(frame.as_numpy(data["PANEL"]), layout_panels)
            if panel_scales_x:
                x_aes = set(panel_scales_x[0].aesthetics)
                x_vars = list((x_aes & columns) - asis)
                # the scale index for each data point
                SCALE_X = layout_scale_x[match_id].tolist()
                panel_scales_x.train(data, x_vars, SCALE_X)

            if panel_scales_y:
                y_aes = set(panel_scales_y[0].aesthetics)
                y_vars = list((y_aes & columns) - asis)
                # the scale index for each data point
                SCALE_Y = layout_scale_y[match_id].tolist()
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
        shallow = {"axs", "first_ax", "last_ax"}
        for key, item in old.items():
            if key in shallow:
                new[key] = item
                memo[id(new[key])] = new[key]
            else:
                new[key] = deepcopy(item, memo)

        return result

    def _make_gridspec(self):
        """
        Create gridspec for the panels
        """
        from plotnine._mpl.gridspec import p9GridSpec

        return p9GridSpec(
            self.nrow, self.ncol, self.figure, nest_into=self.plot._gridspec[0]
        )

    def _make_axes(self) -> tuple[p9GridSpec, list[Axes]]:
        """
        Create and return subplot axes
        """
        num_panels = len(self.layout.layout)
        axsarr = np.empty((self.nrow, self.ncol), dtype=object)
        gs = self._make_gridspec()

        # Create axes
        projection = (
            p9Axes.name
            if self.plot.coordinates._projection is None
            else self.plot.coordinates._projection
        )
        it = itertools.product(range(self.nrow), range(self.ncol))
        for i, (row, col) in enumerate(it):
            axsarr[row, col] = self.figure.add_subplot(
                gs[i], projection=projection
            )

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
            self.figure.delaxes(ax)
        axs = axs[:num_panels]
        return gs, list(axs)

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


@native_io
def combine_vars(
    data: list[DataFrame],
    environment: Environment,
    vars: Sequence[str],
    drop: bool = True,
) -> DataFrame:
    """
    Generate all combinations of data needed for facetting

    The first data frame in the list should be the default data
    for the plot. Other data frames in the list are ones that are
    added to the layers.
    """
    data = [df for df in data if df is not None]
    backend = data[0].implementation
    if len(vars) == 0:
        return frame.frame(backend=backend)

    # For each layer, compute the facet values
    values = [
        frame.convert(eval_facet_vars(df, vars, environment), backend)
        for df in data
    ]

    # Form the base data frame which contains all combinations
    # of facetting variables that appear in the data
    has_all = [len(x.columns) == len(vars) for x in values]
    if not any(has_all):
        raise PlotnineError(
            "At least one layer must contain all variables used for facetting"
        )
    base = frame.concat(
        [x.select(vars) for i, x in enumerate(values) if has_all[i]]
    )
    base = base.unique(maintain_order=True)

    if not drop:
        base = unique_combs(base)

    # sorts according to order of factor levels
    base = frame.sort(base, base.columns)

    # Systematically add on missing combinations
    for i, value in enumerate(values):
        if has_all[i] or len(value.columns) == 0:
            continue
        old = base.select([c for c in base.columns if c not in value.columns])
        new = value.select(
            [c for c in base.columns if c in value.columns]
        ).unique(maintain_order=True)

        if not drop:
            new = unique_combs(new)

        base = frame.concat([base, cross_join(old, new)])

    if len(base) == 0:
        raise PlotnineError("Faceting variables must have at least one value")

    return base


def unique_combs(df: DataFrame) -> DataFrame:
    """
    Generate all possible combinations of the values in the columns
    """

    def _unique(s: nw.Series[Any]) -> list[Any]:
        if frame.is_categorical(s):
            return frame.levels(s)
        return s.unique(maintain_order=True).to_list()

    # List of unique values from every column
    lst = [_unique(df[col]) for col in df.columns]
    rows = list(itertools.product(*lst))
    impl = df.implementation

    # preserve the column dtypes
    columns = []
    for i, col in enumerate(df.columns):
        s = df[col]
        values = [row[i] for row in rows]
        if frame.is_categorical(s):
            columns.append(
                frame.categorical(
                    values,
                    frame.levels(s),
                    ordered=frame.is_ordinal(s),
                    name=col,
                    backend=impl,
                )
            )
        else:
            columns.append(
                frame.series(values, col, backend=impl, dtype=s.dtype)
            )
    return frame.frame({s.name: s for s in columns}, backend=impl)


def layout_null(backend: frame.Implementation) -> DataFrame:
    """
    Layout Null
    """
    return frame.frame(
        {
            "PANEL": [1],
            "ROW": 1,
            "COL": 1,
            "SCALE_X": 1,
            "SCALE_Y": 1,
            "AXIS_X": True,
            "AXIS_Y": True,
            "AXIS_X_SEC": True,
            "AXIS_Y_SEC": True,
        },
        backend=backend,
    )


def add_missing_facets(
    data: DataFrame,
    layout: DataFrame,
    vars: Sequence[str],
    facet_vals: DataFrame,
) -> tuple[DataFrame, DataFrame]:
    """
    Add missing facets
    """
    # When in a dataframe some layer does not have all
    # the facet variables, add the missing facet variables
    # and create new data where the points(duplicates) are
    # present in all the facets
    missing_facets = [v for v in vars if v not in facet_vals.columns]
    if missing_facets:
        to_add = frame.convert(
            layout.select(missing_facets).unique(maintain_order=True),
            data.implementation,
        )

        # a point for each facet, [0, 1, ..., n-1, 0, 1, ..., n-1, ...]
        data_rep = np.tile(np.arange(len(data)), len(to_add))
        # a facet for each point, [0, 0, 0, 1, 1, 1, ... n-1, n-1, n-1]
        facet_rep = np.repeat(np.arange(len(to_add)), len(data))

        data = frame.take(data, data_rep)
        to_add = frame.take(to_add, facet_rep)
        if len(facet_vals.columns):
            facet_vals = nw.concat(
                [frame.take(facet_vals, data_rep), to_add], how="horizontal"
            )
        else:
            facet_vals = to_add

    return data, facet_vals


def eval_facet_vars(
    data: DataFrame, vars: Sequence[str], env: Environment
) -> DataFrame:
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
    facet_vals = {}

    for name in vars:
        if name in data.columns:
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
                res = eval_string(name, data, env, name)
            except PlotnineError as e:
                if isinstance(e.__cause__, NameError):
                    continue
                raise
        facet_vals[name] = res

    if not facet_vals:
        return frame.frame(backend=data.implementation)
    return frame.frame(facet_vals, backend=data.implementation, n=len(data))

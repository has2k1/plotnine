from __future__ import annotations

import typing
from copy import deepcopy
from itertools import chain, repeat

import pandas as pd

from ..exceptions import PlotnineError
from ..layer import layer
from ..mapping.aes import is_valid_aesthetic, rename_aesthetics
from ..mapping.evaluation import evaluate
from ..positions.position import position
from ..stats.stat import stat
from ..utils import (
    Registry,
    copy_keys,
    data_mapping_as_kwargs,
    is_list_like,
    is_string,
    remove_missing,
)

if typing.TYPE_CHECKING:
    from typing import Any

    from plotnine.iapi import panel_view
    from plotnine.typing import (
        Aes,
        Axes,
        Coord,
        DataLike,
        DrawingArea,
        EvalEnvironment,
        Ggplot,
        Layer,
        Layout,
    )


class geom(metaclass=Registry):
    """Base class of all Geoms"""

    __base__ = True

    #: Default aesthetics for the geom
    DEFAULT_AES: dict[str, Any] = {}

    #: Required aesthetics for the geom
    REQUIRED_AES: set[str] = set()

    #: Required aesthetics for the geom
    NON_MISSING_AES: set[str] = set()

    #: Required parameters for the geom
    DEFAULT_PARAMS: dict[str, Any] = {}

    #: geom/layer specific dataframe
    data: DataLike

    #: mappings i.e. :py:`aes(x='col1', fill='col2')`
    mapping: Aes

    aes_params: dict[str, Any] = {}  # setting of aesthetic
    params: dict[str, Any]  # parameter settings

    # Plot namespace, it gets its value when the plot is being
    # built.
    environment: EvalEnvironment

    # The geom responsible for the legend if draw_legend is
    # not implemented
    legend_geom: str = "point"

    # Documentation for the aesthetics. It is added under the
    # documentation for mapping parameter. Use {aesthetics}
    # placeholder to insert a table for all the aesthetics and
    # their default values.
    _aesthetics_doc: str = "{aesthetics_table}"

    def __init__(
        self,
        mapping: Aes | None = None,
        data: DataLike | None = None,
        **kwargs: Any,
    ):
        kwargs = rename_aesthetics(kwargs)
        kwargs = data_mapping_as_kwargs((data, mapping), kwargs)
        self._kwargs = kwargs  # Will be used to create stat & layer

        # separate aesthetics and parameters
        self.aes_params = copy_keys(kwargs, {}, self.aesthetics())
        self.params = copy_keys(kwargs, deepcopy(self.DEFAULT_PARAMS))
        self.mapping = kwargs["mapping"]
        self.data = kwargs["data"]
        self._stat = stat.from_geom(self)
        self._position = position.from_geom(self)
        self._verify_arguments(kwargs)  # geom, stat, layer

    @staticmethod
    def from_stat(stat: stat) -> geom:
        """
        Return an instantiated geom object

        geoms should not override this method.

        Parameters
        ----------
        stat : stat
            `stat`

        Returns
        -------
        out : geom
            A geom object

        Raises
        ------
        PlotnineError
            If unable to create a `geom`.
        """
        name = stat.params["geom"]

        if isinstance(name, geom):
            return name

        if isinstance(name, type) and issubclass(name, geom):
            klass = name
        elif is_string(name):
            if not name.startswith("geom_"):
                name = f"geom_{name}"
            klass = Registry[name]
        else:
            raise PlotnineError(f"Unknown geom of type {type(name)}")

        return klass(stat=stat, **stat._kwargs)

    @classmethod
    def aesthetics(cls: type[geom]) -> set[str]:
        """
        Return all the aesthetics for this geom

        geoms should not override this method.
        """
        main = cls.DEFAULT_AES.keys() | cls.REQUIRED_AES
        other = {"group"}
        # Need to recognize both spellings
        if "color" in main:
            other.add("colour")
        if "outlier_color" in main:
            other.add("outlier_colour")
        return main | other

    def __deepcopy__(self, memo: dict[Any, Any]) -> geom:
        """
        Deep copy without copying the self.data dataframe

        geoms should not override this method.
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        # don't make a deepcopy of data, or environment
        shallow = {"data", "_kwargs", "environment"}
        for key, item in old.items():
            if key in shallow:
                new[key] = old[key]
                memo[id(new[key])] = new[key]
            else:
                new[key] = deepcopy(old[key], memo)

        return result

    def setup_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Modify the data before drawing takes place

        This function is called *before* position adjustments are done.
        It is used by geoms to create the final aesthetics used for
        drawing. The base class method does nothing, geoms can override
        this method for two reasons:

        1. The ``stat`` does not create all the aesthetics (usually
           position aesthetics) required for drawing the ``geom``,
           but those aesthetics can be computed from the available
           data. For example :class:`~plotnine.geoms.geom_boxplot`
           and :class:`~plotnine.geoms.geom_violin`.

        2. The ``geom`` inherits from another ``geom`` (superclass) which
           does the drawing and the superclass requires certain aesthetics
           to be present in the data. For example
           :class:`~plotnine.geoms.geom_tile` and
           :class:`~plotnine.geoms.geom_area`.

        Parameters
        ----------
        data : dataframe
            Data used for drawing the geom.

        Returns
        -------
        out : dataframe
            Data used for drawing the geom.
        """
        return data

    def use_defaults(
        self, data: pd.DataFrame, aes_modifiers: dict[str, Any]
    ) -> pd.DataFrame:
        """
        Combine data with defaults and set aesthetics from parameters

        geoms should not override this method.

        Parameters
        ----------
        data : dataframe
            Data used for drawing the geom.
        aes_modifiers : dict
            Aesthetics

        Returns
        -------
        out : dataframe
            Data used for drawing the geom.
        """
        missing_aes = (
            self.DEFAULT_AES.keys()
            - self.aes_params.keys()
            - set(data.columns.to_list())
        )

        # Not in data and not set, use default
        for ae in missing_aes:
            data[ae] = self.DEFAULT_AES[ae]

        # Evaluate/Modify the mapped aesthetics
        evaled = evaluate(aes_modifiers, data, self.environment)
        for ae in evaled.columns.intersection(data.columns):
            data[ae] = evaled[ae]

        if "PANEL" in data:
            num_panels = len(data["PANEL"].unique())
        else:
            num_panels = 1

        # Aesthetics set as parameters to the geom/stat
        for ae, value in self.aes_params.items():
            try:
                data[ae] = value
            except ValueError:
                # sniff out the special cases, like custom
                # tupled linetypes, shapes and colors
                if is_valid_aesthetic(value, ae):
                    data[ae] = [value] * len(data)
                elif num_panels > 1 and is_list_like(value):
                    data[ae] = list(chain(*repeat(value, num_panels)))
                else:
                    msg = "'{}' does not look like a " "valid value for `{}`"
                    raise PlotnineError(msg.format(value, ae))

        return data

    def draw_layer(
        self, data: pd.DataFrame, layout: Layout, coord: Coord, **params: Any
    ):
        """
        Draw layer across all panels

        geoms should not override this method.

        Parameters
        ----------
        data : DataFrame
            DataFrame specific for this layer
        layout : Layout
            Layout object created when the plot is getting
            built
        coord : coord
            Type of coordinate axes
        params : dict
            Combined *geom* and *stat* parameters. Also
            includes the stacking order of the layer in
            the plot (*zorder*)
        """
        for pid, pdata in data.groupby("PANEL", observed=True):
            if len(pdata) == 0:
                continue
            ploc = pdata["PANEL"].iat[0] - 1
            panel_params = layout.panel_params[ploc]
            ax = layout.axs[ploc]
            self.draw_panel(pdata, panel_params, coord, ax, **params)

    def draw_panel(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: Coord,
        ax: Axes,
        **params: Any,
    ):
        """
        Plot all groups

        For efficiency, geoms that do not need to partition
        different groups before plotting should override this
        method and avoid the groupby.

        Parameters
        ----------
        data : dataframe
            Data to be plotted by this geom. This is the
            dataframe created in the plot_build pipeline.
        panel_params : panel_view
            The scale information as may be required by the
            axes. At this point, that information is about
            ranges, ticks and labels. Attributes are of interest
            to the geom are::

                'panel_params.x.range'  # tuple
                'panel_params.y.range'  # tuple

        coord : coord
            Coordinate (e.g. coord_cartesian) system of the
            geom.
        ax : axes
            Axes on which to plot.
        params : dict
            Combined parameters for the geom and stat. Also
            includes the 'zorder'.
        """
        for _, gdata in data.groupby("group"):
            gdata.reset_index(inplace=True, drop=True)
            self.draw_group(gdata, panel_params, coord, ax, **params)

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: Coord,
        ax: Axes,
        **params: Any,
    ):
        """
        Plot data belonging to a group.

        Parameters
        ----------
        data : dataframe
            Data to be plotted by this geom. This is the
            dataframe created in the plot_build pipeline.
        panel_params : panel_view
            The scale information as may be required by the
            axes. At this point, that information is about
            ranges, ticks and labels. Keys of interest to
            the geom are::

                'x_range'  # tuple
                'y_range'  # tuple

        coord : coord
            Coordinate (e.g. coord_cartesian) system of the
            geom.
        ax : axes
            Axes on which to plot.
        params : dict
            Combined parameters for the geom and stat. Also
            includes the 'zorder'.
        """
        msg = "The geom should implement this method."
        raise NotImplementedError(msg)

    @staticmethod
    def draw_unit(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: Coord,
        ax: Axes,
        **params: Any,
    ):
        """
        Plot data belonging to a unit.

        A matplotlib plot function may require that an aethestic
        have a single unique value. e.g. linestyle='dashed' and
        not linestyle=['dashed', 'dotted', ...].
        A single call to such a function can only plot lines with
        the same linestyle. However, if the plot we want has more
        than one line with different linestyles, we need to group
        the lines with the same linestyle and plot them as one
        unit. In this case, draw_group calls this function to do
        the plotting. For an example see
        :class:`~plotnine.geoms.geom_point`.

        Parameters
        ----------
        data : dataframe
            Data to be plotted by this geom. This is the
            dataframe created in the plot_build pipeline.
        panel_params : panel_view
            The scale information as may be required by the
            axes. At this point, that information is about
            ranges, ticks and labels. Keys of interest to
            the geom are::

                'x_range'  # tuple
                'y_range'  # tuple

            In rare cases a geom may need access to the x or y scales.
            Those are available at::

                'scales'   # SimpleNamespace

        coord : coord
            Coordinate (e.g. coord_cartesian) system of the
            geom.
        ax : axes
            Axes on which to plot.
        params : dict
            Combined parameters for the geom and stat. Also
            includes the 'zorder'.
        """
        msg = "The geom should implement this method."
        raise NotImplementedError(msg)

    def __radd__(self, gg: Ggplot) -> Ggplot:
        """
        Add layer representing geom object on the right

        Parameters
        ----------
        gg : ggplot
            ggplot object

        Returns
        -------
        out : ggplot
            ggplot object with added layer.
        """
        gg += self.to_layer()  # Add layer
        return gg

    def to_layer(self) -> Layer:
        """
        Make a layer that represents this geom

        Returns
        -------
        out : layer
            Layer
        """
        return layer.from_geom(self)

    def _verify_arguments(self, kwargs: dict[str, Any]):
        """
        Verify arguments passed to the geom
        """
        geom_stat_args = kwargs.keys() | self._stat._kwargs.keys()
        unknown = (
            geom_stat_args
            - self.aesthetics()
            - self.DEFAULT_PARAMS.keys()  # geom aesthetics
            - self._stat.aesthetics()  # geom parameters
            - self._stat.DEFAULT_PARAMS.keys()  # stat aesthetics
            - {  # stat parameters
                "data",
                "mapping",
                "show_legend",  # layer parameters
                "inherit_aes",
                "raster",
            }
        )  # layer parameters
        if unknown:
            msg = (
                "Parameters {}, are not understood by "
                "either the geom, stat or layer."
            )
            raise PlotnineError(msg.format(unknown))

    def handle_na(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Remove rows with NaN values

        geoms that infer extra information from missing values
        should override this method. For example
        :class:`~plotnine.geoms.geom_path`.

        Parameters
        ----------
        data : dataframe
            Data

        Returns
        -------
        out : dataframe
            Data without the NaNs.

        Notes
        -----
        Shows a warning if the any rows are removed and the
        `na_rm` parameter is False. It only takes into account
        the columns of the required aesthetics.
        """
        return remove_missing(
            data,
            self.params["na_rm"],
            list(self.REQUIRED_AES | self.NON_MISSING_AES),
            self.__class__.__name__,
        )

    @staticmethod
    def draw_legend(
        data: pd.Series[Any], da: DrawingArea, lyr: Layer
    ) -> DrawingArea:
        """
        Draw a rectangle in the box

        Parameters
        ----------
        data : Series
            Data Row
        da : DrawingArea
            Canvas
        lyr : layer
            Layer

        Returns
        -------
        out : DrawingArea
        """
        msg = "The geom should implement this method."
        raise NotImplementedError(msg)

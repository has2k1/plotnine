from __future__ import annotations

import typing
from abc import ABC
from contextlib import suppress
from copy import deepcopy
from itertools import chain, repeat

import numpy as np

from .._utils import (
    data_mapping_as_kwargs,
    remove_missing,
)
from .._utils.registry import Register, Registry
from ..exceptions import PlotnineError
from ..layer import layer
from ..mapping.aes import rename_aesthetics
from ..mapping.evaluation import evaluate
from ..positions.position import position
from ..stats.stat import stat

if typing.TYPE_CHECKING:
    from typing import Any

    import pandas as pd
    from matplotlib.axes import Axes
    from matplotlib.offsetbox import DrawingArea

    from plotnine import aes, ggplot
    from plotnine.coords.coord import coord
    from plotnine.facets.layout import Layout
    from plotnine.iapi import panel_view
    from plotnine.mapping import Environment
    from plotnine.typing import DataLike


class geom(ABC, metaclass=Register):
    """Base class of all Geoms"""

    DEFAULT_AES: dict[str, Any] = {}
    """Default aesthetics for the geom"""

    REQUIRED_AES: set[str] = set()
    """Required aesthetics for the geom"""

    NON_MISSING_AES: set[str] = set()
    """Required aesthetics for the geom"""

    DEFAULT_PARAMS: dict[str, Any] = {}
    """Required parameters for the geom"""

    data: DataLike
    """Geom/layer specific dataframe"""

    mapping: aes
    """Mappings i.e. `aes(x="col1", fill="col2")`{.py}"""

    aes_params: dict[str, Any] = {}  # setting of aesthetic
    params: dict[str, Any]  # parameter settings

    # Plot namespace, it gets its value when the plot is being
    # built.
    environment: Environment

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
        mapping: aes | None = None,
        data: DataLike | None = None,
        **kwargs: Any,
    ):
        kwargs = rename_aesthetics(kwargs)
        kwargs = data_mapping_as_kwargs((data, mapping), kwargs)
        self._kwargs = kwargs  # Will be used to create stat & layer

        # separate aesthetics and parameters
        self.aes_params = {
            ae: kwargs[ae] for ae in self.aesthetics() & set(kwargs)
        }
        self.params = self.DEFAULT_PARAMS | {
            k: v for k, v in kwargs.items() if k in self.DEFAULT_PARAMS
        }
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
        stat :
            `stat`

        Returns
        -------
        :
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
        elif isinstance(name, str):
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
                new[key] = item
                memo[id(new[key])] = new[key]
            else:
                new[key] = deepcopy(item, memo)

        return result

    def setup_params(self, data: pd.DataFrame):
        """
        Override this method to verify and/or adjust parameters

        Parameters
        ----------
        data :
            Data
        """

    def setup_aes_params(self, data: pd.DataFrame):
        """
        Override this method to verify and/or adjust aesthetic parameters

        Parameters
        ----------
        data :
            Data
        """

    def setup_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Modify the data before drawing takes place

        This function is called *before* position adjustments are done.
        It is used by geoms to create the final aesthetics used for
        drawing. The base class method does nothing, geoms can override
        this method for two reasons:

        1. The `stat` does not create all the aesthetics (usually
           position aesthetics) required for drawing the `geom`,
           but those aesthetics can be computed from the available
           data. For example [](`~plotnine.geoms.geom_boxplot`)
           and [](`~plotnine.geoms.geom_violin`).

        2. The `geom` inherits from another `geom` (superclass) which
           does the drawing and the superclass requires certain aesthetics
           to be present in the data. For example
           [](`~plotnine.geoms.geom_tile`) and
           [](`~plotnine.geoms.geom_area`).

        Parameters
        ----------
        data :
            Data used for drawing the geom.

        Returns
        -------
        :
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
        data :
            Data used for drawing the geom.
        aes_modifiers :
            Aesthetics to evaluate

        Returns
        -------
        :
            Data used for drawing the geom.
        """
        from plotnine.mapping import _atomic as atomic
        from plotnine.mapping._atomic import ae_value

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

        num_panels = len(data["PANEL"].unique()) if "PANEL" in data else 1
        across_panels = num_panels > 1 and not self.params["inherit_aes"]

        # Aesthetics set as parameters in the geom/stat
        for ae, value in self.aes_params.items():
            if isinstance(value, (str, int, float, np.integer, np.floating)):
                data[ae] = value
            elif isinstance(value, ae_value):
                data[ae] = value * len(data)
            elif across_panels:
                value = list(chain(*repeat(value, num_panels)))
                data[ae] = value
            else:
                # Try to make sense of aesthetics whose values can be tuples
                # or sequences of sorts.
                ae_value_cls: type[ae_value] | None = getattr(atomic, ae, None)
                if ae_value_cls:
                    with suppress(ValueError):
                        data[ae] = ae_value_cls(value) * len(data)
                        continue

                # This should catch the aesthetic assignments to
                # non-numeric or non-string values or sequence of values.
                # e.g. x=datetime, x=Sequence[datetime],
                #      x=Sequence[float], shape=Sequence[str]
                try:
                    data[ae] = value
                except ValueError as e:
                    msg = f"'{ae}={value}' does not look like a valid value"
                    raise PlotnineError(msg) from e

        return data

    def draw_layer(self, data: pd.DataFrame, layout: Layout, coord: coord):
        """
        Draw layer across all panels

        geoms should not override this method.

        Parameters
        ----------
        data :
            DataFrame specific for this layer
        layout :
            Layout object created when the plot is getting
            built
        coord :
            Type of coordinate axes
        params :
            Combined *geom* and *stat* parameters. Also
            includes the stacking order of the layer in
            the plot (*zorder*)
        """
        for pid, pdata in data.groupby("PANEL", observed=True):
            if len(pdata) == 0:
                continue
            ploc = pdata["PANEL"].iloc[0] - 1
            panel_params = layout.panel_params[ploc]
            ax = layout.axs[ploc]
            self.draw_panel(pdata, panel_params, coord, ax)

    def draw_panel(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
    ):
        """
        Plot all groups

        For efficiency, geoms that do not need to partition
        different groups before plotting should override this
        method and avoid the groupby.

        Parameters
        ----------
        data :
            Data to be plotted by this geom. This is the
            dataframe created in the plot_build pipeline.
        panel_params :
            The scale information as may be required by the
            axes. At this point, that information is about
            ranges, ticks and labels. Attributes are of interest
            to the geom are:

            ```python
            "panel_params.x.range"  # tuple
            "panel_params.y.range"  # tuple
            ```
        coord :
            Coordinate (e.g. coord_cartesian) system of the geom.
        ax :
            Axes on which to plot.
        params :
            Combined parameters for the geom and stat. Also
            includes the `zorder`.
        """
        for _, gdata in data.groupby("group"):
            gdata.reset_index(inplace=True, drop=True)
            self.draw_group(gdata, panel_params, coord, ax, self.params)

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        """
        Plot data belonging to a group.

        Parameters
        ----------
        data :
            Data to be plotted by this geom. This is the
            dataframe created in the plot_build pipeline.
        panel_params :
            The scale information as may be required by the
            axes. At this point, that information is about
            ranges, ticks and labels. Keys of interest to
            the geom are:

            ```python
            "x_range"  # tuple
            "y_range"  # tuple
            ```
        coord : coord
            Coordinate (e.g. coord_cartesian) system of the geom.
        ax : axes
            Axes on which to plot.
        params : dict
            Combined parameters for the geom and stat. Also
            includes the `zorder`.
        """
        msg = "The geom should implement this method."
        raise NotImplementedError(msg)

    @staticmethod
    def draw_unit(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        """
        Plot data belonging to a unit.

        A matplotlib plot function may require that an aethestic
        have a single unique value. e.g. `linestyle="dashed"`{.py}
        and not `linestyle=["dashed", "dotted", ...]`{.py}.
        A single call to such a function can only plot lines with
        the same linestyle. However, if the plot we want has more
        than one line with different linestyles, we need to group
        the lines with the same linestyle and plot them as one
        unit. In this case, draw_group calls this function to do
        the plotting. For an example see
        [](`~plotnine.geoms.geom_point`).

        Parameters
        ----------
        data :
            Data to be plotted by this geom. This is the
            dataframe created in the plot_build pipeline.
        panel_params :
            The scale information as may be required by the
            axes. At this point, that information is about
            ranges, ticks and labels. Keys of interest to
            the geom are:

            ```python
            "x_range"  # tuple
            "y_range"  # tuple
            ```

            In rare cases a geom may need access to the x or y scales.
            Those are available at:

            ```python
            "scales"   # SimpleNamespace
            ```
        coord :
            Coordinate (e.g. coord_cartesian) system of the
            geom.
        ax :
            Axes on which to plot.
        params :
            Combined parameters for the geom and stat. Also
            includes the `zorder`.
        """
        msg = "The geom should implement this method."
        raise NotImplementedError(msg)

    def __radd__(self, other: ggplot) -> ggplot:
        """
        Add layer representing geom object on the right

        Parameters
        ----------
        plot :
            ggplot object

        Returns
        -------
        :
            ggplot object with added layer.
        """
        other += self.to_layer()  # Add layer
        return other

    def to_layer(self) -> layer:
        """
        Make a layer that represents this geom

        Returns
        -------
        :
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
        [](`~plotnine.geoms.geom_path`).

        Parameters
        ----------
        data :
            Data

        Returns
        -------
        :
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
        data: pd.Series[Any], da: DrawingArea, lyr: layer
    ) -> DrawingArea:
        """
        Draw a rectangle in the box

        Parameters
        ----------
        data :
            A row of the data plotted to this layer
        da :
            Canvas on which to draw
        lyr :
            Layer that the geom belongs to.

        Returns
        -------
        :
            The DrawingArea after a layer has been drawn onto it.
        """
        msg = "The geom should implement this method."
        raise NotImplementedError(msg)

    @staticmethod
    def legend_key_size(
        data: pd.Series[Any], min_size: tuple[int, int], lyr: layer
    ) -> tuple[int, int]:
        """
        Calculate the size of key that would fit the layer contents

        Parameters
        ----------
        data :
            A row of the data plotted to this layer
        min_size :
            Initial size which should be expanded to fit the contents.
        lyr :
            Layer
        """
        return min_size

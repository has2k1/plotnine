from __future__ import annotations

import typing
from copy import deepcopy

import pandas as pd

from .._utils import (
    check_required_aesthetics,
    copy_keys,
    data_mapping_as_kwargs,
    groupby_apply,
    remove_missing,
    uniquecols,
)
from .._utils.registry import Register, Registry
from ..exceptions import PlotnineError
from ..layer import layer
from ..mapping import aes

if typing.TYPE_CHECKING:
    from typing import Any

    from plotnine import ggplot
    from plotnine.facets.layout import Layout
    from plotnine.geoms.geom import geom
    from plotnine.iapi import pos_scales
    from plotnine.mapping import Environment
    from plotnine.typing import DataLike

from abc import ABC


class stat(ABC, metaclass=Register):
    """Base class of all stats"""

    DEFAULT_AES: dict[str, Any] = {}
    """Default aesthetics for the stat"""

    REQUIRED_AES: set[str] = set()
    """Required aesthetics for the stat"""

    NON_MISSING_AES: set[str] = set()
    """Required aesthetics for the stat"""

    DEFAULT_PARAMS: dict[str, Any] = {}
    """Required parameters for the stat"""

    CREATES: set[str] = set()
    """
    Stats may modify existing columns or create extra
    columns.

    Any extra columns that may be created by the stat
    should be specified in this set
    see: stat_bin

    Documentation for the aesthetics. It ie added under the
    documentation for mapping parameter. Use {aesthetics_table}
    placeholder to insert a table for all the aesthetics and
    their default values.
    """

    _aesthetics_doc = "{aesthetics_table}"

    # Plot namespace, it gets its value when the plot is being
    # built.
    environment: Environment | None = None

    def __init__(
        self,
        mapping: aes | None = None,
        data: DataLike | None = None,
        **kwargs: Any,
    ):
        kwargs = data_mapping_as_kwargs((data, mapping), kwargs)
        self._kwargs = kwargs  # Will be used to create the geom
        self.params = copy_keys(kwargs, deepcopy(self.DEFAULT_PARAMS))
        self.DEFAULT_AES = aes(**self.DEFAULT_AES)
        self.aes_params = {
            ae: kwargs[ae] for ae in (self.aesthetics() & kwargs.keys())
        }

    @staticmethod
    def from_geom(geom: geom) -> stat:
        """
        Return an instantiated stat object

        stats should not override this method.

        Parameters
        ----------
        geom :
            A geom object

        Returns
        -------
        stat
            A stat object

        Raises
        ------
        [](`~plotnine.exceptions.PlotnineError`) if unable to create a `stat`.
        """
        name = geom.params["stat"]
        kwargs = geom._kwargs
        # More stable when reloading modules than
        # using issubclass
        if not isinstance(name, type) and hasattr(name, "compute_layer"):
            return name

        if isinstance(name, stat):
            return name
        elif isinstance(name, type) and issubclass(name, stat):
            klass = name
        elif isinstance(name, str):
            if not name.startswith("stat_"):
                name = f"stat_{name}"
            klass = Registry[name]
        else:
            raise PlotnineError(f"Unknown stat of type {type(name)}")

        valid_kwargs = (
            klass.aesthetics() | klass.DEFAULT_PARAMS.keys()
        ) & kwargs.keys()

        params = {k: kwargs[k] for k in valid_kwargs}
        return klass(geom=geom, **params)

    def __deepcopy__(self, memo: dict[Any, Any]) -> stat:
        """
        Deep copy without copying the self.data dataframe

        stats should not override this method.
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        # don't make a _kwargs
        shallow = {"_kwargs"}
        for key, item in old.items():
            if key in shallow:
                new[key] = item
                memo[id(new[key])] = new[key]
            else:
                new[key] = deepcopy(item, memo)

        return result

    @classmethod
    def aesthetics(cls) -> set[str]:
        """
        Return a set of all non-computed aesthetics for this stat.

        stats should not override this method.
        """
        aesthetics = cls.REQUIRED_AES.copy()
        calculated = aes(**cls.DEFAULT_AES)._calculated
        for ae in set(cls.DEFAULT_AES) - set(calculated):
            aesthetics.add(ae)
        return aesthetics

    def use_defaults(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Combine data with defaults and set aesthetics from parameters

        stats should not override this method.

        Parameters
        ----------
        data :
            Data used for drawing the geom.

        Returns
        -------
        out :
            Data used for drawing the geom.
        """
        missing = (
            self.aesthetics() - set(self.aes_params.keys()) - set(data.columns)
        )

        for ae in missing - self.REQUIRED_AES:
            if self.DEFAULT_AES[ae] is not None:
                data[ae] = self.DEFAULT_AES[ae]

        missing = self.aes_params.keys() - set(data.columns)

        for ae in self.aes_params:
            data[ae] = self.aes_params[ae]

        return data

    def setup_params(self, data: pd.DataFrame) -> dict[str, Any]:
        """
        Overide this to verify or adjust parameters

        Parameters
        ----------
        data :
            Data

        Returns
        -------
        out :
            Parameters used by the stats.
        """
        return self.params

    def setup_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Overide to modify data before compute_layer is called

        Parameters
        ----------
        data :
            Data

        Returns
        -------
        out :
            Data
        """
        return data

    def finish_layer(
        self, data: pd.DataFrame, params: dict[str, Any]
    ) -> pd.DataFrame:
        """
        Modify data after the aesthetics have been mapped

        This can be used by stats that require access to the mapped
        values of the computed aesthetics, part 3 as shown below.

            1. stat computes and creates variables
            2. variables mapped to aesthetics
            3. stat sees and modifies data according to the
               aesthetic values

        The default to is to do nothing.

        Parameters
        ----------
        data :
            Data for the layer
        params :
            Paremeters

        Returns
        -------
        data :
            Modified data
        """
        return data

    @classmethod
    def compute_layer(
        cls, data: pd.DataFrame, params: dict[str, Any], layout: Layout
    ) -> pd.DataFrame:
        """
        Calculate statistics for this layers

        This is the top-most computation method for the
        stat. It does not do any computations, but it
        knows how to verify the data, partition it call the
        next computation method and merge results.

        stats should not override this method.

        Parameters
        ----------
        data :
            Data points for all objects in a layer.
        params :
            Stat parameters
        layout :
            Panel layout information
        """
        check_required_aesthetics(
            cls.REQUIRED_AES,
            list(data.columns) + list(params.keys()),
            cls.__name__,
        )

        data = remove_missing(
            data,
            na_rm=params.get("na_rm", False),
            vars=list(cls.REQUIRED_AES | cls.NON_MISSING_AES),
            name=cls.__name__,
            finite=True,
        )

        def fn(pdata):
            """
            Compute function helper
            """
            # Given data belonging to a specific panel, grab
            # the corresponding scales and call the method
            # that does the real computation
            if len(pdata) == 0:
                return pdata
            pscales = layout.get_scales(pdata["PANEL"].iloc[0])
            return cls.compute_panel(pdata, pscales, **params)

        return groupby_apply(data, "PANEL", fn)

    @classmethod
    def compute_panel(
        cls, data: pd.DataFrame, scales: pos_scales, **params: Any
    ):
        """
        Calculate the statistics for all the groups

        Return the results in a single dataframe.

        This is a default function that can be overriden
        by individual stats

        Parameters
        ----------
        data :
            data for the computing
        scales :
            x (``scales.x``) and y (``scales.y``) scale objects.
            The most likely reason to use scale information is
            to find out the physical size of a scale. e.g.

            ```python
            range_x = scales.x.dimension()
            ```
        params :
            The parameters for the stat. It includes default
            values if user did not set a particular parameter.
        """
        if not len(data):
            return type(data)()

        stats = []
        for _, old in data.groupby("group"):
            new = cls.compute_group(old, scales, **params)
            unique = uniquecols(old)
            missing = unique.columns.difference(new.columns)
            idx = [0] * len(new)
            u = unique.loc[idx, missing].reset_index(  # pyright: ignore
                drop=True
            )
            # concat can have problems with empty dataframes that
            # have an index
            if u.empty and len(u):
                u = type(data)()

            group_result = pd.concat([new, u], axis=1)
            stats.append(group_result)

        stats = pd.concat(stats, axis=0, ignore_index=True)
        # Note: If the data coming in has columns with non-unique
        # values with-in group(s), this implementation loses the
        # columns. Individual stats may want to do some preparation
        # before then fall back on this implementation or override
        # it completely.
        return stats

    @classmethod
    def compute_group(
        cls, data: pd.DataFrame, scales: pos_scales, **params: Any
    ) -> pd.DataFrame:
        """
        Calculate statistics for the group

        All stats should implement this method

        Parameters
        ----------
        data :
            Data for a group
        scales :
            x (``scales.x``) and y (``scales.y``) scale objects.
            The most likely reason to use scale information is
            to find out the physical size of a scale. e.g.

            ```python
            range_x = scales.x.dimension()
            ```
        params :
            Parameters
        """
        msg = "{} should implement this method."
        raise NotImplementedError(msg.format(cls.__name__))

    def __radd__(self, plot: ggplot) -> ggplot:
        """
        Add layer representing stat object on the right

        Parameters
        ----------
        gg :
            ggplot object

        Returns
        -------
        out :
            ggplot object with added layer
        """
        plot += self.to_layer()  # Add layer
        return plot

    def to_layer(self) -> layer:
        """
        Make a layer that represents this stat

        Returns
        -------
        out :
            Layer
        """
        # Create, geom from stat, then layer from geom
        from ..geoms.geom import geom

        return layer.from_geom(geom.from_stat(self))

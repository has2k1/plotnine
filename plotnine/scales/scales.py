from __future__ import annotations

import itertools
import typing
from contextlib import suppress
from typing import List
from warnings import warn

import numpy as np
import pandas.api.types as pdtypes

from .._utils import array_kind
from .._utils.registry import Registry
from ..exceptions import PlotnineError, PlotnineWarning
from ..mapping.aes import aes_to_scale
from .scale import scale

if typing.TYPE_CHECKING:
    import pandas as pd

    from plotnine.typing import ScaledAestheticsName


_TPL_DUPLICATE_SCALE = """\
Scale for '{0}' is already present.
Adding another scale for '{0}',
which will replace the existing scale.
"""


class Scales(List[scale]):
    """
    List of scales

    This class has methods the simplify the handling of
    the ggplot object scales
    """

    def append(self, sc: scale):
        """
        Add / Update scale

        Removes any previous scales that cover the same aesthetics
        """
        ae = sc.aesthetics[0]
        cover_ae = self.find(ae)
        if any(cover_ae):
            warn(_TPL_DUPLICATE_SCALE.format(ae), PlotnineWarning)
            idx = cover_ae.index(True)
            self.pop(idx)
        # super() does not work well with reloads
        list.append(self, sc)

    def find(self, aesthetic: ScaledAestheticsName | str) -> list[bool]:
        """
        Find scales for given aesthetic

        Returns a list[bool] each scale if it covers the aesthetic
        """
        return [aesthetic in s.aesthetics for s in self]

    def input(self):
        """
        Return a list of all the aesthetics covered by the scales
        """
        lst = [s.aesthetics for s in self]
        return list(itertools.chain(*lst))

    def get_scales(
        self, aesthetic: ScaledAestheticsName | str
    ) -> scale | None:
        """
        Return the scale for the aesthetic or None if there isn't one

        These are the scales specified by the user e.g
            `ggplot() + scale_x_continuous()`
        or those added by default during the plot building
        process
        """
        bool_lst = self.find(aesthetic)
        try:
            idx = bool_lst.index(True)
            return self[idx]
        except ValueError:
            return None

    @property
    def x(self) -> scale | None:
        """
        Return x scale
        """
        return self.get_scales("x")

    @property
    def y(self) -> scale | None:
        """
        Return y scale
        """
        return self.get_scales("y")

    def non_position_scales(self) -> Scales:
        """
        Return a list of any non-position scales
        """
        l = [
            s
            for s in self
            if "x" not in s.aesthetics and "y" not in s.aesthetics
        ]
        return Scales(l)

    def position_scales(self) -> Scales:
        """
        Return a list of the position scales that are present
        """
        l = [s for s in self if ("x" in s.aesthetics) or ("y" in s.aesthetics)]
        return Scales(l)

    def train(self, data, vars, idx):
        """
        Train the scales on the data.

        The scales should be for the same aesthetic
        e.g. x scales, y scales, color scales, ...

        Parameters
        ----------
        data : dataframe
            data to use for training
        vars : list | tuple
            columns in data to use for training.
            These should be all the aesthetics of
            a scale type that are present in the
            data. e.g x, xmin, xmax
        idx : array_like
            indices that map the data points to the
            scales. These start at 1, so subtract 1 to
            get the true index into the scales array
        """
        idx = np.asarray(idx)
        for col in vars:
            for i, sc in enumerate(self, start=1):
                bool_idx = i == idx
                sc.train(data.loc[bool_idx, col])

    def map(self, data, vars, idx):
        """
        Map the data onto the scales

        The scales should be for the same aesthetic
        e.g. x scales, y scales, color scales, ...

        Parameters
        ----------
        data : dataframe
            data with columns to map
            This is modified inplace
        vars : list | tuple
            columns to map
        idx : array_like
            indices that link the data points to the
            scales. These start at 1, so subtract 1 to
            get the true index into the scales array
        """
        idx = np.asarray(idx)
        # discrete scales change the dtype
        # from category to int. Use a new dataframe
        # to collect these results.
        # Using `type` preserves the subclass of pd.DataFrame
        discrete_data = type(data)(index=data.index)

        # Loop through each variable, mapping across each scale,
        # then joining back into the copy of the data
        for col in vars:
            use_df = array_kind.discrete(data[col])
            for i, sc in enumerate(self, start=1):
                bool_idx = i == idx
                results = sc.map(data.loc[bool_idx, col])
                if use_df:
                    discrete_data.loc[bool_idx, col] = results
                else:
                    data.loc[bool_idx, col] = results

        for col in discrete_data:
            data[col] = discrete_data[col]

    def reset(self):
        """
        Reset all the scales
        """
        for sc in self:
            sc.reset()

    def train_df(self, data: pd.DataFrame, drop: bool = False):
        """
        Train scales from a dataframe
        """
        if (len(data) == 0) or (len(self) == 0):
            return

        # Each scale trains the columns it understands
        for sc in self:
            sc.train_df(data)

    def map_df(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Map values from a dataframe.

        Returns dataframe
        """
        if (len(data) == 0) or (len(self) == 0):
            return data

        # Each scale maps the columns it understands
        for sc in self:
            data = sc.map_df(data)
        return data

    def transform_df(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform values in a dataframe.

        Returns dataframe
        """
        if (len(data) == 0) or (len(self) == 0):
            return data

        # Each scale transforms the columns it understands
        for sc in self:
            data = sc.transform_df(data)
        return data

    def inverse_df(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Inveres transform values in a dataframe.
        Returns dataframe
        """
        if (len(data) == 0) or (len(self) == 0):
            return data

        # Each scale transforms the columns it understands
        for sc in self:
            data = sc.inverse_df(data)
        return data

    def add_defaults(self, data, aesthetics):
        """
        Add default scales for the aesthetics if there is none

        Scales are added only if the aesthetic is mapped to
        a column in the dataframe. This function may have to be
        called separately after evaluating the aesthetics.
        """
        if not aesthetics:
            return

        # aesthetics with scales
        aws = set()
        if self:
            for s in (set(sc.aesthetics) for sc in self):
                aws.update(s)

        # aesthetics that do not have scales present
        # We preserve the order of the aesthetics
        new_aesthetics = [x for x in aesthetics if x not in aws]
        if not new_aesthetics:
            return

        # If a new aesthetic corresponds to a column in the data
        # frame, find a default scale for the type of data in that
        # column
        seen = set()
        for ae in new_aesthetics:
            col = aesthetics[ae]
            if col not in data:
                col = ae
            scale_var = aes_to_scale(ae)

            if self.get_scales(scale_var):
                continue

            seen.add(scale_var)
            try:
                sc = make_scale(scale_var, data[col])
            except PlotnineError:
                # Skip aesthetics with no scales (e.g. group, order, etc)
                continue
            self.append(sc)

    def add_missing(self, aesthetics):
        """
        Add missing but required scales.

        Parameters
        ----------
        aesthetics : list | tuple
            Aesthetic names. Typically, ('x', 'y').
        """
        # Keep only aesthetics that don't have scales
        aesthetics = set(aesthetics) - set(self.input())

        for ae in aesthetics:
            scale_name = f"scale_{ae}_continuous"
            scale_f = Registry[scale_name]
            self.append(scale_f())


def scale_type(series):
    """
    Get a suitable scale for the series
    """
    if array_kind.continuous(series):
        stype = "continuous"
    elif array_kind.ordinal(series):
        stype = "ordinal"
    elif array_kind.discrete(series):
        stype = "discrete"
    elif array_kind.datetime(series):
        stype = "datetime"
    elif array_kind.timedelta(series):
        stype = "timedelta"
    else:
        msg = (
            "Don't know how to automatically pick scale for "
            "object of type {}. Defaulting to 'continuous'"
        )
        warn(msg.format(series.dtype), PlotnineWarning)
        stype = "continuous"
    return stype


def make_scale(ae, series, *args, **kwargs):
    """
    Return a proper scale object for the series

    The scale is for the aesthetic ae, and args & kwargs
    are passed on to the scale creating class
    """
    if pdtypes.is_float_dtype(series) and np.isinf(series).all():
        raise PlotnineError("Cannot create scale for infinite data")

    stype = scale_type(series)

    # filter parameters by scale type
    if stype in ("discrete", "ordinal"):
        with suppress(KeyError):
            del kwargs["trans"]

    scale_name = f"scale_{ae}_{stype}"
    scale_klass = Registry[scale_name]
    return scale_klass(*args, **kwargs)

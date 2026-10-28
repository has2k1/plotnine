from __future__ import annotations

import itertools
import typing
from contextlib import suppress
from typing import List, cast
from warnings import warn

import narwhals as nw
import numpy as np

from .._utils import array_kind, frame
from .._utils.frame import native_io
from .._utils.registry import Registry
from ..exceptions import PlotnineError, PlotnineWarning
from ..mapping.aes import aes_to_scale
from .scale import scale

if typing.TYPE_CHECKING:
    from typing import Any, Sequence

    from plotnine._utils.frame import DataFrame
    from plotnine.scales.scale_xy import ScaleX, ScaleY
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
    def x(self) -> ScaleX | None:
        """
        Return x scale
        """
        return cast("ScaleX | None", self.get_scales("x"))

    @property
    def y(self) -> ScaleY | None:
        """
        Return y scale
        """
        return cast("ScaleY| None", self.get_scales("y"))

    @property
    def axis_positions(self) -> tuple[str, str]:
        """
        The sides the x and y axes occupy, as `(x_side, y_side)`
        """
        # scales.x / scales.y can be None here if "missing" scales
        # have not yet been added.
        x_side = "bottom" if self.x is None else self.x.position
        y_side = "left" if self.y is None else self.y.position
        return x_side, y_side

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

    @native_io
    def train(self, data: DataFrame, vars: Sequence[str], idx: Any):
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
            values = frame.scale_values(data[col])
            for i, sc in enumerate(self, start=1):
                bool_idx = i == idx
                sc.train(_subset(values, bool_idx))

    @native_io
    def map(self, data: DataFrame, vars: Sequence[str], idx: Any) -> DataFrame:
        """
        Map the data onto the scales

        The scales should be for the same aesthetic
        e.g. x scales, y scales, color scales, ...

        Parameters
        ----------
        data : dataframe
            data with columns to map
        vars : list | tuple
            columns to map
        idx : array_like
            indices that link the data points to the
            scales. These start at 1, so subtract 1 to
            get the true index into the scales array

        Returns
        -------
        :
            Data with the mapped columns
        """
        idx = np.asarray(idx)
        n = len(data)
        mapped = {}
        for col in vars:
            values = frame.scale_values(data[col])
            parts = []
            for i, sc in enumerate(self, start=1):
                bool_idx = i == idx
                if bool_idx.all():
                    parts = [(bool_idx, sc.map(values))]
                    break
                elif bool_idx.any():
                    parts.append((bool_idx, sc.map(_subset(values, bool_idx))))

            if len(parts) == 1 and parts[0][0].all():
                mapped[col] = parts[0][1]
            elif parts:
                mapped[col] = _combine(parts, n)

        return frame.assign(data, **mapped)

    def reset(self):
        """
        Reset all the scales
        """
        for sc in self:
            sc.reset()

    @native_io
    def train_df(self, data: DataFrame, drop: bool = False):
        """
        Train scales from a dataframe
        """
        if (len(data) == 0) or (len(self) == 0):
            return

        # Each scale trains the columns it understands
        for sc in self:
            sc.train_df(data)

    @native_io
    def map_df(self, data: DataFrame) -> DataFrame:
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

    @native_io
    def transform_df(self, data: DataFrame) -> DataFrame:
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

    @native_io
    def inverse_df(self, data: DataFrame) -> DataFrame:
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

    @native_io
    def add_defaults(self, data: DataFrame, aesthetics):
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
        columns = set(data.columns)
        for ae in new_aesthetics:
            col = aesthetics[ae]
            if col not in columns:
                col = ae
            if col not in columns:
                continue
            scale_var = aes_to_scale(ae)

            if self.get_scales(scale_var):
                continue

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
    if frame.dtype_kind(series) == "f":
        values = frame.as_numpy(series)
        if len(values) and np.isinf(values).all():
            raise PlotnineError("Cannot create scale for infinite data")

    stype = scale_type(series)

    # filter parameters by scale type
    if stype in ("discrete", "ordinal"):
        with suppress(KeyError):
            del kwargs["trans"]

    scale_name = f"scale_{ae}_{stype}"
    scale_klass = Registry[scale_name]
    return scale_klass(*args, **kwargs)


def _subset(values: Any, bool_idx: np.ndarray) -> Any:
    """
    Select the values (array or series) where bool_idx is True
    """
    if bool_idx.all():
        return values
    if isinstance(values, nw.Series):
        mask = frame.series(bool_idx, backend=values.implementation)
        return values.filter(mask)
    return values[bool_idx]


def _combine(parts: list[tuple[np.ndarray, Any]], n: int) -> np.ndarray:
    """
    Combine values that belong to different rows into an array
    """
    arrays = [(idx, np.asarray(values)) for idx, values in parts]
    if all(arr.ndim == 1 and arr.dtype.kind in "biuf" for _, arr in arrays):
        dtype = np.result_type(float, *[arr.dtype for _, arr in arrays])
        out = np.full(n, np.nan, dtype=dtype)
        for idx, arr in arrays:
            out[idx] = arr
    else:
        # e.g. strings or tuples
        out = np.full(n, None, dtype=object)
        for idx, values in parts:
            _values = np.empty(len(values), dtype=object)
            _values[:] = list(values)
            out[idx] = _values
    return out

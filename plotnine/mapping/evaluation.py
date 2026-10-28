from __future__ import annotations

import datetime
import numbers
from collections.abc import Mapping, Sequence
from contextlib import suppress
from typing import TYPE_CHECKING, Any

import narwhals as nw
import numpy as np

from .._utils import frame
from .._utils.frame import is_native_series, native_io
from ..exceptions import PlotnineError
from ._asis import I, is_asis
from ._eval_environment import factor, reorder

if TYPE_CHECKING:
    from plotnine._utils.frame import DataFrame

    from . import aes
    from ._env import Environment


__all__ = ("after_stat", "after_scale", "stage")


EVAL_ENVIRONMENT = {"factor": factor, "reorder": reorder, "I": I}

_TPL_EVAL_FAIL = """\
Could not evaluate the '{}' mapping: '{}' \
(original error: {})"""

_TPL_BAD_EVAL_TYPE = """\
The '{}' mapping: '{}' produced a value of type '{}',\
but only single items and lists/arrays can be used. \
(original error: {})"""


class stage:
    """
    Stage allows you evaluating mapping at more than one stage

    You can evaluate an expression of a variable in a dataframe, and
    later evaluate an expression that modifies the values mapped to
    the scale.

    Parameters
    ----------
    start : str | array_like | scalar
        Aesthetic expression using primary variables from the layer
        data.
    after_stat : str
        Aesthetic expression using variables calculated by the stat.
    after_scale : str
        Aesthetic expression using aesthetics of the layer.
    """

    def __init__(self, start=None, after_stat=None, after_scale=None):
        self.start = start
        self.after_stat = after_stat
        self.after_scale = after_scale

    def __repr__(self):
        """
        Repr for staged mapping
        """
        # Shorter representation when the mapping happens at a
        # single stage
        if self.after_stat is None and self.after_scale is None:
            return f"{repr(self.start)}"
        if self.start is None and self.after_scale is None:
            return f"after_stat({repr(self.after_stat)})"
        if self.start is None and self.after_stat is None:
            return f"after_scale({repr(self.after_scale)})"
        return (
            f"stage(start={repr(self.start)}, "
            f"after_stat={repr(self.after_stat)}, "
            f"after_scale={repr(self.after_scale)})"
        )


def after_stat(x):
    """
    Evaluate mapping after statistic has been calculated

    Parameters
    ----------
    x : str
        An expression

    See Also
    --------
    plotnine.after_scale
    plotnine.stage
    """
    return stage(after_stat=x)


def after_scale(x):
    """
    Evaluate mapping after variable has been mapped to the scale

    This gives the user a chance to alter the value of a variable
    in the final units of the scale e.g. the rgb hex color.

    Parameters
    ----------
    x : str
        An expression

    See Also
    --------
    plotnine.after_stat
    plotnine.stage
    """
    return stage(after_scale=x)


@native_io
def evaluate(
    aesthetics: aes | dict[str, Any], data: DataFrame, env: Environment
) -> DataFrame:
    """
    Evaluate aesthetics

    Parameters
    ----------
    aesthetics :
        Aesthetics to evaluate. They must be of the form {name: expr}.
        An expression can be a column name, a narwhals expression,
        a string with a python expression, a sequence of values or a
        single value.
    data :
        Dataframe whose columns are/may-be variables in the aesthetic
        expressions i.e. it is a namespace with variables.
    env :
        Environment in which the aesthetics are evaluated

    Returns
    -------
    :
        Dataframe of the form {name: result}, where each column is the
        result from evaluating an expression.

    Notes
    -----
    A string expression is first evaluated with the column names
    standing in for narwhals expressions, e.g. `"np.log(x) + 1"`
    becomes `np.log(nw.col("x")) + 1`, which works for every
    dataframe library. If that does not produce an expression, the
    string is evaluated with the column names standing in for the
    columns, e.g. pandas or polars series. This approach allows
    expressions that use the API of the dataframe library. Lastly, the
    column names stand in for numpy arrays.

    Examples
    --------
    >>> import pandas as pd
    >>> from plotnine.mapping import Environment
    >>> var1 = 2
    >>> env = Environment.capture()
    >>> df = pd.DataFrame({'x': range(1, 6)})
    >>> aesthetics = {'y': 'x**var1'}
    >>> evaluate(aesthetics, df, env)
        y
    0   1
    1   4
    2   9
    3  16
    4  25
    """
    env = env.with_outer_namespace(EVAL_ENVIRONMENT)

    # Store evaluation results in a dict column in a dict
    evaled = {}

    # If a column name is not in the data, it is evaluated/transformed
    # in the environment of the call to ggplot
    for ae, col in aesthetics.items():
        if isinstance(col, nw.Expr):
            evaled[ae] = _eval_expr(col, data, ae)
        elif isinstance(col, str):
            if col in data.columns:
                evaled[ae] = data[col]
            else:
                evaled[ae] = eval_string(col, data, env, ae)
        elif is_list_like(col) or is_asis(col):
            n = len(col)
            if len(data) and n != len(data) and n != 1:
                msg = (
                    "Aesthetics must either be length one, "
                    "or the same length as the data"
                )
                raise PlotnineError(msg)
            evaled[ae] = col
        elif is_known_scalar(col) or col is None:
            if not len(evaled):
                col = [col]
            evaled[ae] = col
        else:
            msg = f"Do not know how to deal with aesthetic '{ae}'"
            raise PlotnineError(msg)

    n = len(data) if len(data) and evaled else None
    try:
        return frame.frame(evaled, backend=data.implementation, n=n)
    except ValueError as e:
        raise PlotnineError(
            "Aesthetics must either be length one, "
            f"or the same length as the data. {e}"
        ) from e


def _eval_expr(expr: nw.Expr, data: DataFrame, ae: str) -> Any:
    """
    Evaluate a narwhals expression on the data
    """
    try:
        return data.select(expr.alias(ae))[ae]
    except Exception as e:
        msg = _TPL_EVAL_FAIL.format(ae, expr, str(e))
        raise PlotnineError(msg) from e


def eval_string(expr: str, data: DataFrame, env: Environment, ae: str) -> Any:
    """
    Evaluate a string expression

    The column names in the expression are first taken to be
    narwhals expressions, and if that does not work, they are taken
    to be the native series of the dataframe.
    """
    columns = _ColumnExpressions(data.columns)
    try:
        value = env.eval(expr, inner_namespace=columns)
    except Exception:
        pass
    else:
        if isinstance(value, nw.Expr):
            with suppress(Exception):
                return data.select(value.alias(ae))[ae]
        elif not columns.accessed:
            # The expression does not depend on the data
            return value

    try:
        return env.eval(expr, inner_namespace=_NativeColumns(data))
    except Exception as e:
        error = e

    # Finally, numpy arrays work with numpy functions for all libraries
    try:
        return env.eval(expr, inner_namespace=_NativeColumns(data, numpy=True))
    except Exception:
        msg = _TPL_EVAL_FAIL.format(ae, expr, str(error))
        raise PlotnineError(msg) from error


class _ColumnExpressions(Mapping[str, nw.Expr]):
    """
    Namespace with the column names as narwhals expressions
    """

    def __init__(self, columns: Sequence[str]):
        self._columns = list(columns)
        self._lookup = set(self._columns)
        self.accessed = False

    def __getitem__(self, key: str) -> nw.Expr:
        if key in self._lookup:
            self.accessed = True
            return nw.col(key)
        raise KeyError(key)

    def __iter__(self):
        return iter(self._columns)

    def __len__(self) -> int:
        return len(self._columns)


class _NativeColumns(Mapping[str, Any]):
    """
    Namespace with the column names as the native series

    Or as numpy arrays.
    """

    def __init__(self, data: DataFrame, numpy: bool = False):
        self._data = data
        self._lookup = set(data.columns)
        self._numpy = numpy

    def __getitem__(self, key: str) -> Any:
        if key in self._lookup:
            s = self._data[key]
            if self._numpy:
                return frame.to_numpy(s)
            native = s.to_native()
            if getattr(native.dtype, "name", None) == "geometry":
                # A geometry column of a geopandas dataframe
                import geopandas as gpd

                native = gpd.GeoSeries(native)
            return native
        raise KeyError(key)

    def __iter__(self):
        return iter(self._data.columns)

    def __len__(self) -> int:
        return len(self._data.columns)


def is_known_scalar(value):
    """
    Return True if value is a type we expect in a dataframe
    """
    return not np.iterable(value) and isinstance(
        value,
        (
            numbers.Number,
            datetime.date,
            datetime.timedelta,
            np.datetime64,
            np.timedelta64,
        ),
    )


def is_list_like(obj: Any) -> bool:
    """
    Return True if *obj* is a list, tuple, series or array
    """
    if isinstance(obj, (list, tuple, range, np.ndarray, nw.Series)):
        return True
    return is_native_series(obj) or (
        hasattr(obj, "__len__")
        and hasattr(obj, "dtype")
        and not isinstance(obj, (str, bytes))
    )

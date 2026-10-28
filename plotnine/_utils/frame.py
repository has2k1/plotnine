"""
Dataframe helpers that work with any backend supported by narwhals

Internally, plotnine passes around eager narwhals dataframes. The
user's dataframe library (pandas, polars, ...) is the backend of those
dataframes and plotnine never converts between backends. The helpers
in this module fill the gaps between what plotnine needs and what the
narwhals API offers, and they smooth over differences between the
backends, e.g. null vs NaN and the order of groups.
"""

from __future__ import annotations

import datetime
import numbers
from collections.abc import Iterable, Mapping, Sequence
from functools import cache
from importlib.util import find_spec
from typing import TYPE_CHECKING

import narwhals as nw
import numpy as np
from narwhals.dependencies import get_pandas, is_pandas_like_dataframe

if TYPE_CHECKING:
    from typing import Any, Callable, Iterator

    from narwhals.typing import IntoDType

    DataFrame = nw.DataFrame[Any]
    Series = nw.Series[Any]

Implementation = nw.Implementation

__all__ = (
    "Implementation",
    "is_frame",
    "to_frame",
    "backend",
    "default_backend",
    "series",
    "frame",
    "empty_like",
    "assign",
    "concat",
    "group_split",
    "group_apply",
    "is_missing",
    "filter_rows",
    "take",
    "levels",
)


def is_frame(obj: Any) -> bool:
    """
    Return True if obj is an eager dataframe of any supported library
    """
    if isinstance(obj, nw.DataFrame):
        return True
    try:
        nw.from_native(obj, eager_only=True)
    except TypeError:
        return False
    return True


def to_frame(data: Any) -> DataFrame:
    """
    Convert the user's data to an eager narwhals dataframe

    Parameters
    ----------
    data :
        A dataframe of any library supported by narwhals, a narwhals
        dataframe or a grouped pandas dataframe.
    """
    if isinstance(data, nw.DataFrame):
        return data

    # A grouped pandas dataframe is accepted as its ungrouped
    # dataframe. Grouping is done through the aesthetics.
    if (pd := get_pandas()) is not None and isinstance(
        data, pd.core.groupby.DataFrameGroupBy
    ):
        data = data.obj

    df = nw.from_native(data, eager_only=True)

    # pandas dataframes with a non-default index, can bring along
    # an index with duplicates that pandas would align on. We only
    # ever refer to rows by position.
    if is_pandas_like_dataframe(data):
        index = data.index
        if not (
            type(index).__name__ == "RangeIndex"
            and index.start == 0  # pyright: ignore[reportAttributeAccessIssue]
            and index.step == 1  # pyright: ignore[reportAttributeAccessIssue]
        ):
            df = nw.from_native(data.reset_index(drop=True), eager_only=True)
    return df


def backend(df: DataFrame | Series) -> Implementation:
    """
    Return the library that backs a narwhals object
    """
    return df.implementation


@cache
def default_backend() -> Implementation:
    """
    Backend to use when there is no data to take it from

    Polars is preferred, and pandas is the fallback.
    """
    if find_spec("polars"):
        return Implementation.POLARS
    if find_spec("pandas"):
        return Implementation.PANDAS
    raise ImportError(
        "plotnine requires either polars or pandas to be installed."
    )


def _is_scalar(value: Any) -> bool:
    return isinstance(value, (str, bytes)) or not isinstance(
        value, (Iterable, nw.Series)
    )


def _infer_object_values(values: Sequence[Any]) -> IntoDType | None:
    """
    Infer the narwhals dtype for values held in a python sequence

    Returns None if the backend should do the inference.
    """
    has_str, has_other = False, False
    for v in values:
        if v is None:
            continue
        elif isinstance(v, str):
            has_str = True
        elif isinstance(v, float) and np.isnan(v):
            continue
        elif isinstance(
            v,
            (
                numbers.Number,
                np.generic,
                datetime.date,
                datetime.timedelta,
            ),
        ):
            has_other = True
        else:
            return nw.Object
        if has_str and has_other:
            return nw.Object
    return nw.String if has_str else None


def _clean_strings(values: Sequence[Any]) -> list[Any]:
    """
    Replace NaN with None in a sequence of strings
    """
    return [
        None if (isinstance(v, float) and np.isnan(v)) else v for v in values
    ]


def series(
    values: Any,
    name: str = "",
    *,
    backend: Implementation,
    dtype: IntoDType | None = None,
) -> Series:
    """
    Create a narwhals series

    Parameters
    ----------
    values :
        Values of the series. It can be a narwhals series, a native
        series, a numpy array or any python sequence.
    name :
        Name of the series.
    backend :
        Library that should hold the series.
    dtype :
        Data type of the series.
    """
    if isinstance(values, nw.Series):
        s = values
        if s.implementation != backend:
            s = series(s.to_list(), name, backend=backend, dtype=s.dtype)
        if s.name != name:
            s = s.alias(name)
        return s.cast(dtype) if dtype is not None else s

    try:
        s = nw.from_native(values, series_only=True)
    except TypeError:
        pass
    else:
        return series(s, name, backend=backend, dtype=dtype)

    if (pd := get_pandas()) is not None and isinstance(
        values, (pd.Categorical, pd.Index)
    ):
        return series(pd.Series(values), name, backend=backend, dtype=dtype)

    if isinstance(values, np.ndarray):
        if values.ndim != 1:
            values = values.ravel()
        if values.dtype.kind == "O" and dtype is None:
            dtype = _infer_object_values(values)
            values = list(values)
            if dtype == nw.String:
                values = _clean_strings(values)
        elif values.dtype.kind == "U" and dtype is None:
            dtype = nw.String
    elif not isinstance(values, Sequence):
        values = list(values)

    if not isinstance(values, np.ndarray) and dtype is None:
        dtype = _infer_object_values(values)
        if dtype == nw.String:
            values = _clean_strings(values)

    if dtype == nw.Object:
        # The narwhals constructors cannot create object columns
        # in polars
        if backend == Implementation.POLARS:
            import polars as pl

            return nw.from_native(
                pl.Series(name, list(values), dtype=pl.Object),
                series_only=True,
            )
        else:
            arr = np.empty(len(values), dtype=object)
            arr[:] = list(values)
            return nw.new_series(name, arr, backend=backend)

    if (
        backend == Implementation.POLARS
        and isinstance(values, np.ndarray)
        and values.dtype.kind in "Mm"
        and values.dtype.str[-3:-1] not in ("ns", "us", "ms")
    ):
        # polars only supports these units
        unit = "datetime64[ns]" if values.dtype.kind == "M" else "m8[ns]"
        values = values.astype(unit)

    return nw.new_series(name, values, dtype, backend=backend)


def _length(values: Any) -> int | None:
    if _is_scalar(values):
        return None
    return len(values)


def frame(
    data: Mapping[str, Any] | None = None,
    *,
    backend: Implementation,
    n: int | None = None,
) -> DataFrame:
    """
    Create a narwhals dataframe

    Parameters
    ----------
    data :
        Mapping of column names to column values. A column value can
        be a scalar, in which case it is repeated to fill the column.
    backend :
        Library that should hold the dataframe.
    n :
        Number of rows. If not given, it is the length of the
        longest column. It is only required when all columns are
        scalars and the dataframe should not have one row.
    """
    data = dict(data or {})
    if n is None:
        lengths = [l for v in data.values() if (l := _length(v)) is not None]
        n = max(lengths) if lengths else (1 if data else 0)

    cols = []
    for name, value in data.items():
        if _is_scalar(value):
            value = [value] * n
        elif len(value) != n:
            if len(value) == 1:
                value = list(value) * n
            else:
                raise ValueError(
                    f"Column {name!r} has length {len(value)}, expected {n}."
                )
        cols.append(series(value, name, backend=backend))

    if not cols:
        ns = backend.to_native_namespace()
        return nw.from_native(ns.DataFrame(), eager_only=True)
    # Adding columns to a frame is safer than nw.from_dict, which
    # cannot handle object columns in polars
    return cols[0].to_frame().with_columns(*cols[1:])


def empty_like(df: DataFrame) -> DataFrame:
    """
    Return a dataframe with the same backend and no rows or columns
    """
    return frame(backend=df.implementation)


def assign(df: DataFrame, **columns: Any) -> DataFrame:
    """
    Add or replace columns

    The values can be scalars, sequences, numpy arrays, native or
    narwhals series and narwhals expressions.
    """
    if not columns:
        return df

    impl = df.implementation
    if not df.columns:
        return frame(columns, backend=impl)

    exprs = []
    for name, value in columns.items():
        if isinstance(value, nw.Expr):
            exprs.append(value.alias(name))
        elif _is_scalar(value):
            exprs.append(series([value] * len(df), name, backend=impl))
        else:
            exprs.append(series(value, name, backend=impl))
    return df.with_columns(*exprs)


def _numeric_rank(dtype: Any) -> int:
    if dtype.is_float():
        return 2
    if dtype.is_integer():
        return 1
    if dtype == nw.Boolean:
        return 0
    return -1


def _supertype(dtypes: list[Any]) -> Any:
    """
    The narwhals dtype that can hold values of all dtypes
    """
    dtypes = [d for d in dtypes if d != nw.Unknown and str(d) != "Null"]
    if not dtypes:
        return None

    first = dtypes[0]
    if all(d == first for d in dtypes[1:]):
        return first

    ranks = [_numeric_rank(d) for d in dtypes]
    if min(ranks) >= 0:
        return nw.Float64 if max(ranks) == 2 else nw.Int64

    if any(d == nw.Object for d in dtypes):
        return nw.Object

    if all(d.is_temporal() for d in dtypes):
        return first

    return nw.String


def concat(frames: Iterable[DataFrame]) -> DataFrame:
    """
    Concatenate dataframes, taking the union of the columns

    Missing columns are filled with nulls and the columns are
    cast to a common dtype. This is like pandas.concat with
    ignore_index=True.
    """
    frames = [df for df in frames if len(df.columns)]
    if not frames:
        raise ValueError("No dataframes to concatenate")
    if len(frames) == 1:
        return frames[0]

    columns: dict[str, list[Any]] = {}
    for df in frames:
        for name, dtype in df.schema.items():
            columns.setdefault(name, []).append(dtype)

    impl = frames[0].implementation
    targets = {
        name: dt
        for name, dtypes in columns.items()
        if len(set(map(str, dtypes))) > 1
        and (dt := _supertype(dtypes)) is not None
    }

    if targets:
        aligned = []
        for df in frames:
            exprs = []
            for name, target in targets.items():
                if name not in df.columns:
                    continue
                dtype = df.schema[name]
                if dtype == target:
                    continue
                if target == nw.Object:
                    exprs.append(
                        series(
                            df[name].to_list(),
                            name,
                            backend=impl,
                            dtype=nw.Object,
                        )
                    )
                elif (
                    target == nw.String
                    and dtype
                    not in (
                        nw.String,
                        nw.Categorical,
                    )
                    and not isinstance(dtype, nw.Enum)
                ):
                    exprs.append(
                        series(
                            [None if v is None else str(v) for v in df[name]],
                            name,
                            backend=impl,
                            dtype=nw.String,
                        )
                    )
                else:
                    exprs.append(nw.col(name).cast(target))
            aligned.append(df.with_columns(*exprs) if exprs else df)
        frames = aligned

    return nw.concat(frames, how="diagonal")


def _sort_key(value: Any) -> tuple[int, Any]:
    # Sort numbers before other types and missing values last
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return (3, 0)
    if isinstance(value, (numbers.Number, np.generic)):
        return (0, value)
    if isinstance(value, str):
        return (1, value)
    return (2, value)


def group_split(
    df: DataFrame, by: str | Sequence[str]
) -> Iterator[tuple[tuple[Any, ...], DataFrame]]:
    """
    Split a dataframe into groups

    The groups are yielded in the sorted order of the keys, and
    groups with missing keys are left out. This matches what pandas
    does with `df.groupby(by, observed=True)`.

    Parameters
    ----------
    df :
        Dataframe
    by :
        Columns to group by
    """
    by = [by] if isinstance(by, str) else list(by)
    if not len(df):
        return

    level_lookup = {}
    for col in by:
        dtype = df.schema[col]
        if isinstance(dtype, nw.Enum) or dtype == nw.Categorical:
            level_lookup[col] = {v: i for i, v in enumerate(levels(df[col]))}

    def key(item: tuple[tuple[Any, ...], Any]):
        return tuple(
            (0, level_lookup[col].get(v, -1))
            if col in level_lookup and v is not None
            else _sort_key(v)
            for col, v in zip(by, item[0])
        )

    groups = list(df.group_by(by, drop_null_keys=True))
    groups.sort(key=key)
    yield from groups


def group_apply(
    df: DataFrame,
    by: str | Sequence[str],
    func: Callable[..., DataFrame],
    *args: Any,
    **kwargs: Any,
) -> DataFrame:
    """
    Split a dataframe into groups, apply func and combine the results

    Parameters
    ----------
    df :
        Dataframe
    by :
        Columns to group by
    func :
        Function to call on each group. It should return a dataframe.
    *args :
        Positional arguments to pass to func
    **kwargs :
        Keyword arguments to pass to func
    """
    if not len(df):
        return df

    results = [func(gdf, *args, **kwargs) for _, gdf in group_split(df, by)]
    results = [r for r in results if r is not None and len(r.columns)]
    if not results:
        return df.head(0)
    return concat(results)


def is_missing(s: Series) -> Series:
    """
    Return a boolean series that is True where values are missing

    A value is missing if it is null or NaN.
    """
    if s.dtype.is_float():
        return s.is_null() | s.is_nan().fill_null(value=True)
    elif s.dtype == nw.Object:
        values = [
            v is None or (isinstance(v, float) and np.isnan(v)) for v in s
        ]
        return series(values, s.name, backend=s.implementation)
    return s.is_null()


def is_finite(s: Series) -> Series:
    """
    Return a boolean series that is True where values are finite

    Missing values are not finite. Values that are not numbers are
    considered finite.
    """
    if s.dtype.is_numeric():
        return s.is_finite().fill_null(value=False)
    return ~is_missing(s)


def filter_rows(df: DataFrame, mask: Any) -> DataFrame:
    """
    Select rows using a boolean mask

    The mask may be a narwhals series, a numpy array or a sequence.
    """
    if not isinstance(mask, nw.Series):
        mask = series(
            np.asarray(mask, dtype=bool), "mask", backend=df.implementation
        )
    return df.filter(mask)


def take(df: DataFrame, indices: Any) -> DataFrame:
    """
    Select rows by position
    """
    indices = np.asarray(indices, dtype=np.int64)
    if not len(indices):
        return df.head(0)
    return df[indices.tolist()]


def levels(s: Series) -> list[Any]:
    """
    Return the levels of a discrete series in their order

    For an Enum, the levels are its categories. For a pandas
    categorical, the levels are the categories that the user
    defined. Otherwise, they are the sorted unique values.
    """
    dtype = s.dtype
    if isinstance(dtype, nw.Enum):
        return list(dtype.categories)

    if s.implementation.is_pandas_like() and dtype == nw.Categorical:
        return list(s.to_native().cat.categories)

    from . import multitype_sort

    uniq = [v for v in s.drop_nulls().unique().to_list() if v == v]
    try:
        return sorted(uniq)
    except TypeError:
        return multitype_sort(uniq)


def is_categorical(s: Series) -> bool:
    """
    Return True if the series is categorical (ordered or not)
    """
    return isinstance(s.dtype, nw.Enum) or s.dtype == nw.Categorical


def is_ordinal(s: Series) -> bool:
    """
    Return True if the series is an ordered categorical

    For pandas, it is a categorical with `ordered=True`. Other
    libraries do not have the concept of an ordered categorical,
    so an Enum, whose categories are fixed and in a meaningful
    order, is taken to be ordinal.
    """
    return isinstance(s.dtype, nw.Enum)


def to_numpy(s: Series) -> np.ndarray:
    """
    Convert a series to a numpy array

    Missing values in float columns become NaN.
    """
    if s.dtype.is_float() and s.null_count():
        s = s.fill_null(float("nan"))
    return s.to_numpy()

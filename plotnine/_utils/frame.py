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
from contextlib import contextmanager, suppress
from contextvars import ContextVar
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

    try:
        df = nw.from_native(data, eager_only=True)
    except TypeError:
        # Objects that are not dataframes but can be turned into
        # a pandas dataframe
        if hasattr(data, "to_pandas"):
            return to_frame(data.to_pandas())
        raise

    if is_pandas_like_dataframe(data):
        df = _normalise_pandas(data)
    return df


def _normalise_pandas(data: Any) -> DataFrame:
    """
    Make a pandas-like dataframe safe for positional row access

    pandas dataframes with a non-default index can bring along
    an index with duplicates that pandas would align on. We only
    ever refer to rows by position. Column names that are not
    strings are converted to strings.
    """
    index = data.index
    if not (
        type(index).__name__ == "RangeIndex"
        and index.start == 0
        and index.step == 1
    ):
        data = data.reset_index(drop=True)
    if not all(isinstance(c, str) for c in data.columns):
        data = data.rename(columns=str)
    return nw.from_native(data, eager_only=True)


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
    has_str, has_other, has_value = False, False, False
    for v in values:
        has_value = has_value or v is not None
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
    if len(values) and not has_value:
        return _ALL_MISSING
    return nw.String if has_str else None


# Values that are all None. They are kept as object values in pandas
# and as strings in other libraries, instead of letting the library
# choose a type (e.g. polars would choose a Null type, which numpy
# turns into NaN floats).
_ALL_MISSING: Any = object()


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
            if is_categorical(s):
                s = categorical(
                    s,
                    levels(s),
                    ordered=is_ordinal(s),
                    name=name,
                    backend=backend,
                )
            else:
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
        values, (pd.api.extensions.ExtensionArray, pd.Index)
    ):
        if backend.is_pandas_like() or isinstance(values, pd.Categorical):
            pds = pd.Series(values, name=name)
            return series(pds, name, backend=backend, dtype=dtype)
        values = np.asarray(values)

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

    if dtype is _ALL_MISSING:
        dtype = nw.Object if backend.is_pandas_like() else nw.String

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
        # A dataframe without columns has no rows, the values
        # determine the number of rows.
        has_vectors = any(not _is_scalar(v) for v in columns.values())
        return frame(columns, backend=impl, n=None if has_vectors else 0)

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

    df = nw.concat(frames, how="diagonal")
    if df.implementation.is_pandas_like():
        df = _normalise_pandas(df.to_native())
    return df


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
    df: DataFrame,
    by: str | Sequence[str],
    drop_missing: bool = True,
    sort: bool = True,
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
    drop_missing :
        Whether to leave out the rows with missing keys. If False,
        they make up groups.
    sort :
        Whether to yield the groups in the sorted order of the keys.
        If False, they are in the order in which they first appear.
    """
    by = [by] if isinstance(by, str) else list(by)
    if not len(df):
        return

    # NaN keys are missing, like nulls
    float_by = [col for col in by if df.schema[col].is_float()]
    if float_by and drop_missing:
        df = df.filter(
            ~nw.any_horizontal(
                *[nw.col(c).is_nan() for c in float_by], ignore_nulls=True
            )
        )

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

    if not sort:
        row = "__plotnine_group_order__"
        groups = list(
            df.with_row_index(row).group_by(by, drop_null_keys=drop_missing)
        )
        groups.sort(key=lambda item: item[1][row].item(0))
        for k, gdf in groups:
            yield k, gdf.drop(row)
        return

    groups = list(df.group_by(by, drop_null_keys=drop_missing))
    groups.sort(key=key)
    yield from groups


def group_indices(
    df: DataFrame,
    by: str | Sequence[str],
    drop_missing: bool = True,
    sort: bool = True,
) -> list[np.ndarray]:
    """
    Return the positions of the rows in each group

    See `group_split` for the parameters.
    """
    row = "__plotnine_row__"
    indexed = df.with_row_index(row)
    return [
        gdf[row].to_numpy()
        for _, gdf in group_split(indexed, by, drop_missing, sort)
    ]


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


# Libraries other than pandas cannot have a categorical with
# a custom order of the categories that is not ordinal (ordered).
# When plotnine creates such a categorical it uses an Enum, and it
# records the categories of the Enum so that it is not taken to be
# ordinal. The records are scoped to the building of a plot.
_NOMINAL_ENUMS: ContextVar[set[tuple[Any, ...]] | None] = ContextVar(
    "nominal_enums", default=None
)


@contextmanager
def nominal_enums_scope() -> Iterator[None]:
    """
    Context in which created nominal Enums are recorded
    """
    token = _NOMINAL_ENUMS.set(set())
    try:
        yield
    finally:
        _NOMINAL_ENUMS.reset(token)


def is_ordinal(s: Series) -> bool:
    """
    Return True if the series is an ordered categorical

    For pandas, it is a categorical with `ordered=True`, which
    narwhals represents as an Enum. Other libraries do not have
    the concept of an ordered categorical, so an Enum, whose
    categories are fixed and in a meaningful order, is taken to be
    ordinal unless plotnine created it as a nominal categorical.

    The nominal Enums are identified by their categories, so within
    a plot, an ordinal Enum with the same categories as a nominal Enum
    is also taken to be nominal.
    """
    dtype = s.dtype
    if not isinstance(dtype, nw.Enum):
        return False
    nominal = _NOMINAL_ENUMS.get()
    return nominal is None or tuple(dtype.categories) not in nominal


def categorical(
    values: Any,
    categories: Sequence[Any] | None = None,
    ordered: bool = False,
    *,
    name: str = "",
    backend: Implementation,
) -> Series:
    """
    Create a categorical series

    Parameters
    ----------
    values :
        Values of the categorical. Values that are not in the
        categories become missing.
    categories :
        The categories in order. If None, they are the sorted
        unique values.
    ordered :
        Whether the categorical is ordinal.
    name :
        Name of the series.
    backend :
        Library that should hold the series.

    Notes
    -----
    For pandas, the result is a pandas categorical that can have
    categories of any type. For other libraries, the result is an
    Enum and the values and categories are converted to strings.
    """
    if isinstance(values, nw.Series) and values.implementation != backend:
        values = values.to_list()

    if categories is None:
        s = (
            values
            if isinstance(values, nw.Series)
            else series(values, backend=backend)
        )
        categories = levels(s)

    if backend.is_pandas_like():
        import pandas as pd

        if isinstance(values, nw.Series):
            values = values.to_native()
        cat = pd.Categorical(values, categories=categories, ordered=ordered)
        return series(pd.Series(cat, name=name), name, backend=backend)

    if isinstance(values, nw.Series):
        values = values.to_list()
    elif isinstance(values, np.ndarray):
        values = values.tolist()

    str_categories = [str(c) for c in categories]
    lookup = {c: str(c) for c in categories}
    str_values = [
        lookup.get(v) if v is not None and v == v else None  # noqa: PLR0124
        for v in values
    ]
    if not ordered and (nominal := _NOMINAL_ENUMS.get()) is not None:
        nominal.add(tuple(str_categories))
    return series(str_values, name, backend=backend, dtype=nw.String).cast(
        nw.Enum(str_categories)
    )


def to_numpy(s: Series) -> np.ndarray:
    """
    Convert a series to a numpy array

    Missing values in float columns become NaN.
    """
    if s.dtype.is_float() and s.null_count():
        s = s.fill_null(float("nan"))
    return s.to_numpy()


def _is_native(obj: Any) -> bool:
    if isinstance(obj, (nw.DataFrame, nw.Series)):
        return False
    try:
        nw.from_native(obj, eager_only=True, allow_series=True)
    except TypeError:
        return False
    return True


def _to_nw(obj: Any) -> tuple[Any, bool]:
    if isinstance(obj, (list, tuple)) and obj and all(map(_is_native, obj)):
        return type(obj)(_to_nw(o)[0] for o in obj), True
    if _is_native(obj):
        if (pd := get_pandas()) is not None and isinstance(obj, pd.DataFrame):
            return to_frame(obj), True
        return nw.from_native(obj, eager_only=True, allow_series=True), True
    return obj, False


def _to_native(obj: Any) -> Any:
    if isinstance(obj, (nw.DataFrame, nw.Series)):
        return obj.to_native()
    if isinstance(obj, (list, tuple)) and any(
        isinstance(o, (nw.DataFrame, nw.Series)) for o in obj
    ):
        return type(obj)(_to_native(o) for o in obj)
    return obj


def native_io(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Let a function that works with narwhals objects accept native ones

    Native dataframe & series arguments are converted to narwhals,
    and if any argument was native, the narwhals return values are
    converted back to native objects.

    plotnine works with narwhals dataframes, but code outside plotnine
    (e.g. extensions) may call these functions with the dataframes of
    the user's library. e.g. a pandas dataframe in gives a pandas
    dataframe out.
    """
    from functools import wraps

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        any_native = False
        new_args = []
        for a in args:
            a, was_native = _to_nw(a)
            any_native |= was_native
            new_args.append(a)
        for k, v in kwargs.items():
            kwargs[k], was_native = _to_nw(v)
            any_native |= was_native

        result = func(*new_args, **kwargs)
        return _to_native(result) if any_native else result

    return wrapper


def is_native_series(obj: Any) -> bool:
    """
    Return True if obj is a series of a library supported by narwhals
    """
    if isinstance(obj, (nw.Series, nw.DataFrame)):
        return False
    try:
        nw.from_native(obj, series_only=True)
    except TypeError:
        return False
    return True


def as_series(obj: Any) -> Series | None:
    """
    Return obj as a narwhals series if it is a (native) series
    """
    if isinstance(obj, nw.Series):
        return obj
    if isinstance(obj, nw.DataFrame):
        return None
    try:
        return nw.from_native(obj, series_only=True)
    except TypeError:
        return None


def as_numpy(obj: Any) -> np.ndarray:
    """
    Convert a series or an array-like to a numpy array
    """
    if (s := as_series(obj)) is not None:
        return to_numpy(s)
    return np.asarray(obj)


def _nw_dtype_kind(dtype: Any) -> str:
    if dtype.is_float() or dtype == nw.Decimal:
        return "f"
    elif dtype.is_signed_integer():
        return "i"
    elif dtype.is_unsigned_integer():
        return "u"
    elif dtype == nw.Boolean:
        return "b"
    elif dtype in (nw.Datetime, nw.Date):
        return "M"
    elif dtype == nw.Duration:
        return "m"
    return "O"


def dtype_kind(arr: Any) -> str:
    """
    Return the numpy dtype kind character of an array-like

    The dtypes of series are mapped to the kind of numpy array
    that pandas would use for them, e.g. strings and categoricals
    are object ("O").
    """
    if (s := as_series(arr)) is not None:
        return _nw_dtype_kind(s.dtype)
    if hasattr(arr, "dtype") and hasattr(arr.dtype, "kind"):
        return arr.dtype.kind
    return np.asarray(arr).dtype.kind


def sort(
    df: DataFrame,
    by: str | Sequence[str],
    descending: bool | Sequence[bool] = False,
    nulls_last: bool = True,
) -> DataFrame:
    """
    Sort a dataframe, keeping the order of rows with equal keys

    Unlike the sort of narwhals (with pandas), this sort is stable.
    """
    by = [by] if isinstance(by, str) else list(by)
    if isinstance(descending, bool):
        descending = [descending] * len(by)
    order = "__plotnine_row_order__"
    return (
        df.with_row_index(order)
        .sort(
            [*by, order],
            descending=[*descending, False],
            nulls_last=nulls_last,
        )
        .drop(order)
    )


def convert(df: DataFrame, backend: Implementation) -> DataFrame:
    """
    Convert a dataframe to another library

    This is meant for small dataframes created by plotnine, e.g. the
    layout of the panels, when layers have data from different
    libraries.
    """
    if df.implementation == backend:
        return df
    if not df.columns:
        return frame(backend=backend)
    return frame(
        {name: series(df[name], name, backend=backend) for name in df.columns},
        backend=backend,
    )


def isna(values: Any) -> np.ndarray:
    """
    Return a boolean array that is True where values are missing

    Missing values are None, NaN and NaT.
    """
    if (s := as_series(values)) is not None:
        return is_missing(s).to_numpy()

    if isinstance(values, np.ndarray):
        arr = values
    else:
        # Keep the items as they are, e.g. strings & NaN or tuples
        arr = np.empty(len(values), dtype=object)
        arr[:] = list(values)
    kind = arr.dtype.kind
    if kind in "fc":
        return np.isnan(arr)
    elif kind in "Mm":
        return np.isnat(arr)
    elif kind == "O":
        if arr.ndim > 1:
            # e.g. tuples that numpy turned into a 2d array
            return np.array(
                [all(_is_na_scalar(v) for v in row) for row in arr], dtype=bool
            )
        return np.array([_is_na_scalar(v) for v in arr.ravel()], dtype=bool)
    return np.zeros(arr.shape, dtype=bool)


def _is_na_scalar(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, (float, np.floating)):
        return bool(np.isnan(v))
    if isinstance(v, (np.datetime64, np.timedelta64)):
        return bool(np.isnat(v))
    # pandas NA & NaT
    return type(v).__name__ in ("NAType", "NaTType")


def scale_values(s: Series) -> Any:
    """
    Return the values of a column in the form that scales use

    Categorical columns stay series so that the order of the levels
    is known, other columns become numpy arrays.
    """
    if is_categorical(s):
        return s
    return to_numpy(s)


def frame_like(
    df: DataFrame | Series,
    data: Mapping[str, Any] | None = None,
    n: int | None = None,
) -> DataFrame:
    """
    Create a dataframe with the same library as df

    See `frame` for the parameters.
    """
    return frame(data, backend=df.implementation, n=n)


def backend_of(obj: Any) -> Implementation:
    """
    Return the library of a (native) dataframe or series

    For other objects, e.g. numpy arrays, it is the default library.
    """
    if isinstance(obj, (nw.DataFrame, nw.Series)):
        return obj.implementation
    with suppress(TypeError):
        return nw.from_native(
            obj, eager_only=True, allow_series=True
        ).implementation
    return default_backend()


def _hashable(value: Any) -> Any:
    try:
        hash(value)
    except TypeError:
        return repr(value)
    return value


def unique_rows(
    df: DataFrame, subset: Sequence[str] | None = None
) -> DataFrame:
    """
    Remove duplicate rows, keeping the first of each in order

    Unlike `DataFrame.unique`, it works with object columns.

    Parameters
    ----------
    df :
        Dataframe
    subset :
        Columns that identify a duplicate. If None, all columns.
    """
    cols = list(subset) if subset is not None else df.columns
    if not any(df.schema[c] == nw.Object for c in cols):
        return df.unique(subset, keep="first", maintain_order=True)

    seen = set()
    keep = np.zeros(len(df), dtype=bool)
    rows = zip(*(df[c].to_list() for c in cols))
    for i, row in enumerate(rows):
        key = tuple(_hashable(v) for v in row)
        if key not in seen:
            seen.add(key)
            keep[i] = True
    return filter_rows(df, keep)


def inner_join(left: DataFrame, right: DataFrame) -> DataFrame:
    """
    Join two dataframes on the columns that they have in common

    The order of the rows of `left` is preserved. This is like
    `pandas.merge(left, right)` and it works for object columns. It
    is meant for small dataframes.
    """
    common = [c for c in left.columns if c in right.columns]

    def keys(df: DataFrame) -> Iterator[tuple[Any, ...]]:
        rows = zip(*(df[c].to_list() for c in common))
        return (tuple(_hashable(v) for v in row) for row in rows)

    lookup: dict[tuple[Any, ...], list[int]] = {}
    for j, key in enumerate(keys(right)):
        lookup.setdefault(key, []).append(j)

    left_idx, right_idx = [], []
    for i, key in enumerate(keys(left)):
        for j in lookup.get(key, []):
            left_idx.append(i)
            right_idx.append(j)

    result = take(left, left_idx)
    others = [c for c in right.columns if c not in common]
    if others:
        extra = convert(
            take(right.select(others), right_idx), left.implementation
        )
        result = nw.concat([result, extra], how="horizontal")
    return result


def row_dict(df: DataFrame, i: int) -> dict[str, Any]:
    """
    Return row i of a dataframe as a dict

    Raises IndexError if there is no row i.
    """
    if not -len(df) <= i < len(df):
        raise IndexError(f"Row {i} is out of range.")
    return dict(zip(df.columns, df.row(i)))

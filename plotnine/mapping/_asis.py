from __future__ import annotations

import ast
import re
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from pandas.api.extensions import (
    ExtensionArray,
    ExtensionDtype,
    ExtensionScalarOpsMixin,  # pyright: ignore[reportAttributeAccessIssue]
    register_extension_dtype,
    take,
)

if TYPE_CHECKING:
    from typing import Any, Iterable, Sequence

    from numpy import _DTypeKind as DtypeKind
    from pandas._typing import TakeIndexer


__all__ = ("I",)

NAME_RE = re.compile(r"^asis\[(?P<subtype>.+)\]$")


@register_extension_dtype
class AsIsDtype(ExtensionDtype):
    """
    Dtype for a column whose values bypass scales

    The dtype stores the tag and the NumPy dtype of the values. Dataframe
    operations that preserve dtypes therefore preserve the tag, while
    `kind` and `type` keep the column's usual scale classification.
    """

    def __init__(self, subtype: Any = None):
        self._subtype = np.dtype(object if subtype is None else subtype)

    @property
    def subtype(self) -> np.dtype:
        """
        NumPy dtype of the underlying values
        """
        return self._subtype

    @property
    def name(self) -> str:  # pyright: ignore[reportIncompatibleVariableOverride]
        """
        Name of the dtype, e.g. `asis[float64]`
        """
        return f"asis[{self._subtype}]"

    @property
    def kind(self) -> DtypeKind:
        """
        Character code of the underlying NumPy dtype
        """
        return self._subtype.kind

    @property
    def type(self) -> type:  # pyright: ignore[reportIncompatibleVariableOverride]
        """
        Scalar type of the underlying NumPy dtype
        """
        return self._subtype.type

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            try:
                other = type(self).construct_from_string(other)
            except TypeError:
                return False
        return isinstance(other, AsIsDtype) and self._subtype == other._subtype

    def __hash__(self) -> int:
        return hash(("asis", self._subtype))

    @classmethod
    def construct_from_string(cls, string: str) -> AsIsDtype:
        """
        Construct a dtype from its name, such as `asis[float64]`
        """
        if not (m := NAME_RE.match(string)):
            raise TypeError(f"Cannot construct an AsIsDtype from {string!r}")
        return cls(np.dtype(m.group("subtype")))

    def construct_array_type(self) -> type[AsIsArray]:
        """
        Return the extension array type for this dtype
        """
        return AsIsArray


class AsIsArray(ExtensionArray, ExtensionScalarOpsMixin):
    """
    Extension array of literal values backed by a NumPy array

    The values remain ordinary; the dtype carries the literal tag that
    scales inspect. Comparing tagged arrays, such as `I(x) == I(y)`,
    returns an untagged boolean array, so the derived column trains a
    scale like any other expression.
    """

    _values: np.ndarray

    def __init__(self, values: Any):
        arr = np.asarray(values)
        # Fixed-width Unicode cannot hold the missing value expected by
        # a pandas object column.
        if arr.dtype.kind in "US":
            arr = arr.astype(object)
        self._values = arr

    @classmethod
    def _from_sequence(
        cls,
        scalars: Iterable[Any],
        *,
        dtype: Any = None,
        copy: bool = False,
    ) -> AsIsArray:
        """
        Construct an array from a sequence of values
        """
        if isinstance(scalars, cls):
            scalars = scalars._values
        arr = np.asarray(scalars)
        if isinstance(dtype, AsIsDtype):
            arr = arr.astype(dtype.subtype)
        elif copy:
            arr = arr.copy()
        return cls(arr)

    @classmethod
    def _from_factorized(
        cls, values: np.ndarray, original: AsIsArray
    ) -> AsIsArray:
        """
        Construct an array from `factorize` output
        """
        return cls(values)

    @classmethod
    def _concat_same_type(cls, to_concat: Sequence[AsIsArray]) -> AsIsArray:
        """
        Concatenate arrays of this type

        The subtypes may differ, so the values are promoted to a
        common numpy dtype first. Values with nothing in common
        become objects.
        """
        subtypes = [a._values.dtype for a in to_concat]
        try:
            common = np.result_type(*subtypes)
        except TypeError:
            common = np.dtype(object)
        return cls(
            np.concatenate([a._values.astype(common) for a in to_concat])
        )

    @property
    def dtype(self) -> AsIsDtype:
        """
        Dtype marking the values as literal
        """
        return AsIsDtype(self._values.dtype)

    @property
    def nbytes(self) -> int:
        """
        Number of bytes occupied by the values
        """
        return self._values.nbytes

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, item: Any) -> Any:
        result = self._values[item]
        if np.isscalar(result) or result is None or result is np.nan:
            return result
        if isinstance(item, (int, np.integer)):
            return result
        return type(self)(result)

    def __setitem__(self, key: Any, value: Any) -> None:
        if isinstance(value, AsIsArray):
            value = value._values
        self._values[key] = value

    def __array__(self, dtype: Any = None, copy: Any = None) -> np.ndarray:
        return np.asarray(self._values, dtype=dtype)

    def isna(self) -> np.ndarray:
        """
        Return a mask identifying missing values
        """
        return pd.isna(self._values)

    def take(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        indices: TakeIndexer,
        *,
        allow_fill: bool = False,
        fill_value: Any = None,
    ) -> AsIsArray:
        """
        Return values at the requested positions
        """
        if allow_fill and fill_value is None:
            fill_value = self.dtype.na_value
        return type(self)(
            take(
                self._values,
                indices,
                fill_value=fill_value,
                allow_fill=allow_fill,
            )
        )

    def copy(self) -> AsIsArray:
        """
        Return an independent copy of the array
        """
        return type(self)(self._values.copy())

    def astype(self, dtype: Any, copy: bool = True) -> Any:
        """
        Cast the values to another dtype

        Casting to anything but this dtype drops the tag, because
        the result is no longer a column of literal values.
        """
        dtype = pd.api.types.pandas_dtype(dtype)
        if isinstance(dtype, AsIsDtype):
            return self.copy() if copy else self
        if isinstance(dtype, ExtensionDtype):
            cls = dtype.construct_array_type()
            return cls._from_sequence(self._values, dtype=dtype, copy=copy)  # pyright: ignore[reportAttributeAccessIssue]
        return self._values.astype(dtype, copy=copy)

    def _values_for_factorize(self) -> tuple[np.ndarray, Any]:
        return self._values.astype(object), np.nan


# Comparisons, such as `I(x) == I(y)`, return plain booleans, so they
# train a scale like any other expression. Leave arithmetic undefined:
# `I(a) + I(b)` raises, matching the untagged `AsIs` it replaces.
AsIsArray._add_comparison_ops()

# Expose the shorter name used in public signatures. `AsIsArray` follows
# pandas' extension-array convention, while `AsIs` describes its purpose.
AsIs = AsIsArray


def I(x: Any) -> Any:  # noqa: E743
    """
    Mark an aesthetic value as literal

    A literal value bypasses scales, reaches the geom unchanged, and
    contributes no training data, mapping, or legend. Use it to mix
    literal and scaled values for one aesthetic across layers.

    For position aesthetics (`x`, `y`, and their `min`/`max`/`end`/
    `intercept` variants), the value represents a fraction of the
    expanded panel range. `I(0)` and `I(1)` mark the panel edges,
    `I(0.5)` marks its centre, and values outside `0` to `1` fall
    outside the panel and are clipped like other out-of-range data.
    Use this form to place annotations relative to the panel.

    Parameters
    ----------
    x :
        Value, or array of values, to use literally.

    Returns
    -------
    :
        The values in a column that bypasses scales.

    Notes
    -----
    Use `I()` with `stat_identity`, the default stat for most geoms.
    Behaviour through another stat or through `position_stack` /
    `position_dodge` is undefined.
    """
    if is_asis(x):
        return x
    return AsIsArray._from_sequence(np.atleast_1d(x))


def is_asis(value: Any) -> bool:
    """
    Return whether a value carries the literal tag
    """
    return isinstance(getattr(value, "dtype", None), AsIsDtype)


def asis_columns(data: pd.DataFrame) -> set[str]:
    """
    Return the columns in `data` that carry the literal tag
    """
    return {str(col) for col in data.columns if is_asis(data[col])}


def is_literal_expression(value: Any) -> bool:
    """
    Return whether a value is an unevaluated `I(...)` expression

    `annotate` and `aes()` can record `I()` as source text, such as
    `"I(x)"`, before evaluating the layer data. This detects the
    expression before evaluation produces an `AsIsDtype` value.

    The expression must be a single call to `I`. A compound expression
    such as `"I(a) == I(b)"` keeps its ordinary label. Invalid Python,
    including a column name with spaces or punctuation, is not a
    literal expression.
    """
    if not isinstance(value, str):
        return False
    try:
        node = ast.parse(value.strip(), mode="eval").body
    except (SyntaxError, ValueError):
        return False
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "I"
    )

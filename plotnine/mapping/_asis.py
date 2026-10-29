from __future__ import annotations

import ast
import operator
from typing import TYPE_CHECKING

import numpy as np

from .._utils import frame

if TYPE_CHECKING:
    from typing import Any


__all__ = ("I",)


class AsIs:
    """
    Values that bypass scales

    The values are held in a numpy array. Comparing literal values,
    such as `I(x) == I(y)`, returns an ordinary boolean array, so
    the derived column trains a scale like any other expression.
    Arithmetic is not defined.
    """

    __array_priority__ = 1000

    def __init__(self, values: Any):
        if isinstance(values, AsIs):
            values = values._values
        elif (s := frame.as_series(values)) is not None:
            values = frame.to_numpy(s)
        arr = np.atleast_1d(np.asarray(values))
        # Fixed-width Unicode cannot hold missing values
        if arr.dtype.kind in "US":
            arr = arr.astype(object)
        self._values: np.ndarray = arr

    def to_numpy(self) -> np.ndarray:
        """
        Return the values as a numpy array
        """
        return self._values

    @property
    def dtype(self) -> np.dtype:
        return self._values.dtype

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def __getitem__(self, item: Any) -> Any:
        result = self._values[item]
        if isinstance(result, np.ndarray):
            return AsIs(result)
        return result

    def __array__(self, dtype: Any = None, copy: Any = None) -> np.ndarray:
        return np.asarray(self._values, dtype=dtype)

    def __repr__(self) -> str:
        return f"I({self._values!r})"

    def _compare(self, other: Any, op: Any) -> np.ndarray:
        if isinstance(other, AsIs):
            other = other._values
        return op(self._values, other)

    def __eq__(self, other: object) -> np.ndarray:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._compare(other, operator.eq)

    def __ne__(self, other: object) -> np.ndarray:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self._compare(other, operator.ne)

    def __lt__(self, other: Any) -> np.ndarray:
        return self._compare(other, operator.lt)

    def __le__(self, other: Any) -> np.ndarray:
        return self._compare(other, operator.le)

    def __gt__(self, other: Any) -> np.ndarray:
        return self._compare(other, operator.gt)

    def __ge__(self, other: Any) -> np.ndarray:
        return self._compare(other, operator.ge)

    __hash__ = None  # pyright: ignore[reportAssignmentType]


# The name of the class before it stopped being a pandas extension array
AsIsArray = AsIs


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
    return AsIs(x)


def is_asis(value: Any) -> bool:
    """
    Return whether a value carries the literal tag
    """
    return isinstance(value, AsIs)


def is_literal_expression(value: Any) -> bool:
    """
    Return whether a value is an unevaluated `I(...)` expression

    `annotate` and `aes()` can record `I()` as source text, such as
    `"I(x)"`, before evaluating the layer data. This detects the
    expression before evaluation produces an `AsIs` value.

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

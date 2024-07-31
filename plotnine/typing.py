from __future__ import annotations

import sys
from datetime import datetime, timedelta
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Literal,
    Protocol,
    Sequence,
    TypeVar,
)

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from typing_extensions import TypeAlias  # noqa: TCH002


class DataFrameConvertible(Protocol):
    """
    Object that can be converted to a DataFrame
    """

    def to_pandas(self) -> pd.DataFrame:
        """
        Convert to pandas dataframe

        Returns
        -------
        :
            Pandas representation of this object.
        """
        ...


# Arrays (strictly numpy)
AnyArray: TypeAlias = NDArray[Any]
BoolArray: TypeAlias = NDArray[np.bool_]
FloatArray: TypeAlias = NDArray[np.float64]
IntArray: TypeAlias = NDArray[np.int64]
StrArray: TypeAlias = NDArray[np.str_]

# Series
AnySeries: TypeAlias = pd.Series[Any]
IntSeries: TypeAlias = pd.Series[int]
FloatSeries: TypeAlias = pd.Series[float]

# ArrayLikes
AnyArrayLike: TypeAlias = AnyArray | pd.Series[Any] | Sequence[Any]
IntArrayLike: TypeAlias = IntArray | IntSeries | Sequence[int]
FloatArrayLike: TypeAlias = FloatArray | FloatSeries | Sequence[float]

# Input data can be a DataFrame, a DataFrame factory or things that
# are convertible to DataFrames.
# `Data` is mostly used internally and `DataLike` is the input type
# before automatic conversion.
# Input data can actually also contain DataFrameGroupBy which is
# specially handled, but pandas doesn't expose that data type in
# their type stubs and instead treats it the same as a DataFrame
# (df.groupby() returns a DataFrame in the stubs).
Data: TypeAlias = pd.DataFrame | Callable[[pd.DataFrame], pd.DataFrame]
DataLike: TypeAlias = Data | DataFrameConvertible

LayerData: TypeAlias = pd.DataFrame | Callable[[pd.DataFrame], pd.DataFrame]
LayerDataLike: TypeAlias = LayerData | DataFrameConvertible
ColorLike: TypeAlias = str
ColorsLike: TypeAlias = (
    ColorLike | list[ColorLike] | pd.Series[ColorLike] | StrArray
)

# Plotting
FigureFormat: TypeAlias = Literal["png", "retina", "jpeg", "jpg", "svg", "pdf"]

# Facet strip

# Facet space
FacetSpaceRatios: TypeAlias = dict[Literal["x", "y"], Sequence[float]]

StripPosition: TypeAlias = Literal["top", "right"]

## Scales

# Name names of scaled aesthetics
ScaledAestheticsName: TypeAlias = Literal[
    "x",
    "xmin",
    "xmax",
    "xend",
    "xintercept",
    "y",
    "ymin",
    "ymax",
    "yend",
    "yintercept",
    "alpha",
    "color",
    "colour",
    "fill",
    "linetype",
    "shape",
    "size",
    "stroke",
    # boxplot
    "ymax_final",
    "ymin_final",
    "lower",
    "middle",
    "upper",
]

## Coords
CoordRange: TypeAlias = tuple[float, float]

# Guide
SidePosition: TypeAlias = Literal["left", "right", "top", "bottom"]
LegendPosition: TypeAlias = (
    Literal["left", "right", "top", "bottom", "inside"] | tuple[float, float]
)
Orientation: TypeAlias = Literal["horizontal", "vertical"]
GuideKind: TypeAlias = Literal["legend", "colorbar", "colourbar"]
NoGuide: TypeAlias = Literal["none", False]
VerticalJustification: TypeAlias = Literal["bottom", "center", "top"]
HorizontalJustification: TypeAlias = Literal["left", "center", "right"]
TextJustification: TypeAlias = (
    VerticalJustification | HorizontalJustification | Literal["baseline"]
)

# Type Variables
# A array variable we can pass to a transforming function and expect
# result to be of the same type
TFloatArrayLike = TypeVar("TFloatArrayLike", bound=FloatArrayLike)

# Column transformation function
TransformCol: TypeAlias = Callable[[FloatSeries], FloatSeries | FloatArray]


class PTransform(Protocol):
    """
    Transform function
    """

    def __call__(self, x: TFloatArrayLike) -> TFloatArrayLike: ...

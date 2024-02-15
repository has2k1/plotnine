from __future__ import annotations

import sys
from typing import (
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

from plotnine import ggplot, guide_colorbar, guide_legend
from plotnine.iapi import strip_label_details


class PlotAddable(Protocol):
    """
    Object that can be added to a ggplot object
    """

    def __radd__(self, plot: ggplot) -> ggplot:
        """
        Add to ggplot object

        Parameters
        ----------
        other :
            ggplot object

        Returns
        -------
        :
            ggplot object
        """
        ...


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


# Tuples
TupleInt2: TypeAlias = tuple[int, int]
TupleFloat2: TypeAlias = tuple[float, float]
TupleFloat3: TypeAlias = tuple[float, float, float]
TupleFloat4: TypeAlias = tuple[float, float, float, float]

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

# Type Variables
# A array variable we can pass to a transforming function and expect
# result to be of the same type
TFloatArrayLike = TypeVar("TFloatArrayLike", bound=FloatArrayLike)

# Column transformation function
TransformCol: TypeAlias = Callable[[FloatSeries], FloatSeries | FloatArray]

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
StripLabellingFuncNames: TypeAlias = Literal[
    "label_value", "label_both", "label_context"
]

# Facet space
FacetSpaceRatios: TypeAlias = dict[Literal["x", "y"], Sequence[float]]

# Function that can facet strips
StripLabellingFunc: TypeAlias = Callable[
    [strip_label_details], strip_label_details
]

StripLabellingDict: TypeAlias = (
    dict[str, str] | dict[str, Callable[[str], str]]
)

# Can be coerced to a StripLabellingFunc
CanBeStripLabellingFunc: TypeAlias = (
    StripLabellingFuncNames
    | StripLabellingFunc
    | Callable[[str], str]
    | StripLabellingDict
)

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
]

# limits
ScaleContinuousLimits: TypeAlias = TupleFloat2
ScaleDiscreteLimits: TypeAlias = Sequence[str]
ScaleLimits: TypeAlias = ScaleContinuousLimits | ScaleDiscreteLimits

ScaleLimitsRaw: TypeAlias = (
    None | ScaleLimits | Callable[[ScaleLimits], ScaleLimits]
)
ScaleContinuousLimitsRaw: TypeAlias = (
    None
    | ScaleContinuousLimits
    | Callable[[ScaleContinuousLimits], ScaleContinuousLimits]
)
ScaleDiscreteLimitsRaw: TypeAlias = (
    None
    | ScaleDiscreteLimits
    | Callable[[ScaleDiscreteLimits], ScaleDiscreteLimits]
)

# Breaks
ScaleContinuousBreaks: TypeAlias = Sequence[float]
ScaleDiscreteBreaks: TypeAlias = Sequence[str]
ScaleBreaks: TypeAlias = ScaleContinuousBreaks | ScaleDiscreteBreaks

ScaleBreaksRaw: TypeAlias = (
    bool | None | ScaleBreaks | Callable[[ScaleLimits], ScaleBreaks]
)
ScaleContinuousBreaksRaw: TypeAlias = (
    bool
    | None
    | ScaleContinuousBreaks
    | Callable[[ScaleContinuousLimits], ScaleContinuousBreaks]
)
ScaleDiscreteBreaksRaw: TypeAlias = (
    bool
    | None
    | ScaleDiscreteBreaks
    | Callable[[ScaleDiscreteLimits], ScaleDiscreteBreaks]
)
ScaleMinorBreaksRaw: TypeAlias = ScaleContinuousBreaksRaw | int

# Labels
ScaleLabelsRaw: TypeAlias = (
    bool
    | None
    | Sequence[str]
    | Callable[[ScaleBreaks], Sequence[str]]
    | dict[str, str]
)
ScaleLabels: TypeAlias = Sequence[str]

## Coords
CoordRange: TypeAlias = TupleFloat2

# Guide
SidePosition: TypeAlias = Literal["left", "right", "top", "bottom"]
LegendPosition: TypeAlias = (
    Literal["left", "right", "top", "bottom", "inside"] | tuple[float, float]
)
Orientation: TypeAlias = Literal["horizontal", "vertical"]
GuideKind: TypeAlias = Literal["legend", "colorbar", "colourbar"]
LegendOrColorbar: TypeAlias = (
    guide_legend | guide_colorbar | Literal["legend", "colorbar"]
)
NoGuide: TypeAlias = Literal["none", False]
LegendOnly: TypeAlias = guide_legend | Literal["legend"]
VerticalJustification: TypeAlias = Literal["bottom", "center", "top"]
HorizontalJustification: TypeAlias = Literal["left", "center", "right"]
TextJustification: TypeAlias = (
    VerticalJustification | HorizontalJustification | Literal["baseline"]
)

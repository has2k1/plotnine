from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Literal,
    NotRequired,
    Protocol,
    Sequence,
    TypedDict,
    TypeVar,
)

import numpy as np
from numpy.typing import NDArray
from typing_extensions import TypeAlias  # noqa: TCH002

if TYPE_CHECKING:
    import pandas as pd
    from narwhals.typing import IntoDataFrame


class DataFrameConvertible(Protocol):
    """
    Object that can be converted to a DataFrame
    """

    def to_pandas(self) -> Any:
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
FloatArray: TypeAlias = NDArray[np.floating]
IntArray: TypeAlias = NDArray[np.int64]
StrArray: TypeAlias = NDArray[np.str_]

# Series. At runtime, they can be series of any dataframe library
# supported by narwhals (e.g. pandas or polars). For static type
# checking, they are described with pandas series.
AnySeries: TypeAlias = "pd.Series[Any]"
IntSeries: TypeAlias = "pd.Series[int]"
FloatSeries: TypeAlias = "pd.Series[float]"

# ArrayLikes
AnyArrayLike: TypeAlias = "AnyArray | AnySeries | Sequence[Any]"
IntArrayLike: TypeAlias = "IntArray | IntSeries | Sequence[int]"
FloatArrayLike: TypeAlias = "FloatArray | FloatSeries | Sequence[float]"

# Input data can be a dataframe of any library supported by narwhals
# (e.g. pandas and polars), a dataframe factory or things that are
# convertible to dataframes.
# `Data` is mostly used internally and `DataLike` is the input type
# before automatic conversion.
# Input data can also be a pandas DataFrameGroupBy which is specially
# handled.
Data: TypeAlias = "IntoDataFrame | Callable[[Any], IntoDataFrame]"
DataLike: TypeAlias = "Data | DataFrameConvertible"

LayerData: TypeAlias = "IntoDataFrame | Callable[[Any], IntoDataFrame]"
LayerDataLike: TypeAlias = "LayerData | DataFrameConvertible"
ColorLike: TypeAlias = str
ColorsLike: TypeAlias = "ColorLike | list[ColorLike] | AnySeries | StrArray"

# NumPy random-number generators accepted by plotnine
RandomGenerator: TypeAlias = np.random.RandomState | np.random.Generator

# Integer seed or generator accepted by random-state parameters
RandomStateLike: TypeAlias = int | RandomGenerator

# Plotting
FigureFormat: TypeAlias = Literal["png", "retina", "jpeg", "jpg", "svg", "pdf"]

# Facet strip

# Facet space
FacetSpaceRatios: TypeAlias = dict[Literal["x", "y"], Sequence[float]]

StripPosition: TypeAlias = Literal["top", "right", "bottom", "left"]

# Scales

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

# Coords
CoordRange: TypeAlias = tuple[float, float]

# Guide
Side: TypeAlias = Literal["left", "right", "top", "bottom"]
PolarSide: TypeAlias = Literal[
    "theta_inside", "theta_outside", "r_start", "r_end"
]
"""
A side of a polar panel's theta or r axis

`"theta_inside"`/`"theta_outside"` are the donut-hole and rim boundaries
of the angular axis; `"r_start"`/`"r_end"` are the start-angle and
end-angle spokes of the radial axis.
"""
LegendPosition: TypeAlias = (
    Literal["left", "right", "top", "bottom", "inside"] | tuple[float, float]
)
Orientation: TypeAlias = Literal["horizontal", "vertical"]
GuideKind: TypeAlias = Literal[
    "bins",
    "colorbar",
    "colorsteps",
    "colourbar",
    "coloursteps",
    "legend",
]
NoGuide: TypeAlias = Literal["none", False]
VerticalJustification: TypeAlias = Literal["bottom", "center", "top"]
HorizontalJustification: TypeAlias = Literal["left", "center", "right"]
Justification: TypeAlias = HorizontalJustification | VerticalJustification
HorizontalTextJustification: TypeAlias = HorizontalJustification
VerticalTextJustification: TypeAlias = (
    VerticalJustification | Literal["baseline", "center_baseline"]
)
TextJustification: TypeAlias = (
    HorizontalTextJustification | VerticalTextJustification
)

# Type Variables
# A array variable we can pass to a transforming function and expect
# result to be of the same type
TFloatArrayLike = TypeVar("TFloatArrayLike", bound=FloatArrayLike)

# Column transformation function
TransformCol: TypeAlias = Callable[[FloatArray], FloatSeries | FloatArray]


class PTransform(Protocol):
    """
    Transform function
    """

    def __call__(self, x: TFloatArrayLike) -> TFloatArrayLike: ...


class DisplayMetadata(TypedDict):
    """
    Metadata for the IPython output
    """

    width: NotRequired[int]
    height: NotRequired[int]


MimeBundle: TypeAlias = tuple[dict[str, str], dict[str, DisplayMetadata]]

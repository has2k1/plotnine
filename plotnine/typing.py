from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typing import (
        Any,
        Callable,
        Dict,
        Literal,
        Protocol,
        Sequence,
        TypeVar,
    )

    import numpy as np
    import numpy.typing as npt
    import pandas as pd
    from matplotlib.artist import Artist
    from matplotlib.axes import Axes
    from matplotlib.axis import Axis, XAxis, XTick, YAxis, YTick
    from matplotlib.figure import Figure
    from matplotlib.offsetbox import DrawingArea
    from matplotlib.patches import PathPatch
    from matplotlib.text import Text
    from mizani.transforms import trans
    from patsy.eval import EvalEnvironment
    from typing_extensions import TypeAlias

    from plotnine.coords.coord import coord
    from plotnine.facets.facet import facet
    from plotnine.facets.facet_grid import facet_grid
    from plotnine.facets.facet_wrap import facet_wrap
    from plotnine.facets.layout import Layout
    from plotnine.facets.strips import Strips
    from plotnine.geoms.geom import geom
    from plotnine.ggplot import ggplot
    from plotnine.guides.guide import guide
    from plotnine.iapi import strip_label_details
    from plotnine.layer import Layers, layer
    from plotnine.mapping.aes import aes
    from plotnine.positions.position import position
    from plotnine.scales.scale import scale, scale_continuous, scale_discrete
    from plotnine.scales.scales import Scales
    from plotnine.stats.stat import stat
    from plotnine.themes.theme import theme
    from plotnine.watermark import watermark

    class PlotAddable(Protocol):
        """
        Object that can be added to a ggplot object
        """

        def __radd__(self, other: ggplot) -> ggplot:
            """
            Add to ggplot object
            """
            ...

    class DataFrameConvertible(Protocol):
        """
        Object that can be converted to a DataFrame
        """

        def to_pandas(self) -> pd.DataFrame:
            """
            Convert to pandas dataframe
            """
            ...

    # Tuples
    TupleInt2: TypeAlias = tuple[int, int]
    TupleFloat2: TypeAlias = tuple[float, float]
    TupleFloat3: TypeAlias = tuple[float, float, float]
    TupleFloat4: TypeAlias = tuple[float, float, float, float]

    # Arrays (strictly numpy)
    AnyArray: TypeAlias = npt.NDArray[Any]
    BoolArray: TypeAlias = npt.NDArray[np.bool_]
    FloatArray: TypeAlias = npt.NDArray[np.float64]
    IntArray: TypeAlias = npt.NDArray[np.int64]
    StrArray: TypeAlias = npt.NDArray[np.str_]

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
    FloatArrayLikeTV = TypeVar(
        "FloatArrayLikeTV",
        # We cannot use FloatArrayLike type because pyright expect
        # the result to be a FloatArrayLike
        FloatArray,
        FloatSeries,
        Sequence[float],
        TupleFloat2,
    )

    # Column transformation function
    TransformCol = Callable[[FloatSeries], FloatSeries | FloatArray]

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

    LayerData: TypeAlias = (
        pd.DataFrame | Callable[[pd.DataFrame], pd.DataFrame]
    )
    LayerDataLike: TypeAlias = LayerData | DataFrameConvertible
    ColorLike: TypeAlias = str | Literal["None", "none"]
    ColorsLike: TypeAlias = (
        ColorLike | list[ColorLike] | pd.Series[ColorLike] | StrArray
    )

    # Mizani
    Trans: TypeAlias = trans

    # Facet strip
    StripLabellingFuncNames: TypeAlias = Literal[
        "label_value", "label_both", "label_context"
    ]

    # Function that can facet strips
    StripLabellingFunc: TypeAlias = Callable[
        [strip_label_details], strip_label_details
    ]

    StripLabellingDict: TypeAlias = (
        Dict[str, str] | Dict[str, Callable[[str], str]]
    )

    # Can be coerced to a StripLabellingFunc
    CanBeStripLabellingFunc: TypeAlias = (
        StripLabellingFuncNames
        | StripLabellingFunc
        | Callable[[str], str]
        | StripLabellingDict
    )

    StripPosition: TypeAlias = Literal["top", "right"]

    # Plotnine Classes
    Aes: TypeAlias = aes
    Coord: TypeAlias = coord
    Facet: TypeAlias = facet
    FacetGrid: TypeAlias = facet_grid
    FacetWrap: TypeAlias = facet_wrap
    Geom: TypeAlias = geom
    Ggplot: TypeAlias = ggplot
    Guide: TypeAlias = guide
    Layer: TypeAlias = layer
    Position: TypeAlias = position
    Scale: TypeAlias = scale
    ScaleContinuous: TypeAlias = scale_continuous
    ScaleDiscrete: TypeAlias = scale_discrete
    Stat: TypeAlias = stat
    Theme: TypeAlias = theme
    Watermark: TypeAlias = watermark

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

    # Legend
    LegendPosition: TypeAlias = (
        Literal["left", "right", "top", "bottom"] | tuple[float, float]
    )

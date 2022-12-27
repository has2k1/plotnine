from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typing import Callable, Literal, Protocol

    import numpy as np
    import numpy.typing as npt
    import pandas as pd
    from typing_extensions import TypeAlias

    import plotnine as p9

    class PlotAddable(Protocol):
        """
        Object that can be added to a ggplot object
        """

        def __radd__(self, other: p9.ggplot) -> p9.ggplot:
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

    # Input data can be a DataFrame, a DataFrame factory or things that
    # are convertible to DataFrames.
    # `Data` is mostly used internally and `DataLike` is the input type
    # before automatic conversion.
    # Input data can actually also contain DataFrameGroupBy which is
    # specially handled, but pandas doesn't expose that data type in
    # their type stubs and instead treats it the same as a DataFrame
    # (df.groupby() returns a DataFrame in the stubs).
    Data: TypeAlias = "pd.DataFrame | Callable[[], pd.DataFrame]"
    DataLike: TypeAlias = "Data | DataFrameConvertible"

    LayerData: TypeAlias = (
        "pd.DataFrame | Callable[[pd.DataFrame], pd.DataFrame]"
    )
    LayerDataLike: TypeAlias = "LayerData | DataFrameConvertible"
    ColorLike: TypeAlias = "str | Literal['None', 'none']"
    ColorsLike: TypeAlias = (
        "ColorLike | list[ColorLike] | pd.Series[ColorLike] | "
        "npt.NDArray[np.str_]"
    )

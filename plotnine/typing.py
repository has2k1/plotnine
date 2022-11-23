from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typing import Callable, Protocol

    import pandas as pd
    from typing_extensions import TypeAlias

    import plotnine as p9

    class PlotAddable(Protocol):
        def __radd__(self, other: p9.ggplot) -> p9.ggplot:
            ...

    class DataFrameConvertible(Protocol):
        def to_pandas(self) -> pd.DataFrame:
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

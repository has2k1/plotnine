from __future__ import annotations

import typing

from .facet import facet, layout_null

if typing.TYPE_CHECKING:
    import pandas as pd


class facet_null(facet):
    """
    A single Panel

    Parameters
    ----------
    shrink : bool, default=True
        Whether to shrink the scales to the output of the
        statistics instead of the raw data.
    """

    def __init__(self, shrink: bool = True):
        facet.__init__(self, shrink=shrink)
        self.nrow = 1
        self.ncol = 1

    def map(self, data: pd.DataFrame, layout: pd.DataFrame) -> pd.DataFrame:
        data["PANEL"] = 1
        return data

    def compute_layout(
        self,
        data: list[pd.DataFrame],
    ) -> pd.DataFrame:
        return layout_null()

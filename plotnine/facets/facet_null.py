from __future__ import annotations

import typing

from .._utils import frame
from .._utils.frame import native_io
from .facet import facet, layout_null

if typing.TYPE_CHECKING:
    from plotnine._utils.frame import DataFrame

    from ..scales.scales import Scales


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

    @native_io
    def map(self, data: DataFrame, layout: DataFrame) -> DataFrame:
        return frame.assign(data, PANEL=1)

    def compute_layout(
        self,
        data: list[DataFrame],
        scales: Scales,
    ) -> DataFrame:
        return layout_null(data[0].implementation)

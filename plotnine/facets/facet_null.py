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
    shrink : bool
        Whether to shrink the scales to the output of the
        statistics instead of the raw data. Default is ``True``.
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

    def spaceout_and_resize_panels(self):
        """
        Adjust the space between the panels
        """
        # Only deal with the aspect ratio
        figure = self.figure
        aspect_ratio = self._aspect_ratio()

        if aspect_ratio is None:
            return

        left = figure.subplotpars.left
        right = figure.subplotpars.right
        top = figure.subplotpars.top
        bottom = figure.subplotpars.bottom
        W, H = figure.get_size_inches()

        w = (right - left) * W
        h = w * aspect_ratio
        H = h / (top - bottom)

        figure.set_figheight(H)

from __future__ import annotations

from mizani.utils import min_max

from ..doctools import document
from .contours import (
    contour_breaks,
    contour_lines,
    drop_duplicate_xy,
    estimate_grid_angle,
    rotate_xy,
    xyz_to_grid,
)
from .stat import stat


@document
class stat_contour(stat):
    """
    Contour lines for a gridded surface

    {usage}

    The `x` and `y` values must form a grid with one `z` value per
    coordinate. When `z` is missing, cells that touch it are not contoured.

    Parameters
    ----------
    {common_parameters}
    bins :
        Number of contour bands. Takes precedence over `binwidth`.
    binwidth :
        Distance between adjacent contour values.
    breaks :
        Explicit contour values, or a function that receives the `z` range
        and distance between contours. Explicit values override `bins` and
        `binwidth`. A function uses the distance selected by `bins` or
        `binwidth`. By default, values are selected for ten bands.

    See Also
    --------
    plotnine.geom_contour : The default `geom` for this `stat`.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "level"   # height of the contour
    "nlevel"  # height of the contour, scaled to a maximum of 1
    "piece"   # numeric id of a contour in a given group
    ```
    """
    REQUIRED_AES = {"x", "y", "z"}
    DEFAULT_PARAMS = {
        "geom": "contour",
        "bins": None,
        "binwidth": None,
        "breaks": None,
    }
    CREATES = {"level", "nlevel", "piece"}
    DROPPED_AES = ["z", "weight"]

    def setup_params(self, data):
        # Use one surface range for the full layer so facet panels share
        # comparable contour heights.
        self.params["z_range"] = min_max(data["z"], na_rm=True, finite=True)

    def setup_data(self, data):
        return drop_duplicate_xy(data)

    def compute_group(self, data, scales):
        params = self.params
        breaks = contour_breaks(
            params["z_range"],
            params["bins"],
            params["binwidth"],
            params["breaks"],
        )

        # Align a rotated grid with the axes before arranging `z` into rows
        # and columns. Restore the original orientation afterwards.
        angle = estimate_grid_angle(data["x"], data["y"])
        x, y = rotate_xy(data["x"], data["y"], -angle)
        data = data.assign(x=x, y=y)

        res = self.compute_contours(
            *xyz_to_grid(data), breaks, data["group"].iloc[0]
        )
        if len(res):
            res["x"], res["y"] = rotate_xy(res["x"], res["y"], angle)
        return res

    def compute_contours(self, x, y, Z, breaks, group):
        """
        Trace one contour line at every break on an axis-aligned grid
        """
        return contour_lines(x, y, Z, breaks, group)

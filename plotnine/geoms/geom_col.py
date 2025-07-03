from ..doctools import document
from .geom_bar import geom_bar


@document
class geom_col(geom_bar):
    """
    Bar plot with base on the x-axis

    {usage}

    This is an alternate version of [](`~plotnine.geoms.geom_bar`) that maps
    the height of bars to an existing variable in your data. If
    you want the height of the bar to represent a count of cases,
    use [](`~plotnine.geoms.geom_bar`).

    Parameters
    ----------
    {common_parameters}
    just : float, default=0.5
        How to align the column with respect to the axis breaks. The default
        `0.5` aligns the center of the column with the break. `0` aligns the
        left of the of the column with the break and `1` aligns the right of
        the column with the break.
    width : float, default=None
        Bar width. If `None`{.py}, the width is set to
        `90%` of the resolution of the data.

    See Also
    --------
    plotnine.geom_bar
    """

    REQUIRED_AES = {"x", "y"}
    NON_MISSING_AES = {"xmin", "xmax", "ymin", "ymax"}
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "stack",
        "na_rm": False,
        "just": 0.5,
        "width": None,
    }

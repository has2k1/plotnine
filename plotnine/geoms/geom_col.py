from ..doctools import document
from .geom_bar import geom_bar


@document
class geom_col(geom_bar):
    """
    Bar plot with base on the x-axis

    This is an alternate version of [](`~plotnine.geoms.geom_bar`) that maps
    the height of bars to an existing variable in your data. If
    you want the height of the bar to represent a count of cases,
    use [](`~plotnine.geoms.geom_bar`).

    {usage}

    Parameters
    ----------
    {common_parameters}
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
        "width": None,
    }

from ..doctools import document
from .geom_path import geom_path


@document
class geom_density_2d(geom_path):
    """
    2D density estimate

    {usage}

    This is a 2d version of [](`~plotnine.geoms.geom_density`).

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.stat_density_2d : The default `stat` for this `geom`.
    """

    DEFAULT_PARAMS = {
        "stat": "density_2d",
        "position": "identity",
        "na_rm": False,
    }

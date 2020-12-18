from ..doctools import document
from .geom_point import geom_point


@document
class geom_pointdensity(geom_point):
    """
    2D density estimate

    This is a 2d version of :class:`~plotnine.geoms.geom_density`.

    {usage}

    Parameters
    ----------
    {common_parameters}
    """
    DEFAULT_PARAMS = {'stat': 'pointdensity', 'position': 'identity',
                      'na_rm': False}

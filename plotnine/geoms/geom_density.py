from ..doctools import document
from .geom_area import geom_area


@document
class geom_density(geom_area):
    """
    Smooth density estimate

    {usage}

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.geoms.geom_ribbon
    """
    DEFAULT_AES = dict(
        geom_area.DEFAULT_AES, **{
            'color': 'black',
            'fill': None,
            'weight': 1
        }
    )

    DEFAULT_PARAMS = dict(
        geom_area.DEFAULT_PARAMS, **{
            'stat': 'density',
            'position': 'identity'
        }
    )

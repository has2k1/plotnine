from ..doctools import document
from .geom_ribbon import geom_ribbon


@document
class geom_area(geom_ribbon):
    """
    Area plot

    An area plot is a special case of geom_ribbon,
    where the minimum of the range is fixed to 0,
    and the position adjustment defaults to 'stack'.

    {usage}

    Parameters
    ----------
    {common_parameters}

    See Also
    --------
    plotnine.geoms.geom_ribbon
    """
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'stack',
                      'na_rm': False}

    def setup_data(self, data):
        data['ymin'] = 0
        data['ymax'] = data['y']
        return data

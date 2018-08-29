from ..doctools import document
from .geom import geom


@document
class geom_blank(geom):
    """
    An empty plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    """
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False}

    def draw_panel(self, data, panel_params, coord, ax, **params):
        pass

    def handle_na(self, data):
        return data

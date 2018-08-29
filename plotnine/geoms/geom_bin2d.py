from ..doctools import document
from .geom_rect import geom_rect


@document
class geom_bin2d(geom_rect):
    """
    Heatmap of 2d bin counts


    Divides the plane into rectangles, counts the number of
    cases in each rectangle, and then (by default) maps the number
    of cases to the rectangle's fill. This is a useful alternative
    to geom_point in the presence of overplotting.

    {usage}

    Parameters
    ----------
    {common_parameters}
    """
    DEFAULT_PARAMS = {'stat': 'bin_2d', 'position': 'identity',
                      'na_rm': False}

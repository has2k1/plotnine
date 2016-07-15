from __future__ import absolute_import, division, print_function

from .geom_point import geom_point


class geom_qq(geom_point):
    """
    Quantile-Quantile plot
    """
    DEFAULT_PARAMS = {'stat': 'qq', 'position': 'identity'}

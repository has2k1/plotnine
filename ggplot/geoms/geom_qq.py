from __future__ import absolute_import, division, print_function

from ..utils.doctools import document
from .geom_point import geom_point


@document
class geom_qq(geom_point):
    """
    Quantile-Quantile plot

    {documentation}
    """
    DEFAULT_PARAMS = {'stat': 'qq', 'position': 'identity'}

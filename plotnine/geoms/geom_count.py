from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..doctools import document
from .geom_point import geom_point


@document
class geom_count(geom_point):
    """
    Plot overlapping points

    This is a variant :class:`geom_point` that counts the number
    of observations at each location, then maps the count to point
    area. It useful when you have discrete data and overplotting.

    {usage}

    Parameters
    ----------
    {common_parameters}

    {aesthetics}
    """
    DEFAULT_PARAMS = {'stat': 'sum', 'position': 'identity',
                      'na_rm': False}

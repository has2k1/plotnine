from __future__ import (absolute_import, division, print_function)

from ..utils.doctools import document
from .geom_path import geom_path


_params = geom_path.DEFAULT_PARAMS.copy()
_params['stat'] = 'bin'


@document
class geom_freqpoly(geom_path):
    """
    Frequency polygon

    {usage}

    Parameters
    ----------
    {common_parameters}

    {aesthetics}
    """
    DEFAULT_PARAMS = _params

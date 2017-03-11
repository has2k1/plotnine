from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..doctools import document
from .geom_bar import geom_bar


@document
class geom_histogram(geom_bar):
    """
    Histogram

    {usage}

    Parameters
    ----------
    {common_parameters}

    {aesthetics}

    See Also
    --------
    :class:`~plotnine.geoms.geom_bar`
    """
    DEFAULT_PARAMS = {'stat': 'bin', 'position': 'stack',
                      'na_rm': False}

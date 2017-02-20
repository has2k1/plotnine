from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils.doctools import document
from .geom_path import geom_path


@document
class geom_line(geom_path):
    """
    Connected points

    {usage}

    Parameters
    ----------
    {common_parameters}

    {aesthetics}
    """

    def setup_data(self, data):
        return data.sort_values(['PANEL', 'group', 'x'])

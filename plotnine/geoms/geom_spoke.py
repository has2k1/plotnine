from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from ..doctools import document
from .geom_segment import geom_segment


@document
class geom_spoke(geom_segment):
    """
    Line segment parameterised by location, direction and distance

    {usage}

    Parameters
    ----------
    {common_parameters}

    {aesthetics}

    See Also
    --------
    :class:`~plotnine.geoms.geom_segment` for documentation of extra
    parameters.
    """
    REQUIRED_AES = {'x', 'y', 'angle', 'radius'}

    def setup_data(self, data):
        try:
            radius = data['radius']
        except KeyError:
            radius = self.aes_params['radius']

        data['xend'] = data['x'] + np.cos(data['angle']) * radius
        data['yend'] = data['y'] + np.sin(data['angle']) * radius
        return data

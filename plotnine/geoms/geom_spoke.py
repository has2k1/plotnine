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

    See Also
    --------
    plotnine.geoms.geom_segment : For documentation of extra
        parameters.
    """
    REQUIRED_AES = {'x', 'y', 'angle', 'radius'}

    def setup_data(self, data):
        try:
            radius = data['radius']
        except KeyError:
            radius = self.aes_params['radius']
        try:
            angle = data['angle']
        except KeyError:
            angle = self.aes_params['angle']

        data['xend'] = data['x'] + np.cos(angle) * radius
        data['yend'] = data['y'] + np.sin(angle) * radius
        return data

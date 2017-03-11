from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import resolution
from ..doctools import document
from .geom_rect import geom_rect


@document
class geom_bar(geom_rect):
    """
    Bar plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    width : float, optional (default None)
        Bar width. If :py:`None`, the width is set to
        `90%` of the resolution of the data.

    {aesthetics}

    See Also
    --------
    :class:`~plotnine.geoms.geom_histogram`
    """
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'count', 'position': 'stack',
                      'na_rm': False, 'width': None}

    def setup_data(self, data):
        if 'width' not in data:
            if self.params['width']:
                data['width'] = self.params['width']
            else:
                data['width'] = resolution(data['x'], False) * 0.9

        bool_idx = (data['y'] < 0)

        data['ymin'] = 0
        data.loc[bool_idx, 'ymin'] = data.loc[bool_idx, 'y']

        data['ymax'] = data['y']
        data.loc[bool_idx, 'ymax'] = 0

        data['xmin'] = data['x'] - data['width'] / 2
        data['xmax'] = data['x'] + data['width'] / 2
        del data['width']
        return data

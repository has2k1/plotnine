from warnings import warn

import pandas as pd

from ..utils import make_iterable, order_as_mapping_data
from ..exceptions import PlotnineWarning
from ..doctools import document
from ..aes import aes
from .geom import geom
from .geom_segment import geom_segment


@document
class geom_hline(geom):
    """
    Horizontal line

    {usage}

    Parameters
    ----------
    {common_parameters}
    """
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 0.5, 'alpha': 1}
    REQUIRED_AES = {'yintercept'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False, 'inherit_aes': False}
    legend_geom = 'path'

    def __init__(self, mapping=None, data=None, **kwargs):
        mapping, data = order_as_mapping_data(mapping, data)
        yintercept = kwargs.pop('yintercept', None)
        if yintercept is not None:
            if mapping:
                warn("The 'yintercept' parameter has overridden "
                     "the aes() mapping.", PlotnineWarning)
            data = pd.DataFrame({'yintercept': make_iterable(yintercept)})
            mapping = aes(yintercept='yintercept')
            kwargs['show_legend'] = False

        geom.__init__(self, mapping, data, **kwargs)

    def draw_panel(self, data, panel_params, coord, ax, **params):
        """
        Plot all groups
        """
        ranges = coord.backtransform_range(panel_params)
        data['y'] = data['yintercept']
        data['yend'] = data['yintercept']
        data['x'] = ranges.x[0]
        data['xend'] = ranges.x[1]
        data = data.drop_duplicates()

        for _, gdata in data.groupby('group'):
            gdata.reset_index(inplace=True)
            geom_segment.draw_group(gdata, panel_params,
                                    coord, ax, **params)

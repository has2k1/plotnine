from warnings import warn

import pandas as pd

from ..mapping import aes
from ..exceptions import PlotnineWarning
from ..utils import make_iterable, order_as_data_mapping
from ..doctools import document
from .geom import geom
from .geom_segment import geom_segment


@document
class geom_abline(geom):
    """
    Lines specified by slope and intercept

    {usage}

    Parameters
    ----------
    {common_parameters}
    """
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'alpha': 1, 'size': 0.5}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False, 'inherit_aes': False}
    REQUIRED_AES = {'slope', 'intercept'}
    legend_geom = 'path'

    def __init__(self, mapping=None, data=None, **kwargs):
        data, mapping = order_as_data_mapping(data, mapping)
        slope = kwargs.pop('slope', None)
        intercept = kwargs.pop('intercept', None)

        # If nothing is set, it defaults to y=x
        if mapping is None and slope is None and intercept is None:
            slope = 1
            intercept = 0

        if slope is not None or intercept is not None:
            if mapping:
                warn("The 'intercept' and 'slope' when specified override "
                     "the aes() mapping.", PlotnineWarning)
            if data is not None and len(data):
                warn("The 'intercept' and 'slope' when specified override "
                     "the data", PlotnineWarning)

            if slope is None:
                slope = 1
            if intercept is None:
                intercept = 0

            data = pd.DataFrame({
                'intercept': make_iterable(intercept),
                'slope': slope
            })

            mapping = aes(intercept=intercept, slope=slope)
            kwargs['show_legend'] = False

        geom.__init__(self, mapping, data, **kwargs)

    def draw_panel(self, data, panel_params, coord, ax, **params):
        """
        Plot all groups
        """
        ranges = coord.backtransform_range(panel_params)
        data['x'] = ranges.x[0]
        data['xend'] = ranges.x[1]
        data['y'] = ranges.x[0] * data['slope'] + data['intercept']
        data['yend'] = ranges.x[1] * data['slope'] + data['intercept']
        data = data.drop_duplicates()

        for _, gdata in data.groupby('group'):
            gdata.reset_index(inplace=True)
            geom_segment.draw_group(gdata, panel_params,
                                    coord, ax, **params)

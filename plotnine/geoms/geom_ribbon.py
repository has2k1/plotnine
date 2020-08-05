from ..coords import coord_flip
from ..utils import to_rgba, SIZE_FACTOR
from ..doctools import document
from ..exceptions import PlotnineError
from .geom import geom


@document
class geom_ribbon(geom):
    """
    Ribbon plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    """
    DEFAULT_AES = {'alpha': 1, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 0.5}
    REQUIRED_AES = {'x', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False}
    legend_geom = 'polygon'

    def handle_na(self, data):
        return data

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        data = coord.transform(data, panel_params, munch=True)
        data = data.sort_values(by=['group', 'x'], kind='mergesort')
        units = ['alpha', 'color', 'fill', 'linetype', 'size']

        if len(data[units].drop_duplicates()) > 1:
            msg = "Aesthetics cannot vary within a ribbon."
            raise PlotnineError(msg)

        for _, udata in data.groupby(units, dropna=False):
            udata.reset_index(inplace=True, drop=True)
            geom_ribbon.draw_unit(udata, panel_params, coord,
                                  ax, **params)

    @staticmethod
    def draw_unit(data, panel_params, coord, ax, **params):
        data['size'] *= SIZE_FACTOR
        fill = to_rgba(data['fill'], data['alpha'])
        color = data['color']

        if fill is None:
            fill = 'none'

        if all(color.isnull()):
            color = 'none'

        if isinstance(coord, coord_flip):
            fill_between = ax.fill_betweenx
            _x, _min, _max = data['y'], data['xmin'], data['xmax']
        else:
            fill_between = ax.fill_between
            _x, _min, _max = data['x'], data['ymin'], data['ymax']

        fill_between(_x, _min, _max,
                     facecolor=fill,
                     edgecolor=color,
                     linewidth=data['size'].iloc[0],
                     linestyle=data['linetype'].iloc[0],
                     zorder=params['zorder'])

from matplotlib.patches import Rectangle

from ..doctools import document
from .geom import geom
from .geom_ribbon import geom_ribbon
from .geom_line import geom_line
from .geom_line import geom_path


@document
class geom_smooth(geom):
    """
    A smoothed conditional mean

    {usage}

    Parameters
    ----------
    {common_parameters}
    legend_fill_ratio : float (default: 0.5)
        How much (vertically) of the legend box should be filled by
        the color that indicates the confidence intervals. Should be
        in the range [0, 1].
    """
    DEFAULT_AES = {'alpha': 0.4, 'color': 'black', 'fill': '#999999',
                   'linetype': 'solid', 'size': 1,
                   'ymin': None, 'ymax': None}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'smooth', 'position': 'identity',
                      'na_rm': False, 'legend_fill_ratio': 0.5}

    def setup_data(self, data):
        return data.sort_values(['PANEL', 'group', 'x'])

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        _loc = data.columns.get_loc
        has_ribbon = (data.iloc[0, _loc('ymin')] is not None and
                      data.iloc[0, _loc('ymax')] is not None)
        if has_ribbon:
            data2 = data.copy()
            data2['color'] = None
            geom_ribbon.draw_group(data2, panel_params,
                                   coord, ax, **params)

        data['alpha'] = 1
        geom_line.draw_group(data, panel_params, coord, ax, **params)

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw letter 'a' in the box

        Parameters
        ----------
        data : dataframe
        params : dict
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        try:
            has_se = lyr.stat.params['se']
        except KeyError:
            has_se = False

        if has_se:
            r = lyr.geom.params['legend_fill_ratio']
            bg = Rectangle((0, (1-r)*da.height/2),
                           width=da.width,
                           height=r*da.height,
                           alpha=data['alpha'],
                           facecolor=data['fill'],
                           linewidth=0)
            da.add_artist(bg)

        data['alpha'] = 1
        return geom_path.draw_legend(data, da, lyr)

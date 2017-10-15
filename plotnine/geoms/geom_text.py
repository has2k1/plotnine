from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.text import Text

from ..utils import to_rgba, suppress
from ..doctools import document
from ..positions import position_nudge
from .geom import geom


# Note: hjust & vjust are parameters instead of aesthetics
# due to a limitation imposed by MPL
# see: https://github.com/matplotlib/matplotlib/pull/1181
@document
class geom_text(geom):
    """
    Textual annotations

    {usage}

    Parameters
    ----------
    {common_parameters}
    parse : bool (default: False)
        If :py:`True`, the labels will be rendered with
        `latex <http://matplotlib.org/users/usetex.html>`_.
    family : str (default: None)
        Font family.
    fontweight : int or str (default: normal)
        Font weight.
    fontstyle : str (default: normal)
        Font style. One of *normal*, *italic* or *oblique*
    ha : str (default: center)
        Horizontal alignment. One of *left*, *center* or *right.*
    va : str (default: center)
        Vertical alignment. One of *top*, *center* or *bottom.*
    nudge_x : float (default: 0)
        Horizontal adjustment to apply to the text
    nudge_y : float (default: 0)
        Vertical adjustment to apply to the text
    format_string : str (default: None)
        If not :py:`None`, then the text if formatted with this
        string using :meth:`str.format`

    {aesthetics}

    See Also
    --------
    :class:`matplotlib.text.Text`

    """
    DEFAULT_AES = {'alpha': 1, 'angle': 0, 'color': 'black',
                   'size': 11, 'lineheight': 1.2}
    REQUIRED_AES = {'label', 'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False, 'parse': False,
                      'family': None, 'fontweight': 'normal',
                      'fontstyle': 'normal', 'ha': 'center',
                      'va': 'center', 'nudge_x': 0, 'nudge_y': 0,
                      'format_string': None}

    def __init__(self, *args, **kwargs):
        nudge_kwargs = {}
        with suppress(KeyError):
            nudge_kwargs['x'] = kwargs['nudge_x']
        with suppress(KeyError):
            nudge_kwargs['y'] = kwargs['nudge_y']
        if nudge_kwargs:
            kwargs['position'] = position_nudge(**nudge_kwargs)

        # Accomodate for the old names
        if 'hjust' in kwargs:
            kwargs['ha'] = kwargs['hjust']

        if 'vjust' in kwargs:
            kwargs['va'] = kwargs['vjust']

        geom.__init__(self, *args, **kwargs)

    def setup_data(self, data):
        parse = self.params['parse']
        fmt = self.params['format_string']

        # format
        if fmt:
            data['label'] = [fmt.format(l) for l in data['label']]

        # Parse latex
        if parse:
            data['label'] = ['${}$'.format(l) for l in data['label']]

        return data

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        data = coord.transform(data, panel_params)

        # Bind color and alpha
        color = to_rgba(data['color'], data['alpha'])

        # Create a dataframe for the plotting data required
        # by ax.text
        df = data[['x', 'y', 'size']].copy()
        df['s'] = data['label']
        df['rotation'] = data['angle']
        df['linespacing'] = data['lineheight']
        df['color'] = color
        df['ha'] = params['ha']
        df['va'] = params['va']
        df['family'] = params['family']
        df['fontweight'] = params['fontweight']
        df['fontstyle'] = params['fontstyle']
        df['zorder'] = params['zorder']
        df['clip_on'] = True

        # 'boxstyle' indicates geom_label so we need an MPL bbox
        draw_label = 'boxstyle' in params
        if draw_label:
            fill = to_rgba(data.pop('fill'), data['alpha'])
            if isinstance(fill, tuple):
                fill = [list(fill)] * len(data['x'])
            df['facecolor'] = fill

            if params['boxstyle'] in ('round', 'round4'):
                boxstyle = '{},pad={},rounding_size={}'.format(
                    params['boxstyle'],
                    params['label_padding'],
                    params['label_r'])
            elif params['boxstyle'] in ('roundtooth', 'sawtooth'):
                boxstyle = '{},pad={},tooth_size={}'.format(
                    params['boxstyle'],
                    params['label_padding'],
                    params['tooth_size'])
            else:
                boxstyle = '{},pad={}'.format(
                    params['boxstyle'],
                    params['label_padding'])
            bbox = {'linewidth': params['label_size'],
                    'boxstyle': boxstyle}
        else:
            bbox = {}

        # For labels add a bbox
        for i in range(len(data)):
            kw = df.iloc[i].to_dict()
            if draw_label:
                kw['bbox'] = bbox
                kw['bbox']['edgecolor'] = kw['color']
                kw['bbox']['facecolor'] = kw.pop('facecolor')
            ax.text(**kw)

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw letter 'a' in the box

        Parameters
        ----------
        data : dataframe
        da : DrawingArea
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        key = Text(x=0.5*da.width,
                   y=0.5*da.height,
                   text='a',
                   alpha=data['alpha'],
                   size=data['size'],
                   family=lyr.geom.params['family'],
                   color=data['color'],
                   rotation=data['angle'],
                   horizontalalignment='center',
                   verticalalignment='center')
        da.add_artist(key)
        return da

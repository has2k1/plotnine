from __future__ import annotations

import typing
from warnings import warn

import matplotlib.lines as mlines
import pandas as pd

from ..doctools import document
from ..exceptions import PlotnineWarning
from ..mapping import aes
from ..utils import SIZE_FACTOR, make_iterable, order_as_data_mapping
from .geom import geom
from .geom_segment import geom_segment

if typing.TYPE_CHECKING:
    from typing import Any

    import matplotlib as mpl

    import plotnine as p9

    from ..typing import DataLike


@document
class geom_vline(geom):
    """
    Vertical line

    {usage}

    Parameters
    ----------
    {common_parameters}
    """
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 0.5, 'alpha': 1}
    REQUIRED_AES = {'xintercept'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False, 'inherit_aes': False}

    def __init__(
        self,
        mapping: aes | None = None,
        data: DataLike | None = None,
        **kwargs: Any
    ) -> None:
        data, mapping = order_as_data_mapping(data, mapping)
        xintercept = kwargs.pop('xintercept', None)
        if xintercept is not None:
            if mapping:
                warn("The 'xintercept' parameter has overridden "
                     "the aes() mapping.", PlotnineWarning)
            data = pd.DataFrame({'xintercept': make_iterable(xintercept)})
            mapping = aes(xintercept='xintercept')
            kwargs['show_legend'] = False

        geom.__init__(self, mapping, data, **kwargs)

    def draw_panel(
        self,
        data: pd.DataFrame,
        panel_params: p9.iapi.panel_view,
        coord: p9.coords.coord.coord,
        ax: mpl.axes.Axes,
        **params: Any
    ) -> None:
        """
        Plot all groups
        """
        ranges = coord.backtransform_range(panel_params)
        data['x'] = data['xintercept']
        data['xend'] = data['xintercept']
        data['y'] = ranges.y[0]
        data['yend'] = ranges.y[1]
        data = data.drop_duplicates()

        for _, gdata in data.groupby('group'):
            gdata.reset_index(inplace=True)
            geom_segment.draw_group(gdata, panel_params,
                                    coord, ax, **params)

    @staticmethod
    def draw_legend(
        data: pd.Series[Any],
        da: mpl.patches.DrawingArea,
        lyr: p9.layer.layer
    ) -> mpl.patches.DrawingArea:
        """
        Draw a vertical line in the box

        Parameters
        ----------
        data : Series
            Data Row
        da : DrawingArea
            Canvas
        lyr : layer
            Layer

        Returns
        -------
        out : DrawingArea
        """
        x = [0.5 * da.width] * 2
        y = [0, da.height]
        data['size'] *= SIZE_FACTOR
        key = mlines.Line2D(
            x,
            y,
            alpha=data['alpha'],
            linestyle=data['linetype'],
            linewidth=data['size'],
            color=data['color'],
            solid_capstyle='butt',
            antialiased=False
        )
        da.add_artist(key)
        return da

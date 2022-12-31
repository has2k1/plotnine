from __future__ import annotations

import typing
from warnings import warn

import pandas as pd

from ..doctools import document
from ..exceptions import PlotnineWarning
from ..mapping import aes
from ..utils import make_iterable, order_as_data_mapping
from .geom import geom
from .geom_path import geom_path
from .geom_segment import geom_segment

if typing.TYPE_CHECKING:
    from typing import Any

    import matplotlib as mpl

    import plotnine as p9

    from ..typing import DataLike


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
    draw_legend = staticmethod(geom_path.draw_legend)  # type: ignore

    def __init__(
        self,
        mapping: aes | None = None,
        data: DataLike | None = None,
        **kwargs: Any
    ) -> None:
        data, mapping = order_as_data_mapping(data, mapping)
        yintercept = kwargs.pop('yintercept', None)
        if yintercept is not None:
            if mapping:
                warn("The 'yintercept' parameter has overridden "
                     "the aes() mapping.", PlotnineWarning)
            data = pd.DataFrame({'yintercept': make_iterable(yintercept)})
            mapping = aes(yintercept='yintercept')
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
        data['y'] = data['yintercept']
        data['yend'] = data['yintercept']
        data['x'] = ranges.x[0]
        data['xend'] = ranges.x[1]
        data = data.drop_duplicates()

        for _, gdata in data.groupby('group'):
            gdata.reset_index(inplace=True)
            geom_segment.draw_group(gdata, panel_params,
                                    coord, ax, **params)

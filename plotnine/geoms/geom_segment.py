import numpy as np
import pandas as pd
import matplotlib.collections as mcoll

from ..utils import to_rgba, make_line_segments, interleave
from ..utils import SIZE_FACTOR
from ..doctools import document
from .geom import geom


@document
class geom_segment(geom):
    """
    Line segments

    {usage}

    Parameters
    ----------
    {common_parameters}
    lineend : str (default: butt)
        Line end style, of of *butt*, *round* or *projecting.*
        This option is applied for solid linetypes.
    arrow : plotnine.geoms.geom_path.arrow (default: None)
        Arrow specification. Default is no arrow.

    See Also
    --------
    plotnine.geoms.geom_path.arrow : for adding arrowhead(s)
        to segments.
    """
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'linetype': 'solid',
                   'size': 0.5}
    REQUIRED_AES = {'x', 'y', 'xend', 'yend'}
    NON_MISSING_AES = {'linetype', 'size', 'shape'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False, 'lineend': 'butt', 'arrow': None}

    legend_geom = 'path'

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        data = coord.transform(data, panel_params)
        data['size'] *= SIZE_FACTOR
        color = to_rgba(data['color'], data['alpha'])

        # start point -> end point, sequence of xy points
        # from which line segments are created
        x = interleave(data['x'], data['xend'])
        y = interleave(data['y'], data['yend'])
        segments = make_line_segments(x, y, ispath=False)
        coll = mcoll.LineCollection(segments,
                                    edgecolor=color,
                                    linewidth=data['size'],
                                    linestyle=data['linetype'][0],
                                    zorder=params['zorder'])
        ax.add_collection(coll)

        if 'arrow' in params and params['arrow']:
            adata = pd.DataFrame(index=range(len(data)*2))
            idx = np.arange(1, len(data)+1)
            adata['group'] = np.hstack([idx, idx])
            adata['x'] = np.hstack([data['x'], data['xend']])
            adata['y'] = np.hstack([data['y'], data['yend']])
            other = ['color', 'alpha', 'size', 'linetype']
            for param in other:
                adata[param] = np.hstack([data[param], data[param]])

            params['arrow'].draw(
                adata, panel_params, coord, ax,
                params['zorder'], constant=False)

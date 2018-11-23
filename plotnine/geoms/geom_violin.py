import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from ..utils import groupby_apply, interleave, resolution
from ..doctools import document
from .geom_polygon import geom_polygon
from .geom_path import geom_path
from .geom import geom


@document
class geom_violin(geom):
    """
    Violin Plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    draw_quantiles: float or [float]
       draw horizontal lines at the given quantiles (0..1)
       of the density estimate.
    """
    DEFAULT_AES = {'alpha': 1, 'color': '#333333', 'fill': 'white',
                   'linetype': 'solid', 'size': 0.5, 'weight': 1}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'ydensity', 'position': 'dodge',
                      'draw_quantiles': None, 'scale': 'area',
                      'trim': True, 'width': None, 'na_rm': False}
    legend_geom = 'polygon'

    def __init__(self, *args, **kwargs):
        if 'draw_quantiles' in kwargs:
            kwargs['draw_quantiles'] = pd.Series(kwargs['draw_quantiles'],
                                                 dtype=float)
            if not kwargs['draw_quantiles'].between(0, 1,
                                                    inclusive=False).all():
                raise ValueError(
                    "draw_quantiles must be a float or"
                    " an iterable of floats (>0.0; < 1.0)")
        super().__init__(*args, **kwargs)

    def setup_data(self, data):
        if 'width' not in data:
            if self.params['width']:
                data['width'] = self.params['width']
            else:
                data['width'] = resolution(data['x'], False) * 0.9

        def func(df):
            df['ymin'] = df['y'].min()
            df['ymax'] = df['y'].max()
            df['xmin'] = df['x'] - df['width']/2
            df['xmax'] = df['x'] + df['width']/2
            return df

        # This is a plyr::ddply
        data = groupby_apply(data, 'group', func)
        return data

    def draw_panel(self, data, panel_params, coord, ax, **params):
        quantiles = params['draw_quantiles']

        for _, df in data.groupby('group'):
            # Find the points for the line to go all the way around
            df['xminv'] = (df['x'] - df['violinwidth'] *
                           (df['x'] - df['xmin']))
            df['xmaxv'] = (df['x'] + df['violinwidth'] *
                           (df['xmax'] - df['x']))

            # Make sure it's sorted properly to draw the outline
            # i.e violin = kde + mirror kde,
            # bottom to top then top to bottom
            n = len(df)
            polygon_df = pd.concat(
                [df.sort_values('y'), df.sort_values('y', ascending=False)],
                axis=0, ignore_index=True)

            _df = polygon_df.iloc
            _loc = polygon_df.columns.get_loc
            _df[:n, _loc('x')] = _df[:n, _loc('xminv')]
            _df[n:, _loc('x')] = _df[n:, _loc('xmaxv')]

            # Close the polygon: set first and last point the same
            polygon_df.loc[-1, :] = polygon_df.loc[0, :]

            # plot violin polygon
            geom_polygon.draw_group(polygon_df, panel_params,
                                    coord, ax, **params)

            if quantiles is not None:
                # Get dataframe with quantile segments and that
                # with aesthetics then put them together
                # Each quantile segment is defined by 2 points and
                # they all get similar aesthetics
                aes_df = df.drop(['x', 'y', 'group'], axis=1)
                aes_df.reset_index(inplace=True)
                idx = [0] * 2 * len(quantiles)
                aes_df = aes_df.iloc[idx, :].reset_index(drop=True)
                segment_df = pd.concat(
                    [make_quantile_df(df, quantiles), aes_df],
                    axis=1)

                # plot quantile segments
                geom_path.draw_group(segment_df, panel_params, coord,
                                     ax, **params)


def make_quantile_df(data, draw_quantiles):
    """
    Return a dataframe with info needed to draw quantile segments
    """
    dens = data['density'].cumsum() / data['density'].sum()
    ecdf = interp1d(dens, data['y'], assume_sorted=True)
    ys = ecdf(draw_quantiles)

    # Get the violin bounds for the requested quantiles
    violin_xminvs = interp1d(data['y'], data['xminv'])(ys)
    violin_xmaxvs = interp1d(data['y'], data['xmaxv'])(ys)

    data = pd.DataFrame({
        'x': interleave(violin_xminvs, violin_xmaxvs),
        'y': np.repeat(ys, 2),
        'group': np.repeat(np.arange(1, len(ys)+1), 2)})

    return data

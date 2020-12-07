from warnings import warn

import numpy as np
import matplotlib.image as mimage
from matplotlib.colors import to_rgba_array

from ..utils import resolution
from ..coords import coord_cartesian
from ..doctools import document
from ..exceptions import PlotnineError, PlotnineWarning
from .geom import geom


@document
class geom_raster(geom):
    """
    Rasterized Rectangles specified using center points

    {usage}

    Parameters
    ----------
    {common_parameters}

    hjust : float (default: 0.5)
        Horizontal justification for the rectangle at point ``x``.
        Default is 0.5, which centers the rectangle horizontally.
        Must be in the range ``[0, 1]``.
    vjust : float (default: 0.5)
        Vertical justification for the rectangle at point ``y``
        Default is 0.5, which centers the rectangle vertically.
        Must be in the range ``[0, 1]``.
    interpolation : str | None (default: None)
        How to calculate values between the center points of
        adjacent rectangles. The default is :py:`None` not to
        interpolate. Allowed values are:
        :py:`'none', 'antialiased', 'nearest', 'bilinear', 'bicubic',`
        :py:`'spline16', 'spline36', 'hanning', 'hamming', 'hermite',`
        :py:`'kaiser', 'quadric', 'catrom', 'gaussian', 'bessel',`
        :py:`'mitchell', 'sinc', 'lanczos', 'blackman'`

    filterrad : float, (default: 4.0)
        The filter radius for filters that have a radius parameter, i.e.
        when interpolation is one of: *'sinc', 'lanczos' or 'blackman'*.
        Must be a number greater than zero.

    See Also
    --------
    plotnine.geoms.geom_rect
    plotnine.geoms.geom_tile
    """
    DEFAULT_AES = {'alpha': 1, 'fill': '#333333'}
    REQUIRED_AES = {'x', 'y'}
    NON_MISSING_AES = {'fill', 'xmin', 'xmax', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False, 'vjust': 0.5, 'hjust': 0.5,
                      'interpolation': None, 'filterrad': 4.0,
                      'raster': True}
    legend_geom = 'polygon'

    def __init__(self, *args, **kwargs):
        # Silently accept:
        #    1. interpolate
        #    2. bool values for interpolation
        if 'interpolate' in kwargs:
            kwargs['interpolation'] = kwargs.pop('interpolate')
        if isinstance(kwargs.get('interpolation', None), bool):
            if kwargs['interpolation'] is True:
                kwargs['interpolation'] = 'bilinear'
            else:
                kwargs['interpolation'] = None

        super().__init__(*args, **kwargs)

    def setup_data(self, data):
        hjust = self.params['hjust']
        vjust = self.params['vjust']
        precision = np.sqrt(np.finfo(float).eps)

        x_diff = np.diff(np.sort(data['x'].unique()))
        if len(x_diff) == 0:
            w = 1
        elif np.any(np.abs(np.diff(x_diff)) > precision):
            warn(
                "Raster pixels are placed at uneven horizontal intervals "
                "and will be shifted. Consider using geom_tile() instead.",
                PlotnineWarning
            )
            w = x_diff.min()
        else:
            w = x_diff[0]

        y_diff = np.diff(np.sort(data['y'].unique()))
        if len(y_diff) == 0:
            h = 1
        elif np.any(np.abs(np.diff(y_diff)) > precision):
            warn(
                "Raster pixels are placed at uneven vertical intervals "
                "and will be shifted. Consider using geom_tile() instead.",
                PlotnineWarning
            )
            h = y_diff.min()
        else:
            h = y_diff[0]

        data['xmin'] = data['x'] - w * (1 - hjust)
        data['xmax'] = data['x'] + w * hjust
        data['ymin'] = data['y'] - h * (1 - vjust)
        data['ymax'] = data['y'] + h * vjust
        return data

    def draw_panel(self, data, panel_params, coord, ax, **params):
        """
        Plot all groups
        """
        if not isinstance(coord, coord_cartesian):
            raise PlotnineError(
                "geom_raster only works with cartesian coordinates"
            )

        data = coord.transform(data, panel_params)
        x = data['x'].to_numpy().astype(float)
        y = data['y'].to_numpy().astype(float)
        facecolor = to_rgba_array(data['fill'].to_numpy())
        facecolor[:, 3] = data['alpha'].to_numpy()

        # Convert vector of data to flat image,
        # figure out dimensions of raster on plot, and the colored
        # indices.
        x_pos = ((x - x.min()) / resolution(x, False)).astype(int)
        y_pos = ((y - y.min()) / resolution(y, False)).astype(int)
        nrow = y_pos.max() + 1
        ncol = x_pos.max() + 1
        yidx, xidx = nrow-y_pos-1, x_pos

        # Create and "color" the matrix.
        # Any gaps left whites (ones) colors pluse zero alpha values
        # allows makes it possible to have a "neutral" interpolation
        # into the gaps when intervals are uneven.
        X = np.ones((nrow, ncol, 4))
        X[:, :, 3] = 0
        X[yidx, xidx] = facecolor

        im = mimage.AxesImage(
            ax,
            data=X,
            interpolation=params['interpolation'],
            origin='upper',
            extent=(
                data['xmin'].min(),
                data['xmax'].max(),
                data['ymin'].min(),
                data['ymax'].max()
            ),
            rasterized=params['raster'],
            filterrad=params['filterrad'],
            zorder=params['zorder']
        )
        ax.add_image(im)

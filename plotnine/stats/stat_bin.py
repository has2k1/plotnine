from warnings import warn

import numpy as np

from ..doctools import document
from ..exceptions import PlotnineError, PlotnineWarning
from .binning import (breaks_from_bins, breaks_from_binwidth,
                      assign_bins, freedman_diaconis_bins)
from .stat import stat


@document
class stat_bin(stat):
    """
    Count cases in each interval

    {usage}

    Parameters
    ----------
    {common_parameters}
    binwidth : float, optional (default: None)
        The width of the bins. The default is to use bins bins that
        cover the range of the data. You should always override this
        value, exploring multiple widths to find the best to illustrate
        the stories in your data.
    bins : int, optional (default: None)
        Number of bins. Overridden by binwidth. If :py:`None`,
        a number is computed using the freedman-diaconis method.
    breaks : array-like, optional (default: None)
        Bin boundaries. This supercedes the ``binwidth``, ``bins``,
        ``center`` and ``boundary``.
    center : float, optional (default: None)
        The center of one of the bins. Note that if center is above
        or below the range of the data, things will be shifted by
        an appropriate number of widths. To center on integers, for
        example, use :py:`width=1` and :py:`center=0`, even if 0 i
        s outside the range of the data. At most one of center and
        boundary may be specified.
    boundary : float, optional (default: None)
        A boundary between two bins. As with center, things are
        shifted when boundary is outside the range of the data.
        For example, to center on integers, use :py:`width=1` and
        :py:`boundary=0.5`, even if 1 is outside the range of the
        data. At most one of center and boundary may be specified.
    closed : str, optional (default: right)
        Which edge of the bins is included, *left* or *right*.
    pad : bool, optional (default: False)
        If :py:`True`, adds empty bins at either side of x.
        This ensures that frequency polygons touch 0.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    .. rubric:: Options for computed aesthetics

    ::

         'count'    # number of points in bin
         'density'  # density of points in bin, scaled to integrate to 1
         'ncount'   # count, scaled to maximum of 1
         'ndensity' # density, scaled to maximum of 1

    """
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'histogram', 'position': 'stack',
                      'na_rm': False, 'binwidth': None, 'bins': None,
                      'breaks': None, 'center': None,
                      'boundary': None, 'closed': 'right',
                      'pad': False}
    DEFAULT_AES = {'y': 'stat(count)', 'weight': None}
    CREATES = {'width', 'count', 'density', 'ncount', 'ndensity'}

    def setup_params(self, data):
        params = self.params

        if 'y' in data or 'y' in params:
            msg = "stat_bin() must not be used with a y aesthetic."
            raise PlotnineError(msg)

        if params['closed'] not in ('right', 'left'):
            raise PlotnineError(
                "`closed` should either 'right' or 'left'")

        if (params['breaks'] is None and
                params['binwidth'] is None and
                params['bins'] is None):
            params = params.copy()
            params['bins'] = freedman_diaconis_bins(data['x'])
            msg = ("'stat_bin()' using 'bins = {}'. "
                   "Pick better value with 'binwidth'.")
            warn(msg.format(params['bins']), PlotnineWarning)

        return params

    @classmethod
    def compute_group(cls, data, scales, **params):
        if params['breaks'] is not None:
            breaks = np.asarray(params['breaks'])
            if hasattr(scales.x, 'transform'):
                breaks = scales.x.transform(breaks)
        elif params['binwidth'] is not None:
            breaks = breaks_from_binwidth(
                scales.x.dimension(), params['binwidth'],
                params['center'], params['boundary'])
        else:
            breaks = breaks_from_bins(
                scales.x.dimension(), params['bins'],
                params['center'], params['boundary'])

        new_data = assign_bins(
            data['x'], breaks, data.get('weight'),
            params['pad'], params['closed'])
        return new_data

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

from ..aes import has_groups
from ..doctools import document
from ..exceptions import PlotnineError
from ..utils import array_kind, jitter, resolution
from .binning import breaks_from_bins, breaks_from_binwidth
from .stat import stat
from .stat_density import compute_density


@document
class stat_sina(stat):
    """
    Compute Sina plot values

    {usage}

    Parameters
    ----------
    {common_parameters}
    binwidth : float
        The width of the bins. The default is to use bins that
        cover the range of the data. You should always override this
        value, exploring multiple widths to find the best to
        illustrate the stories in your data.
    bins : int (default: 50)
        Number of bins. Overridden by binwidth.
    method : 'density' or 'counts'
        Choose the method to spread the samples within the same bin
        along the x-axis. Available methods: "density", "counts"
        (can be abbreviated, e.g. "d"). See Details.
    maxwidth : float
        Control the maximum width the points can spread into.
        Values should be in the range (0, 1).
    adjust : float, optional (default: 1)
        Adjusts the bandwidth of the density kernel when
        ``method='density'`` (see density).
    bw : str or float, optional (default: 'nrd0')
        The bandwidth to use, If a float is given, it is the bandwidth.
        The :py:`str` choices are::

            'nrd0'
            'normal_reference'
            'scott'
            'silverman'

        ``nrd0`` is a port of ``stats::bw.nrd0`` in R; it is eqiuvalent
        to ``silverman`` when there is more than 1 value in a group.
    bin_limit : int (default: 1)
        If the samples within the same y-axis bin are more
        than `bin_limit`, the samples's X coordinates will be adjusted.
        This parameter is effective only when :py:`method='counts'`
    random_state : int or ~numpy.random.RandomState, optional
        Seed or Random number generator to use. If ``None``, then
        numpy global generator :class:`numpy.random` is used.
    scale : str (default: area)
        How to scale the sina groups. The options are::

            'area'   # Scale by the largest density/bin amoung the different
                     # sinas

            'count'  # areas are scaled proportionally to the number of points

            'width'  # Only scale according to the maxwidth parameter.

    See Also
    --------
    plotnine.geoms.geom_sina
    """

    _aesthetics_doc = """
    {aesthetics_table}

    .. rubric:: Options for computed aesthetics

    ::

         'quantile'  # quantile
         'group'     # group identifier

    Calculated aesthetics are accessed using the `stat` function.
    e.g. :py:`'stat(quantile)'`.
    """

    REQUIRED_AES = {'x', 'y'}
    DEFAULT_AES = {'xend': 'stat(scaled)'}
    DEFAULT_PARAMS = {'geom': 'sina', 'position': 'dodge',
                      'na_rm': False, 'binwidth': None, 'bins': None,
                      'method': 'density',
                      'bw': 'nrd0',
                      'maxwidth': None, 'adjust': 1, 'bin_limit': 1,
                      'random_state': None, 'scale': 'area'
                      }
    CREATES = {'scaled'}

    def setup_data(self, data):
        if (array_kind.continuous(data['x']) and
                not has_groups(data) and
                (data['x'] != data.loc['x', 0]).any()):
            raise TypeError("Continuous x aesthetic -- did you forget "
                            "aes(group=...)?")
        return data

    def setup_params(self, data):
        params = self.params.copy()
        random_state = params['random_state']

        if params['maxwidth'] is None:
            params['maxwidth'] = resolution(data['x'], False) * 0.9

        if params['binwidth'] is None and self.params['bins'] is None:
            params['bins'] = 50

        if random_state is None:
            params['random_state'] = np.random
        elif isinstance(random_state, int):
            params['random_state'] = np.random.RandomState(random_state)

        # Required by compute_density
        params['kernel'] = 'gau'  # It has to be a gaussian kernel
        params['cut'] = 0
        params['gridsize'] = None
        params['clip'] = (-np.inf, np.inf)
        params['n'] = 512
        return params

    @classmethod
    def compute_panel(cls, data, scales, **params):
        maxwidth = params['maxwidth']
        random_state = params['random_state']

        if params['binwidth'] is not None:
            params['bins'] = breaks_from_binwidth(
                np.array(scales.y.dimension()) + 1e-8,
                params['binwidth']
            )
        else:
            params['bins'] = breaks_from_bins(
                np.array(scales.y.dimension()) + 1e-8,
                params['bins']
            )

        data = super(cls, stat_sina).compute_panel(data, scales, **params)

        if not len(data):
            return data

        if params['scale'] == 'area':
            data['sinawidth'] = data['density']/data['density'].max()
        elif params['scale'] == 'count':
            data['sinawidth'] = (data['density'] /
                                 data['density'].max() *
                                 data['n']/data['n'].max())
        elif params['scale'] == 'width':
            data['sinawidth'] = data['scaled']
        else:
            msg = "Unknown scale value '{}'"
            raise PlotnineError(msg.format(params['scale']))

        data['xmin'] = data['x'] - maxwidth/2
        data['xmax'] = data['x'] + maxwidth/2
        data['x_diff'] = (random_state.uniform(-1, 1, len(data)) *
                          maxwidth *
                          data['sinawidth']/2
                          )
        data['width'] = maxwidth

        # jitter y values if the input is input is integer
        if (data['y'] == np.floor(data['y'])).all():
            data['y'] = jitter(data['y'], random_state=random_state)

        return data

    @classmethod
    def compute_group(cls, data, scales, **params):
        maxwidth = params['maxwidth']
        bins = params['bins']
        bin_limit = params['bin_limit']
        weight = None

        if len(data) == 0:
            return pd.DataFrame()

        elif len(data) < 3:
            data['density'] = 0
            data['scaled'] = 1
        elif params['method'] == 'density':
            # density kernel estimation
            range_y = data['y'].min(), data['y'].max()
            dens = compute_density(data['y'], weight, range_y, **params)
            densf = interp1d(dens['x'], dens['density'],
                             bounds_error=False, fill_value='extrapolate')
            data['density'] = densf(data['y'])
            data['scaled'] = data['density']/dens['density'].max()
        else:
            # bin based estimation
            bin_index = pd.cut(
                data['y'], bins, include_lowest=True, labels=False)
            data['density'] = (pd.Series(bin_index)
                               .groupby(bin_index)
                               .apply(len)[bin_index]
                               .values)
            data.loc[data['density'] <= bin_limit, 'density'] = 0
            data['scaled'] = data['density']/data['density'].max()

        # Compute width if x has multiple values
        if len(data['x'].unique()) > 1:
            width = np.ptp(data['x']) * maxwidth
        else:
            width = maxwidth

        data['width'] = width
        data['n'] = len(data)
        data['x'] = np.mean([data['x'].max(), data['x'].min()])

        return data

    def finish_layer(self, data, params):
        # Rescale x in case positions have been adjusted
        x_mod = (data['xmax'] - data['xmin']) / data['width']
        data['x'] = data['x'] + data['x_diff'] * x_mod
        return data

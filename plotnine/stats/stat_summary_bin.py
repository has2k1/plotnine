import numpy as np
import pandas as pd

from ..utils import groupby_apply
from ..doctools import document
from ..exceptions import PlotnineError
from ..scales.scale import scale_discrete
from .binning import fuzzybreaks
from .stat_summary import make_summary_fun
from .stat import stat


@document
class stat_summary_bin(stat):
    """
    Summarise y values at x intervals

    {usage}

    Parameters
    ----------
    {common_parameters}
    binwidth : float or tuple, optional (default: None)
        The width of the bins. The default is to use bins bins that
        cover the range of the data. You should always override this
        value, exploring multiple widths to find the best to illustrate
        the stories in your data.
    bins : int or tuple, optional (default: 30)
        Number of bins. Overridden by binwidth.
    breaks : array-like(s), optional (default: None)
        Bin boundaries. This supercedes the ``binwidth``, ``bins``
        and ``boundary`` arguments.
    boundary : float or tuple, optional (default: None)
        A boundary between two bins. As with center, things are
        shifted when boundary is outside the range of the data.
        For example, to center on integers, use :py:`width=1` and
        :py:`boundary=0.5`, even if 1 is outside the range of the
        data. At most one of center and boundary may be specified.
    fun_data : str or function, optional
        One of
        :py:`['mean_cl_boot', 'mean_cl_normal', 'mean_sdl', 'median_hilow']`
        or any function that takes a array and returns a dataframe
        with three rows indexed as ``y``, ``ymin`` and ``ymax``.
        Defaults to :py:`'mean_cl_boot'`.
    fun_y : function, optional (default: None)
        Any function that takes a array-like and returns a value
        fun_ymin : function (default:None)
        Any function that takes an array-like and returns a value
    fun_ymax : function, optional (default: None)
        Any function that takes an array-like and returns a value
    fun_args : dict, optional (default: None)
        Arguments to any of the functions. Provided the names of the
        arguments of the different functions are in not conflict, the
        arguments will be assigned to the right functions. If there is
        a conflict, create a wrapper function that resolves the
        ambiguity in the argument names.
    random_state : int or ~numpy.random.RandomState, optional
        Seed or Random number generator to use. If ``None``, then
        numpy global generator :class:`numpy.random` is used.

    Notes
    -----
    The *binwidth*, *bins*, *breaks* and *bounary* arguments can be a
    tuples with two values (``(xaxis-value, yaxis-value)``) of the
    required type.

    See Also
    --------
    plotnine.geoms.geom_pointrange
    """

    _aesthetics_doc = """
    {aesthetics_table}

    .. rubric:: Options for computed aesthetics

    ::

        'bin'    # bin identifier
        'width'  # bin width
        'ymin'   # ymin computed by the summary function
        'ymax'   # ymax computed by the summary function

    Calculated aesthetics are accessed using the `stat` function.
    e.g. :py:`'stat(ymin)'`.
    """

    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'pointrange', 'position': 'identity',
                      'na_rm': False,
                      'bins': 30, 'breaks': None, 'binwidth': None,
                      'boundary': None, 'fun_data': None, 'fun_y': None,
                      'fun_ymin': None, 'fun_ymax': None,
                      'fun_args': None, 'random_state': None}
    CREATES = {'bin', 'width', 'ymin', 'ymax'}

    def setup_params(self, data):
        keys = ('fun_data', 'fun_y', 'fun_ymin', 'fun_ymax')
        if not any(self.params[k] for k in keys):
            raise PlotnineError('No summary function')

        if self.params['fun_args'] is None:
            self.params['fun_args'] = {}

        if 'random_state' not in self.params['fun_args']:
            if self.params['random_state']:
                random_state = self.params['random_state']
                if random_state is None:
                    random_state = np.random
                elif isinstance(random_state, int):
                    random_state = np.random.RandomState(random_state)

                self.params['fun_args']['random_state'] = random_state

        return self.params

    @classmethod
    def compute_group(cls, data, scales, **params):
        bins = params['bins']
        breaks = params['breaks']
        binwidth = params['binwidth']
        boundary = params['boundary']

        func = make_summary_fun(params['fun_data'], params['fun_y'],
                                params['fun_ymin'], params['fun_ymax'],
                                params['fun_args'])

        breaks = fuzzybreaks(scales.x, breaks, boundary, binwidth, bins)
        data['bin'] = pd.cut(data['x'], bins=breaks, labels=False,
                             include_lowest=True)

        def func_wrapper(data):
            """
            Add `bin` column to each summary result.
            """
            result = func(data)
            result['bin'] = data['bin'].iloc[0]
            return result

        # This is a plyr::ddply
        out = groupby_apply(data, 'bin', func_wrapper)
        centers = (breaks[:-1] + breaks[1:]) * 0.5
        bin_centers = centers[out['bin'].values]
        out['x'] = bin_centers
        out['bin'] += 1
        if isinstance(scales.x, scale_discrete):
            out['width'] = 0.9
        else:
            out['width'] = np.diff(breaks)[bins-1]

        return out

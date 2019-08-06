from ..doctools import document
from ..exceptions import PlotnineError
from ..positions import position_jitter
from .geom_point import geom_point


@document
class geom_jitter(geom_point):
    """
    Scatter plot with points jittered to reduce overplotting

    {usage}

    Parameters
    ----------
    {common_parameters}
    width : float, optional
        Proportion to jitter in horizontal direction.
        The default value is that from
        :class:`~plotnine.positions.position_jitter`
    height : float, optional
        Proportion to jitter in vertical direction.
        The default value is that from
        :class:`~plotnine.positions.position_jitter`.
    random_state : int or ~numpy.random.RandomState, optional
        Seed or Random number generator to use. If ``None``, then
        numpy global generator :class:`numpy.random` is used.

    See Also
    --------
    plotnine.positions.position_jitter
    plotnine.geoms.geom_point
    """
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'jitter',
                      'na_rm': False, 'width': None, 'height': None,
                      'random_state': None}

    def __init__(self, mapping=None, data=None, **kwargs):
        if {'width', 'height', 'random_state'} & set(kwargs):
            if 'position' in kwargs:
                raise PlotnineError(
                    "Specify either 'position' or "
                    "'width'/'height'/'random_state'")

            try:
                width = kwargs.pop('width')
            except KeyError:
                width = None

            try:
                height = kwargs.pop('height')
            except KeyError:
                height = None

            try:
                random_state = kwargs.pop('random_state')
            except KeyError:
                random_state = None

            kwargs['position'] = position_jitter(
                width=width, height=height, random_state=random_state)
        geom_point.__init__(self, mapping, data, **kwargs)

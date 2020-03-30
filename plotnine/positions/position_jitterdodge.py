from contextlib import suppress
from copy import copy

from ..aes import scaled_aesthetics
from ..utils import jitter, resolution
from ..exceptions import PlotnineError
from .position import position
from .position_dodge import position_dodge


# Adjust position by simultaneously dodging and jittering
class position_jitterdodge(position):
    """
    Dodge and jitter to minimise overlap

    Useful when aligning points generated through
    :class:`~plotnine.geoms.geom_point` with dodged a
    :class:`~plotnine.geoms.geom_boxplot`.

    Parameters
    ----------
    jitter_width : float
        Proportion to jitter in horizontal direction.
        Default is ``0.4`` of the resolution of the data.
    jitter_height : float
        Proportion to jitter in vertical direction.
        Default is ``0.0`` of the resolution of the data.
    dodge_width : float
        Amount to dodge in horizontal direction.
        Default is ``0.75``
    random_state : int or ~numpy.random.RandomState, optional
        Seed or Random number generator to use. If ``None``, then
        numpy global generator :class:`numpy.random` is used.
    """
    REQUIRED_AES = ['x', 'y']
    strategy = staticmethod(position_dodge.strategy)

    def __init__(self, jitter_width=None, jitter_height=0,
                 dodge_width=0.75, random_state=None):
        self.params = {'jitter_width': jitter_width,
                       'jitter_height': jitter_height,
                       'dodge_width': dodge_width,
                       'random_state': random_state}

    def setup_params(self, data):
        params = copy(self.params)
        width = params['jitter_width']
        if width is None:
            width = resolution(data['x']) * .4

        # Adjust the x transformation based on the number
        # of dodge variables
        dvars = scaled_aesthetics - {'x', 'y'}
        dodge_columns = data.columns.intersection(dvars)
        if len(dodge_columns) == 0:
            raise PlotnineError(
                "'position_jitterdodge' requires at least one "
                "aesthetic to dodge by.")

        s = set()
        for col in dodge_columns:
            with suppress(AttributeError):
                s.update(data[col].cat.categories)
        ndodge = len(s)

        params['jitter_width'] = width/(ndodge+2)
        params['width'] = params['dodge_width']
        return params

    @classmethod
    def compute_panel(cls, data, scales, params):
        trans_x = None
        trans_y = None

        if params['jitter_width'] > 0:
            def trans_x(x):
                return jitter(x, amount=params['jitter_width'],
                              random_state=params['random_state'])

        if params['jitter_height'] > 0:
            def trans_y(y):
                return jitter(y, amount=params['jitter_height'],
                              random_state=params['random_state'])

        # dodge, then jitter
        data = cls.collide(data, params=params)
        data = cls.transform_position(data, trans_x, trans_y)
        return data

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

from .position import position
from .collide import collide, pos_dodge
from ..utils.exceptions import GgplotError


class position_dodge(position):
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'width': None}

    def __init__(self, width=None):
        self.params = {'width': width}

    def setup_params(self, data):
        if (('xmin' not in data) and
                ('xmax' not in data) and
                (self.params['width'] is None)):
            msg = ("Width not defined. "
                   "Set with `position_dodge(width = ?)`")
            raise GgplotError(msg)
        return deepcopy(self.params)

    @classmethod
    def compute_panel(cls, data, scales, params):
        return collide(data, width=params['width'],
                       name='position_dodge',
                       strategy=pos_dodge)

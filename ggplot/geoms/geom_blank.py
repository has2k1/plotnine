from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom


class geom_blank(geom):
    DEFAULT_AES = {}
    REQUIRED_AES = set()
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _aes_renames = {}
    _units = set()

    def _plot_unit(self, pinfo, ax):
        pass

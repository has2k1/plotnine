from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .geom_path import geom_path


class geom_line(geom_path):

    def setup_data(self, data):
        return data.sort_values(['PANEL', 'group', 'x'])

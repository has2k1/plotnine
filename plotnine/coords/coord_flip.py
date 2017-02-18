from __future__ import absolute_import, division, print_function

from matplotlib.cbook import Bunch

from .coord_cartesian import coord_cartesian


class coord_flip(coord_cartesian):
    """
    Flipped cartesian coordinates


    The horizontal becomes vertical, and vertical becomes
    horizontal. This is primarily useful for converting
    geoms and statistics which display y conditional
    on x, to x conditional on y.

    See :class:`.coord_cartesian` for documentation.
    """
    def labels(self, label_lookup):
        return flip_labels(coord_cartesian.labels(
            self, label_lookup))

    def transform(self, data, panel_params, munch=False):
        data = flip_labels(data)
        return coord_cartesian.transform(self, data,
                                         panel_params,
                                         munch=munch)

    def setup_panel_params(self, scale_x, scale_y):
        panel_params = coord_cartesian.setup_panel_params(
            self, scale_x, scale_y)
        return flip_labels(panel_params)

    def setup_layout(self, layout):
        # switch the scales
        x, y = 'SCALE_X', 'SCALE_Y'
        layout[x], layout[y] = layout[y], layout[x]
        return layout

    def range(self, panel_params):
        """
        Return the range along the dimensions of the coordinate system
        """
        # Defaults to providing the 2D x-y ranges
        return Bunch(x=panel_params['y_range'],
                     y=panel_params['x_range'])


def flip_labels(obj):
    """
    Rename fields x to y and y to x

    Parameters
    ----------
    obj : dict_like
        Object with labels to rename
    """
    def sub(a, b):
        """
        Substitute all keys that start with a to b
        """
        for label in list(obj.keys()):
            if label.startswith(a):
                new_label = b+label[1:]
                obj[new_label] = obj.pop(label)

    sub('x', 'z')
    sub('y', 'x')
    sub('z', 'y')
    return obj

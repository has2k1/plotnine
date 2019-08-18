from types import SimpleNamespace as NS

from .coord_cartesian import coord_cartesian


class coord_flip(coord_cartesian):
    """
    Flipped cartesian coordinates

    The horizontal becomes vertical, and vertical becomes
    horizontal. This is primarily useful for converting
    geoms and statistics which display y conditional
    on x, to x conditional on y.

    Parameters
    ----------
    xlim : None | (float, float)
        Limits for x axis. If None, then they are
        automatically computed.
    ylim : None | (float, float)
        Limits for y axis. If None, then they are
        automatically computed.
    expand : bool
        If `True`, expand the coordinate axes by
        some factor. If `False`, use the limits
        from the data.
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
        layout[x], layout[y] = layout[y].copy(), layout[x].copy()
        return layout

    def range(self, panel_params):
        """
        Return the range along the dimensions of the coordinate system
        """
        # Defaults to providing the 2D x-y ranges
        return NS(x=panel_params.y.range,
                  y=panel_params.x.range)


def flip_labels(obj):
    """
    Rename fields x to y and y to x

    Parameters
    ----------
    obj : dict_like | types.SimpleNamespace
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

    if hasattr(obj, 'keys'):  # dict or dataframe
        sub('x', 'z')
        sub('y', 'x')
        sub('z', 'y')
    elif hasattr(obj, 'x') and hasattr(obj, 'y'):
        obj.x, obj.y = obj.y, obj.x

    return obj

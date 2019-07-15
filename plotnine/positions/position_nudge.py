from .position import position


class position_nudge(position):
    """
    Nudge points

    Useful to nudge labels away from the points
    being labels.

    Parameters
    ----------
    x : float
        Horizontal nudge
    y : float
        Vertical nudge
    """
    def __init__(self, x=0, y=0):
        self.params = {'x': x, 'y': y}

    @classmethod
    def compute_layer(cls, data, params, layout):
        trans_x, trans_y = None, None

        if params['x']:
            def trans_x(x):
                return x + params['x']

        if params['y']:
            def trans_y(y):
                return y + params['y']

        return cls.transform_position(data, trans_x, trans_y)

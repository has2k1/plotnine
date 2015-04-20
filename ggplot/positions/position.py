from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


class _position_base(object):
    """Base class for all positions"""

    # Aesthetics that map onto the x and y scales
    X = {'x', 'xmin', 'xmax', 'xend', 'xintercept'}
    Y = {'y', 'ymin', 'xmax', 'yend', 'yintercept'}

    def __init__(self, width=None, height=None, **kwargs):
        self.width = kwargs.get('w', width)
        self.height = kwargs.get('h', height)

    def adjust(self, data):
        """
        Positions must override this function

        How?
        ----
        Make necessary adjustments to the columns in the dataframe.

        Create the position transformation functions and
        use self._transform_position() do the rest.

        See: position_jitter.adjust()
        """
        return data

    def _transform_position(self, data, trans_x=None, trans_y=None):
        """
        Transform all the variables that map onto the x and y scales.

        Parameters
        ----------
        data    : dataframe
        trans_x : function
            Transforms x scale mappings
            Takes one argument, either a scalar or an array-type
        trans_y : function
            Transforms y scale mappings
            Takes one argument, either a scalar or an array-type

        Helper function for self.adjust
        """
        if trans_x:
            xs = [name for name in data.columns if name in self.X]
            data[xs] = data[xs].apply(trans_x)

        if trans_y:
            ys = [name for name in data.columns if name in self.Y]
            data[ys] = data[ys].apply(trans_y)
        return data

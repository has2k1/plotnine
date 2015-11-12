from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

from ..utils import check_required_aesthetics, groupby_apply


class position(object):
    """Base class for all positions"""
    REQUIRED_AES = {}

    def __init__(self, **kwargs):
        self.params = deepcopy(kwargs)

    def setup_params(self, data):
        """
        Verify, modify & return a copy of the params.
        """
        return deepcopy(self.params)

    def setup_data(self, data, params):
        """
        Verify & return data
        """
        check_required_aesthetics(
            self.REQUIRED_AES,
            data.columns,
            self.__class__.__name__)
        return data

    @classmethod
    def compute_layer(cls, data, params, panel):
        """
        Compute position for the layer in all panels

        Positions can override this function instead of
        `compute_panel` if the position computations are
        independent of the panel. i.e when not colliding
        """
        def fn(pdata):
            """
            Helper compute function
            """
            # Given data belonging to a specific panel, grab
            # the corresponding scales and call the method
            # that does the real computation
            if len(pdata) == 0:
                return pdata
            pscales = panel.panel_scales(pdata['PANEL'].iat[0])
            return cls.compute_panel(pdata, pscales, params)

        return groupby_apply(data, 'PANEL', fn)

    @classmethod
    def compute_panel(cls, data, scales, params):
        """
        Positions must override this function

        How?
        ----
        Make necessary adjustments to the columns in the dataframe.

        Create the position transformation functions and
        use self.transform_position() do the rest.

        See: position_jitter.compute_panel()
        """
        msg = '{} needs to implement this method'
        raise NotImplementedError(msg.format(cls.__name__))

    @staticmethod
    def transform_position(data, trans_x=None, trans_y=None):
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
        # Aesthetics that map onto the x and y scales
        X = {'x', 'xmin', 'xmax', 'xend', 'xintercept'}
        Y = {'y', 'ymin', 'ymax', 'yend', 'yintercept'}

        if trans_x:
            xs = [name for name in data.columns if name in X]
            data[xs] = data[xs].apply(trans_x)

        if trans_y:
            ys = [name for name in data.columns if name in Y]
            data[ys] = data[ys].apply(trans_y)
        return data

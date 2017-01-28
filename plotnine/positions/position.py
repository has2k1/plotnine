from __future__ import absolute_import, division, print_function

from copy import deepcopy
from six import add_metaclass

from ..utils import check_required_aesthetics, groupby_apply
from ..utils import is_string, Registry
from ..utils.exceptions import PlotnineError


@add_metaclass(Registry)
class position(object):
    """Base class for all positions"""
    __base__ = True

    REQUIRED_AES = {}
    params = {}

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
    def compute_layer(cls, data, params, layout):
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
            scales = layout.get_scales(pdata['PANEL'].iat[0])
            return cls.compute_panel(pdata, scales, params)

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

    @staticmethod
    def from_geom(geom):
        """
        Create and return a position object for the geom

        Parameters
        ----------
        geom : geom
            An instantiated geom object.

        Returns
        -------
        out : position
            A position object

        Raises :class:`PlotnineError` if unable to create a `position`.
        """
        name = geom.params['position']
        if issubclass(type(name), position):
            return name

        if isinstance(name, position):
            klass = name
        elif is_string(name):
            if not name.startswith('position_'):
                name = 'position_{}'.format(name)
            klass = Registry[name]
        else:
            raise PlotnineError(
                'Unknown position of type {}'.format(type(name)))

        return klass()


transform_position = position.transform_position

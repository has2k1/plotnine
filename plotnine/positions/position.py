from copy import copy
from warnings import warn

import numpy as np

from ..utils import check_required_aesthetics, groupby_apply
from ..utils import is_string, Registry
from ..exceptions import PlotnineError, PlotnineWarning


class position(metaclass=Registry):
    """Base class for all positions"""
    __base__ = True

    REQUIRED_AES = {}
    params = {}

    def setup_params(self, data):
        """
        Verify, modify & return a copy of the params.
        """
        return copy(self.params)

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

        Notes
        -----
        Make necessary adjustments to the columns in the dataframe.

        Create the position transformation functions and
        use self.transform_position() do the rest.

        See Also
        --------
        position_jitter.compute_panel
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

        Raises
        ------
        PlotnineError
            If unable to create a `position`.
        """
        name = geom.params['position']
        if issubclass(type(name), position):
            return name

        if isinstance(name, type) and issubclass(name, position):
            klass = name
        elif is_string(name):
            if not name.startswith('position_'):
                name = 'position_{}'.format(name)
            klass = Registry[name]
        else:
            raise PlotnineError(
                'Unknown position of type {}'.format(type(name)))

        return klass()

    @staticmethod
    def strategy(data, params):
        """
        Calculate boundaries of geometry object
        """
        return data

    @classmethod
    def _collide_setup(cls, data, params):
        xminmax = ['xmin', 'xmax']
        width = params.get('width', None)

        # Determine width
        if width is not None:
            # Width set manually
            if not all([col in data.columns for col in xminmax]):
                data['xmin'] = data['x'] - width / 2
                data['xmax'] = data['x'] + width / 2
        else:
            if not all([col in data.columns for col in xminmax]):
                data['xmin'] = data['x']
                data['xmax'] = data['x']

            # Width determined from data, must be floating point constant
            widths = (data['xmax'] - data['xmin']).drop_duplicates()
            widths = widths[~np.isnan(widths)]
            width = widths.iloc[0]

        return data, width

    @classmethod
    def collide(cls, data, params):
        """
        Calculate boundaries of geometry object

        Uses Strategy
        """
        xminmax = ['xmin', 'xmax']
        data, width = cls._collide_setup(data, params)
        if params.get('width', None) is None:
            params['width'] = width

        # Reorder by x position then on group, relying on stable sort to
        # preserve existing ordering. The default stacking order reverses
        # the group in order to match the legend order.
        if params and 'reverse' in params and params['reverse']:
            idx = data.sort_values(
                ['xmin', 'group'], kind='mergesort').index
        else:
            data['-group'] = -data['group']
            idx = data.sort_values(
                ['xmin', '-group'], kind='mergesort').index
            del data['-group']

        data = data.loc[idx, :]

        # Check for overlap
        intervals = data[xminmax].drop_duplicates().values.flatten()
        intervals = intervals[~np.isnan(intervals)]

        if (len(np.unique(intervals)) > 1 and
                any(np.diff(intervals - intervals.mean()) < -1e-6)):
            msg = "{} requires non-overlapping x intervals"
            warn(msg.format(cls.__name__), PlotnineWarning)

        if 'ymax' in data:
            data = groupby_apply(data, 'xmin', cls.strategy, params)
        elif 'y' in data:
            data['ymax'] = data['y']
            data = groupby_apply(data, 'xmin', cls.strategy, params)
            data['y'] = data['ymax']
        else:
            raise PlotnineError('Neither y nor ymax defined')

        return data

    @classmethod
    def collide2(cls, data, params):
        """
        Calculate boundaries of geometry object

        Uses Strategy
        """
        data, width = cls._collide_setup(data, params)
        if params.get('width', None) is None:
            params['width'] = width

        # Reorder by x position then on group, relying on stable sort to
        # preserve existing ordering. The default stacking order reverses
        # the group in order to match the legend order.
        if params and 'reverse' in params and params['reverse']:
            data['-group'] = -data['group']
            idx = data.sort_values(
                ['x', '-group'], kind='mergesort').index
            del data['-group']
        else:
            idx = data.sort_values(
                ['x', 'group'], kind='mergesort').index

        data = data.loc[idx, :]
        data.reset_index(inplace=True, drop=True)
        return cls.strategy(data, params)


transform_position = position.transform_position

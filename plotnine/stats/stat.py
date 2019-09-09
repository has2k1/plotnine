from copy import deepcopy

import pandas as pd

from ..aes import get_calculated_aes
from ..layer import layer
from ..utils import data_mapping_as_kwargs, remove_missing
from ..utils import groupby_apply, copy_keys, uniquecols
from ..utils import is_string, Registry, check_required_aesthetics
from ..exceptions import PlotnineError


class stat(metaclass=Registry):
    """Base class of all stats"""
    __base__ = True

    REQUIRED_AES = set()
    DEFAULT_AES = dict()
    NON_MISSING_AES = set()
    DEFAULT_PARAMS = dict()

    # Should the values produced by the statistic also
    # be transformed in the second pass when recently
    # added statistics are trained to the scales
    retransform = True

    # Stats may modify existing columns or create extra
    # columns.
    #
    # Any extra columns that may be created by the stat
    # should be specified in this set
    # see: stat_bin
    CREATES = set()

    # Documentation for the aesthetics. It ie added under the
    # documentation for mapping parameter. Use {aesthetics_table}
    # placeholder to insert a table for all the aesthetics and
    # their default values.
    _aesthetics_doc = '{aesthetics_table}'

    # The namespace in which the ggplot object is invoked
    environment = None

    def __init__(self, mapping=None, data=None, **kwargs):
        kwargs = data_mapping_as_kwargs((mapping, data), kwargs)
        self._kwargs = kwargs  # Will be used to create the geom
        self.params = copy_keys(kwargs, deepcopy(self.DEFAULT_PARAMS))
        self.aes_params = {ae: kwargs[ae]
                           for ae in (self.aesthetics() &
                                      kwargs.keys())}

    @staticmethod
    def from_geom(geom):
        """
        Return an instantiated stat object

        stats should not override this method.

        Parameters
        ----------
        geom : geom
            `geom`

        Returns
        -------
        out : stat
            A stat object

        Raises
        ------
        :class:`PlotnineError` if unable to create a `stat`.
        """
        name = geom.params['stat']
        kwargs = geom._kwargs
        # More stable when reloading modules than
        # using issubclass
        if (not isinstance(name, type) and
                hasattr(name, 'compute_layer')):
            return name

        if isinstance(name, stat):
            return name
        elif isinstance(name, type) and issubclass(name, stat):
            klass = name
        elif is_string(name):
            if not name.startswith('stat_'):
                name = 'stat_{}'.format(name)
            klass = Registry[name]
        else:
            raise PlotnineError(
                'Unknown stat of type {}'.format(type(name)))

        valid_kwargs = (
             (klass.aesthetics() |
              klass.DEFAULT_PARAMS.keys()) &
             kwargs.keys())

        params = {k: kwargs[k] for k in valid_kwargs}
        return klass(geom=geom, **params)

    def __deepcopy__(self, memo):
        """
        Deep copy without copying the self.data dataframe

        stats should not override this method.
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        # don't make a _kwargs and environment
        shallow = {'_kwargs', 'environment'}
        for key, item in old.items():
            if key in shallow:
                new[key] = old[key]
                memo[id(new[key])] = new[key]
            else:
                new[key] = deepcopy(old[key], memo)

        return result

    @classmethod
    def aesthetics(cls):
        """
        Return a set of all non-computed aesthetics for this stat.

        stats should not override this method.
        """
        aesthetics = cls.REQUIRED_AES.copy()
        calculated = get_calculated_aes(cls.DEFAULT_AES)
        for ae in set(cls.DEFAULT_AES) - set(calculated):
            aesthetics.add(ae)
        return aesthetics

    def use_defaults(self, data):
        """
        Combine data with defaults and set aesthetics from parameters

        stats should not override this method.

        Parameters
        ----------
        data : dataframe
            Data used for drawing the geom.

        Returns
        -------
        out : dataframe
            Data used for drawing the geom.
        """
        missing = (self.aesthetics() -
                   self.aes_params.keys() -
                   set(data.columns))

        for ae in missing-self.REQUIRED_AES:
            if self.DEFAULT_AES[ae] is not None:
                data[ae] = self.DEFAULT_AES[ae]

        missing = (self.aes_params.keys() -
                   set(data.columns))

        for ae in self.aes_params:
            data[ae] = self.aes_params[ae]

        return data

    def setup_params(self, data):
        """
        Overide this to verify or adjust parameters

        Parameters
        ----------
        data : dataframe
            Data

        Returns
        -------
        out : dict
            Parameters used by the stats.
        """
        return self.params

    def setup_data(self, data):
        """
        Overide to modify data before compute_layer is called

        Parameters
        ----------
        data : dataframe
            Data

        Returns
        -------
        out : dataframe
            Data
        """
        return data

    def finish_layer(self, data, params):
        """
        Modify data after the aesthetics have been mapped

        This can be used by stats that require access to the mapped
        values of the computed aesthetics, part 3 as shown below.

            1. stat computes and creates variables
            2. variables mapped to aesthetics
            3. stat sees and modifies data according to the
               aesthetic values

        The default to is to do nothing.

        Parameters
        ----------
        data : dataframe
            Data for the layer
        params : dict
            Paremeters

        Returns
        -------
        data : dataframe
            Modified data
        """
        return data

    @classmethod
    def compute_layer(cls, data, params, layout):
        """
        Calculate statistics for this layers

        This is the top-most computation method for the
        stat. It does not do any computations, but it
        knows how to verify the data, partition it call the
        next computation method and merge results.

        stats should not override this method.

        Parameters
        ----------
        data : panda.DataFrame
            Data points for all objects in a layer.
        params : dict
            Stat parameters
        layout : plotnine.layout.Layout
            Panel layout information
        """
        check_required_aesthetics(
            cls.REQUIRED_AES,
            list(data.columns) + list(params.keys()),
            cls.__name__)

        data = remove_missing(
            data,
            na_rm=params.get('na_rm', False),
            vars=list(cls.REQUIRED_AES | cls.NON_MISSING_AES),
            name=cls.__name__,
            finite=True)

        def fn(pdata):
            """
            Helper compute function
            """
            # Given data belonging to a specific panel, grab
            # the corresponding scales and call the method
            # that does the real computation
            if len(pdata) == 0:
                return pdata
            pscales = layout.get_scales(pdata['PANEL'].iat[0])
            return cls.compute_panel(pdata, pscales, **params)

        return groupby_apply(data, 'PANEL', fn)

    @classmethod
    def compute_panel(cls, data, scales, **params):
        """
        Calculate the stats of all the groups and
        return the results in a single dataframe.

        This is a default function that can be overriden
        by individual stats

        Parameters
        ----------
        data : dataframe
            data for the computing
        scales : types.SimpleNamespace
            x (``scales.x``) and y (``scales.y``) scale objects.
            The most likely reason to use scale information is
            to find out the physical size of a scale. e.g::

                range_x = scales.x.dimension()

        params : dict
            The parameters for the stat. It includes default
            values if user did not set a particular parameter.
        """
        if not len(data):
            return type(data)()

        stats = []
        for _, old in data.groupby('group'):
            new = cls.compute_group(old, scales, **params)
            unique = uniquecols(old)
            missing = unique.columns.difference(new.columns)
            u = unique.loc[[0]*len(new), missing].reset_index(drop=True)
            # concat can have problems with empty dataframes that
            # have an index
            if u.empty and len(u):
                u = type(data)()

            df = pd.concat([new, u], axis=1)
            stats.append(df)

        stats = pd.concat(stats, axis=0, ignore_index=True)
        # Note: If the data coming in has columns with non-unique
        # values with-in group(s), this implementation loses the
        # columns. Individual stats may want to do some preparation
        # before then fall back on this implementation or override
        # it completely.
        return stats

    @classmethod
    def compute_group(cls, data, scales, **params):
        """
        Calculate statistics for the group

        All stats should implement this method

        Parameters
        ----------
        data : dataframe
            Data for a group
        scales : types.SimpleNamespace
            x (``scales.x``) and y (``scales.y``) scale objects.
            The most likely reason to use scale information is
            to find out the physical size of a scale. e.g::

                range_x = scales.x.dimension()

        params : dict
            Parameters
        """
        msg = "{} should implement this method."
        raise NotImplementedError(
            msg.format(cls.__name__))

    def __radd__(self, gg, inplace=False):
        """
        Add layer representing stat object on the right

        Parameters
        ----------
        gg : ggplot
            ggplot object
        inplace : bool
            If True, modify ``gg``.

        Returns
        -------
        out : ggplot
            ggplot object with added layer
        """
        gg = gg if inplace else deepcopy(gg)
        self.environment = gg.environment
        gg += self.to_layer()  # Add layer
        return gg

    def to_layer(self):
        """
        Make a layer that represents this stat

        Returns
        -------
        out : layer
            Layer
        """
        # Create, geom from stat, then layer from geom
        from ..geoms.geom import geom
        return layer.from_geom(geom.from_stat(self))

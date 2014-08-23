from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

import pandas as pd

from ..components import aes
from ..utils.exceptions import GgplotError
from ..layer import layer
from ..utils import is_scalar_or_string, gg_import

__all__ = ['geom']
__all__ = [str(u) for u in __all__]


class geom(object):
    """Base class of all Geoms"""
    DEFAULT_AES = dict()
    REQUIRED_AES = set()
    DEFAULT_PARAMS = dict()

    data = None
    aes = None
    manual_aes = None
    params = None

    # geoms & stats and even users can pass parameters to the
    # layer when it is created.
    layer_params = dict()

    # Some geoms require more information than that provided by the
    # user. This information is usually another aesthetic variable
    # but it could another non-aesthetic variable. It is the duty
    # of the associated statistic to calculate this information.
    #
    # For example:
    #   A geom may have REQUIRED_AES = {'x', 'y'} and
    #   the user may map or manually set only aesthetic 'x',
    #   so the stat would have to calculate 'y'. However this
    #   may not be enough, to actually make the plot the geom
    #   may require the 'width' aesthetic. In this case, 'width'
    #   would be the extra required information.
    #
    # geoms should fill out this set with what they require
    # and is not in REQUIRED_AES
    # see: geom_bar, stat_bin
    _extra_requires = set()

    # Some ggplot aesthetics are named different from the parameters of
    # the matplotlib function that will be used to plot.
    # This dictionary, of the form {ggplot-aes-name: matplotlib-aes-name},
    # connects the two.
    #
    # geoms should fill it out so that the plot
    # information they receive is properly named.
    # See: geom_point
    _aes_renames = dict()

    # A matplotlib plot function may require that an aethestic have a
    # single unique value. e.g. linestyle='dashed' and not
    # linestyle=['dashed', 'dotted', ...].
    # A single call to such a function can only plot lines with the
    # same linestyle. However, if the plot we want has more than one
    # line with different linestyles, we need to group the lines with
    # the same linestyle and plot them as one unit.
    #
    # geoms should fill out this set with such aesthetics so that the
    # plot information they receive can be plotted in a single call.
    # Use names as expected by matplotlib
    # See: geom_point
    _units = set()

    def __init__(self, *args, **kwargs):
        self.valid_aes = set(self.DEFAULT_AES) ^ self.REQUIRED_AES
        self._stat_type = self._get_stat_type(kwargs)
        self.aes, self.data, kwargs = self._find_aes_and_data(args, kwargs)

        # This set will list the geoms that were uniquely set in this
        # geom (not specified already i.e. in the ggplot aes).
        self.aes_unique_to_geom = set(self.aes.keys())

        if 'colour' in kwargs:
            kwargs['color'] = kwargs.pop('colour')

        # When a geom is created, some of the parameters may be meant
        # for the stat and some for the layer.
        # Some arguments are can be identified as either aesthetics to
        # the geom and or parameter settings to the stat, in this case
        # if the argument has a scalar value it is a setting for the stat.
        self._stat_params = {}
        self.params = deepcopy(self.DEFAULT_PARAMS)
        self.manual_aes = {}
        for k, v in kwargs.items():
            if k in self.aes:
                raise GgplotError('Aesthetic, %s, specified twice' % k)
            elif (k in self.valid_aes and
                  k in self._stat_type.DEFAULT_PARAMS and
                  is_scalar_or_string(kwargs[k])):
                self._stat_params[k] = v
            elif k in self.valid_aes:
                self.manual_aes[k] = v
            elif k in self.DEFAULT_PARAMS:
                self.params[k] = v
            elif k in self._stat_type.DEFAULT_PARAMS:
                self._stat_params[k] = v
            else:
                raise GgplotError('Cannot recognize argument: %s' % k)

        self._cache = {}

    def __deepcopy__(self, memo):
        """
        Deep copy without copying the self.data dataframe
        """
        # In case the object cannot be initialized with out
        # arguments
        class _empty(object):
            pass
        result = _empty()
        result.__class__ = self.__class__
        for key, item in self.__dict__.items():
            # don't make a deepcopy of data!
            if key == "data":
                result.__dict__[key] = self.__dict__[key]
                continue
            result.__dict__[key] = deepcopy(self.__dict__[key], memo)
        return result

    def reparameterise(self, data):
        return data

    def draw_groups(self, data, scales, ax, **kwargs):
        """
        Plot all groups

        For effeciency, geoms that do not need to partition
        different groups before plotting should override this
        method and avoid the groupby.
        """
        for gdata in data.groupby('group'):
            pinfos = self._make_pinfos(data)
            for pinfo in pinfos:
                self.draw(pinfo, scales, ax, **kwargs)

    def plot_layer(self, data, ax):
        # Any aesthetic to be overridden by the manual aesthetics
        # should not affect the statistics and the unit grouping
        # of the data
        _cols = set(data.columns) & set(self.manual_aes)
        data = data.drop(_cols, axis=1)
        data = self._calculate_stats(data)
        self._verify_aesthetics(data)
        _needed = self.valid_aes | self._extra_requires
        data = data[list(set(data.columns) & _needed)]

        # aesthetic precedence
        # geom.manual_aes > geom.aes > ggplot.aes (part of data)
        # NOTE: currently geom.aes is not handled. This may be
        # a bad place to do it -- may mess up faceting or just
        # inefficient. Probably in ggplot or layer.
        data = data.rename(columns=self._aes_renames)
        units = self._units & set(data.columns)

        # Create plot information that observes the aesthetic precedence
        #   - (grouped data + manual aesthics)
        #   - modify previous using statistic
        #   - previous overwrites the default aesthetics
        for _data in self._get_unit_grouped_data(data, units):
            _data.update(self._cache['manual_aes_mpl']) # should happen before the grouping
            pinfo = deepcopy(self._cache['default_aes_mpl'])
            pinfo.update(_data)
            self._plot_unit(pinfo, ax)

    def draw(self, pinfo, ax):
        msg = "{} should implement this method."
        raise NotImplementedError(
            msg.format(self.__class__.__name__))

    def _get_stat_type(self, kwargs):
        """
        Find out the stat and return the type object that can be
        used(called) to create it.
        For example, if the stat is 'smooth' we return
        ggplot.stats.stat_smooth
        """
        name = 'stat_{}'.format(
            kwargs.get('stat', self.DEFAULT_PARAMS['stat']))
        return gg_import(name)

    def __radd__(self, gg):
        gg = deepcopy(gg)
        # create stat and hand over the parameters it understands
        if not hasattr(self, '_stat'):
            self._stat = self._stat_type()
            self._stat.params.update(self._stat_params)
        l = layer(geom=self, stat=self._stat, data=self.data,
                  mapping=self.aes,
                  position=self.params['position'],
                  **self.layer_params)
        gg.layers.append(l)
        return gg

    def _find_aes_and_data(self, args, kwargs):
        """
        Identify the aes and data objects.

        Return a dictionary of the aes mappings and
        the data object.

        - args is a list
        - kwargs is a dictionary

        Note: This is a helper function for self.__init__
        It modifies the kwargs
        """
        passed_aes = {}
        data = None
        aes_err = 'Found more than one aes argument. Expecting zero or one'

        for arg in args:
            if isinstance(arg, aes) and passed_aes:
                raise Exception(aes_err)
            if isinstance(arg, aes):
                passed_aes = arg
            elif isinstance(arg, pd.DataFrame):
                data = arg
            else:
                raise GgplotError(
                    'Unknown argument of type "{0}".'.format(type(arg)))

        if 'mapping' in kwargs and passed_aes:
            raise GgplotError(aes_err)
        elif not passed_aes and 'mapping' in kwargs:
            passed_aes = kwargs.pop('mapping')

        if data is None and 'data' in kwargs:
            data = kwargs.pop('data')

        _aes = {}
        # To make mapping of columns to geom/stat or stat parameters
        # possible
        _keep = set(self.DEFAULT_PARAMS) | set(self._stat_type.DEFAULT_PARAMS)
        for k, v in passed_aes.items():
            if k in self.valid_aes or k in _keep:
                _aes[k] = v
            else:
                raise GgplotError('Cannot recognize aesthetic: %s' % k)
        return _aes, data, kwargs

    def _make_pinfos(self, data):
        """
        Make plot information

        Put together the data and the default aesthetics into
        groups that can be plotted in a single call to self._plot_unit.

        Parameters
        ----------
        data : dataframe
            The data to be split into groups

        Returns
        -------
        out : list of dict
            Each dict represents a unique grouping, ready for
            plotting
            The dicts are of the form
            {'column-name' | 'mpl-param-name': list-of-values | value}

        Note
        ----
        This is a helper function for self.draw_group or self.draw
        """
        # (default aesthetics + data), grouped into plotable units
        # and renamed -- ready for matplotlib

        # self._units as ggplot aesthetics
        units = []
        for col in data.columns:
            try:
                flag = self._aes_renames[col] in self._units
            except KeyError:
                flag = col in self._units
            if flag:
                units.append(col)

        # ggplot plot building stuff that is not needed
        # by to draw the plot. Look at all the superclasses
        # other than 'object'
        required = set()
        for klass in type(self).__mro__[:-1]:
            required.update(klass.REQUIRED_AES)
        wanted = set(self.DEFAULT_AES) | required

        def remove_unwanted(d):
            for key in set(d) - wanted:
                del d[key]
            return d

        out = []
        if units:
            for name, _data in data.groupby(units):
                pinfo = deepcopy(self.DEFAULT_AES)
                pinfo.update(_data.to_dict('list'))
                for ae in units:
                    pinfo[ae] = pinfo[ae][0]

                pinfo = remove_unwanted(pinfo)
                pinfo.update(self.manual_aes)
                pinfo = self._rename_to_mpl(pinfo)
                out.append(pinfo)
        else:
            pinfo = deepcopy(self.DEFAULT_AES)
            pinfo.update(data.to_dict('list'))
            pinfo = remove_unwanted(pinfo)
            pinfo.update(self.manual_aes)
            pinfo = self._rename_to_mpl(pinfo)
            out.append(pinfo)
        return out

    def _rename_to_mpl(self, pinfo):
        """
        Rename the keys in pinfo from ggplot aesthetic names
        to matplotlib plot function parameter names
        """
        # use a separate dict to prevent cyclic overwrites
        renamed = {}
        for old, new in self._aes_renames.items():
            try:
                renamed[new] = pinfo.pop(old)
            except KeyError:
                pass
        pinfo.update(renamed)
        return pinfo

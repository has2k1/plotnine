from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

import pandas as pd
import numpy as np
from matplotlib.cbook import iterable
from ggplot.utils import is_string

import ggplot.stats
from ggplot.utils import is_scalar_or_string
from ggplot.components import aes
from ggplot.utils.exceptions import GgplotError

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
        # When putting together the plot information for the geoms,
        # we need the aethetics names to be matplotlib compatible.
        # These are created and stored in self._cache and so would
        # go stale if users or geoms change geom.manual_aes
        self._create_aes_with_mpl_names()

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

    def _plot_unit(self, pinfo, ax):
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
        # get
        try:
            _name = 'stat_%s' % kwargs['stat']
        except KeyError:
            _name = 'stat_%s' % self.DEFAULT_PARAMS['stat']
        return getattr(ggplot.stats, _name)

    def __radd__(self, gg):
        gg = deepcopy(gg)
        # steal aesthetics info.
        self._cache['ggplot.aesthetics'] = deepcopy(gg.aesthetics)
        # create stat and hand over the parameters it understands
        if not hasattr(self, '_stat'):
            self._stat = self._stat_type()
            self._stat.params.update(self._stat_params)
        gg.geoms.append(self)
        return gg

    def _verify_aesthetics(self, data):
        """
        Check if all the required aesthetics have been specified.

        Raise an Exception if an aesthetic is missing
        """

        missing_aes = (self.REQUIRED_AES -
                       set(self.manual_aes) -
                       set(data.columns))
        if missing_aes:
            msg = '{} requires the following missing aesthetics: {}'
            raise GgplotError(msg.format(
                self.__class__.__name__, ', '.join(missing_aes)))

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

    def _calculate_and_rename_stats(self, data):
        """
        Use the stat object (self._stat) to compute the stats
        and make sure the returned columns are renamed to
        matplotlib compatible names
        """
        # only rename the new columns,
        # so keep track of the original ones
        _original = set(data)
        data = self._stat._calculate(data)
        _d = {}
        for old, new in self._aes_renames.items():
            if (old in data) and (old not in _original):
                _d[new] = data.pop(old)
        data.update(_d)
        return data

    def _calculate_stats(self, data):
        """
        Calculate the statistics on each group in the data

        The groups are determined by the mappings.

        Returns
        -------
        data : dataframe
        """
        self._stat._verify_aesthetics(data)
        self._stat._calculate_global(data)
        # In most cases 'x' and 'y' mappings do not and
        # should not influence the grouping. If this is
        # not the desired behaviour then the groups
        # parameter should be used.
        groups = set(self._cache['ggplot.aesthetics'].keys())
        groups = groups & (self.valid_aes - {'x', 'y'})
        groups = groups & set(data.columns)

        new_data = pd.DataFrame()
        # TODO: Find a more effecient way to concatenate
        # the dataframes
        if groups:
            for name, _data in data.groupby(sorted(groups)):
                _data = _data.reindex()
                _data = self._stat._calculate(_data)
                new_data = new_data.append(_data, ignore_index=True)
        else:
            new_data = self._stat._calculate(data)

        return new_data

    def _create_aes_with_mpl_names(self):
        """
        Create copies of the manual and default aesthetics
        with matplotlib compatitble names.

        Uses self._aes_renames, and the results are stored
        in:
            self._cache['manual_aes_mpl']
            self._cache['default_aes_mpl']
        """
        def _rename_fn(aes_dict):
            # to prevent overwrites
            _d = {}
            for old, new in self._aes_renames.items():
                if old in aes_dict:
                    _d[new] = aes_dict.pop(old)
            aes_dict.update(_d)

        self._cache['manual_aes_mpl'] = deepcopy(self.manual_aes)
        self._cache['default_aes_mpl'] = deepcopy(self.DEFAULT_AES)
        _rename_fn(self._cache['manual_aes_mpl'])
        _rename_fn(self._cache['default_aes_mpl'])

    def _get_unit_grouped_data(self, data, units):
        """
        Split data into groups.

        The units determine the groups.

        Parameters
        ----------
        data : dataframe
            The data to be split into groups
        units : set
            A set of column names in the data and by
            which the grouping will happen

        Returns
        -------
        out : list of dict
            Each dict represents a unique grouping.
            The dicts are of the form
            {'column-name': list-of-values | value}

        Note
        ----
        This is a helper function for self._plot_layer
        """
        out = []
        if units:
            for name, _data in data.groupby(list(units)):
                _data = _data.to_dict('list')
                for ae in units:
                    _data[ae] = _data[ae][0]
                out.append(_data)
        else:
            _data = data.to_dict('list')
            out.append(_data)
        return out


    def sort_by_x(self, pinfo):
        """
        Sort the lists in pinfo according to pinfo['x']
        This function is useful for geom's that expect
        the x-values to come in sorted order
        """
        # Remove list types from pinfo
        _d = {}
        for k in list(pinfo.keys()):
            if not is_string(pinfo[k]) and iterable(pinfo[k]):
                _d[k] = pinfo.pop(k)

        # Sort numerically if all items can be cast
        try:
            x = list(map(np.float, _d['x']))
        except (ValueError, TypeError):
            x = _d['x']

        # Make sure we don't try to sort something unsortable
        try:
            idx = np.argsort(x)
            # Put sorted lists back in pinfo
            for key in _d:
                pinfo[key] = [_d[key][i] for i in idx]
        except:
            pass
        return pinfo


from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

import pandas as pd

from ..components.aes import aes, make_labels
from ..utils.exceptions import GgplotError
from ..layer import layer
from ..utils import is_scalar_or_string, gg_import, defaults

__all__ = ['geom']
__all__ = [str(u) for u in __all__]


class geom(object):
    """Base class of all Geoms"""
    DEFAULT_AES = dict()
    REQUIRED_AES = set()
    DEFAULT_PARAMS = dict()

    data = None           # geom/layer specific dataframe
    aes = None            # mappings i.e aes(x=col1, fill=col2, ...)
    manual_aes = None     # setting of aesthetic
    params = None         # parameter settings
    guide_geom = 'point'  # the geom responsible for the legend

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
        self._layer_params = {}
        layer_params = ['group', 'show_guide', 'inherit_aes']
        for p in layer_params:
            try:
                self._layer_params[p] = self.params.pop(p)
            except KeyError:
                pass

        for k, v in kwargs.items():
            if k in self.aes:
                raise GgplotError('Aesthetic, %s, specified twice' % k)
            # geom recognizes aesthetic but stat wants it as a parameter,
            # if it is a scalar the stat takes it
            elif (k in self.valid_aes and
                  k in self._stat_type.DEFAULT_PARAMS and
                  is_scalar_or_string(kwargs[k])):
                self._stat_params[k] = v
            # geom mapping
            elif k in self.valid_aes:
                self.manual_aes[k] = v
            # layer parameters
            elif k in layer_params:
                self._layer_params[k] = kwargs[k]
            # Override default geom parameters
            elif k in self.DEFAULT_PARAMS:
                self.params[k] = v
            # stat parameters
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

    @staticmethod
    def reparameterise(data):
        return data

    def draw_groups(self, data, scales, ax, **kwargs):
        """
        Plot all groups

        For effeciency, geoms that do not need to partition
        different groups before plotting should override this
        method and avoid the groupby.
        """
        for _, gdata in data.groupby('group'):
            pinfos = self._make_pinfos(gdata, kwargs)
            for pinfo in pinfos:
                self.draw(pinfo, scales, ax, **kwargs)

    @staticmethod
    def draw(pinfo, scales, ax, **kwargs):
        msg = "The geom should implement this method."
        raise NotImplementedError(msg)

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

        l = layer(geom=self,
                  stat=self._stat,
                  data=self.data,
                  mapping=self.aes,
                  position=self.params['position'],
                  **self._layer_params)
        gg.layers.append(l)

        # Add any new labels
        mapping = make_labels(self.aes)
        default = make_labels(self._stat.DEFAULT_AES)
        new_labels = defaults(mapping, default)
        gg.labels = defaults(gg.labels, new_labels)
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
        _keep.update(self._stat_type.DEFAULT_AES)
        _keep.add('group')
        for k, v in passed_aes.items():
            if k in self.valid_aes or k in _keep:
                _aes[k] = v
        return _aes, data, kwargs

    def _make_pinfos(self, data, kwargs):
        """
        Make plot information

        Put together the data and the default aesthetics into
        groups that can be plotted in a single call to self.draw

        Parameters
        ----------
        data : dataframe
            The data to be split into groups
        kwargs : dict
            kwargs passed to the draw or draw_groups methods

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
        wanted.add('group')

        def remove_unwanted(d):
            for key in set(d) - wanted:
                del d[key]
            return d

        out = []

        def prep_and_append(pinfo):
            """
            After data has been converted to a dict of lists
            prepare it for ploting and append it the output
            list
            """
            pinfo = remove_unwanted(pinfo)
            pinfo.update(self.manual_aes)
            pinfo = self._rename_to_mpl(pinfo)
            pinfo['zorder'] = kwargs['zorder']
            out.append(pinfo)

        if units:
            for name, _data in data.groupby(units):
                pinfo = deepcopy(self.DEFAULT_AES)
                pinfo.update(_data.to_dict('list'))
                for ae in units:
                    pinfo[ae] = pinfo[ae][0]

                prep_and_append(pinfo)
        else:
            pinfo = deepcopy(self.DEFAULT_AES)
            pinfo.update(data.to_dict('list'))
            prep_and_append(pinfo)
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

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

import pandas as pd
import six

from ..components.aes import aes, make_labels, rename_aesthetics
from ..components.layer import layer
from ..utils.exceptions import GgplotError
from ..utils import gg_import, defaults, suppress, copy_keys
from ..stats.stat import stat


class geom(object):
    """Base class of all Geoms"""
    DEFAULT_AES = dict()
    REQUIRED_AES = set()
    DEFAULT_PARAMS = dict()

    data = None           # geom/layer specific dataframe
    mapping = None        # mappings i.e aes(x=col1, fill=col2, ...)
    aes_params = None     # setting of aesthetic
    params = None         # parameter settings

    # The geom responsible for the legend if draw_legend is
    # not implemented
    legend_geom = 'point'

    def __init__(self, *args, **kwargs):
        kwargs = rename_aesthetics(kwargs)
        kwargs = self._sanitize_arguments(args, kwargs)
        self._cache = {'kwargs': kwargs}  # for making stat & layer
        self._stat = self._make_stat()
        self.verify_arguments(kwargs)     # geom, stat, layer

        # separate aesthetics and parameters
        self.aes_params = copy_keys(kwargs, {}, self.aesthetics())
        self.params = copy_keys(kwargs, deepcopy(self.DEFAULT_PARAMS))
        self.mapping = kwargs['mapping']
        self.data = kwargs['data']

    @classmethod
    def aesthetics(cls):
        """
        Return all the aesthetics for this geom
        """
        main = six.viewkeys(cls.DEFAULT_AES) | cls.REQUIRED_AES
        other = {'group'}
        # Need to recognize both spellings
        if 'color' in main:
            other.add('colour')
        if 'outlier_color' in main:
            other.add('outlier_colour')
        return main | other

    def __deepcopy__(self, memo):
        """
        Deep copy without copying the self.data dataframe
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        for key, item in self.__dict__.items():
            if key == 'data':
                result.__dict__[key] = self.__dict__[key]
            else:
                result.__dict__[key] = deepcopy(self.__dict__[key], memo)

        return result

    def setup_data(self, data):
        return data

    def use_defaults(self, data):
        """
        Combine data with defaults and set aesthetics from parameters
        """
        missing_aes = (six.viewkeys(self.DEFAULT_AES) -
                       six.viewkeys(self.aes_params) -
                       set(data.columns))

        # Not in data and not set, use default
        for ae in missing_aes:
            data[ae] = self.DEFAULT_AES[ae]

        # If set, use it
        for ae in self.aes_params:
            data[ae] = self.aes_params[ae]

        return data

    def draw_layer(self, data, panel, coord, zorder):
        """
        Draw layer across all panels

        Parameters
        ----------
        data : DataFrame
            DataFrame specific for this layer
        panel : Panel
            Panel object created when the plot is getting
            built
        coord : coord
            Type of coordinate axes
        zorder : int
            Stacking order of the layer in the plot
        """
        params = deepcopy(self.params)
        params.update(self._stat.params)
        params['zorder'] = zorder
        for pid, pdata in data.groupby('PANEL'):
            if len(pdata) == 0:
                continue
            pdata.is_copy = None
            ploc = pid - 1
            panel_scales = panel.ranges[ploc]
            ax = panel.axs[ploc]
            self.draw_panel(pdata, panel_scales, coord, ax, **params)

    def draw_panel(self, data, panel_scales, coord, ax, **params):
        """
        Plot all groups

        For effeciency, geoms that do not need to partition
        different groups before plotting should override this
        method and avoid the groupby.

        Parameters
        ----------
        data : dataframe
            Data to be plotted by this geom. This is the
            dataframe created in the plot_build pipeline
        scales : dict
            The scale information as may be required by the
            axes. At this point, that information is about
            ranges, ticks and labels. Keys of interest to
            the geom are:
                - 'x_range' -- tuple
                - 'y_range' -- tuple
        coord : coord
            Coordinate (e.g. coord_cartesian) system of the
            geom
        ax : axes
            Axes on which to plot
        params : dict
            Combined parameters for the geom and stat. Also
            includes the 'zorder'.
        """
        for _, gdata in data.groupby('group'):
            gdata.reset_index(inplace=True, drop=True)
            gdata.is_copy = None
            self.draw_group(gdata, panel_scales, coord, ax, **params)

    @staticmethod
    def draw_group(data, panel_scales, coord, ax, **params):
        """
        Plot data
        """
        msg = "The geom should implement this method."
        raise NotImplementedError(msg)

    @staticmethod
    def draw_unit(data, panel_scales, coord, ax, **params):
        """
        Plot data

        A matplotlib plot function may require that an aethestic
        have a single unique value. e.g. linestyle='dashed' and
        not linestyle=['dashed', 'dotted', ...].
        A single call to such a function can only plot lines with
        the same linestyle. However, if the plot we want has more
        than one line with different linestyles, we need to group
        the lines with the same linestyle and plot them as one
        unit. In this case, draw_group calls this function to do
        the plotting.

        See: geom_point
        """
        msg = "The geom should implement this method."
        raise NotImplementedError(msg)

    def __radd__(self, gg):
        gg = deepcopy(gg)

        # create and add layer
        gg.layers.append(self._make_layer())

        # Add any new labels
        mapping = make_labels(self.mapping)
        default = make_labels(self._stat.DEFAULT_AES)
        new_labels = defaults(mapping, default)
        gg.labels = defaults(gg.labels, new_labels)
        return gg

    def _make_layer(self):
        kwargs = self._cache['kwargs']
        DP = self.DEFAULT_PARAMS
        lkwargs = {'geom': self,
                   'mapping': kwargs['mapping'],
                   'data': kwargs['data'],
                   'stat': self._stat,
                   'position': kwargs.get('position',
                                          DP['position'])}

        for param in ('show_legend', 'inherit_aes'):
            if param in kwargs:
                lkwargs[param] = kwargs[param]
            else:
                with suppress(KeyError):
                    lkwargs[param] = DP[param]

        return layer(**lkwargs)

    def _make_stat(self):
        """
        Return stat instance for this geom

        Create a stat if none has been passed in the
        kwargs
        """
        kwargs = self._cache['kwargs']
        # The user (or DEFAULT_PARAMS) can specify one of;
        # - a stat object
        # - a stat class
        # - the name of the stat (only the provided stats)
        stat_klass = kwargs.get(
            'stat', self.DEFAULT_PARAMS['stat'])

        # More stable when reloading modules than
        # using issubclass
        if (not isinstance(stat_klass, type) and
                hasattr(stat_klass, 'compute_layer')):
            return stat_klass

        if isinstance(stat_klass, six.string_types):
            if not stat_klass.startswith('stat_'):
                stat_klass = 'stat_{}'.format(stat_klass)
            stat_klass = gg_import(stat_klass)

        try:
            recognized = (
                (stat_klass.aesthetics() |
                 six.viewkeys(stat_klass.DEFAULT_PARAMS)) &
                six.viewkeys(kwargs))
        except AttributeError:
            msg = '{} is not a stat'.format(stat_klass)
            raise GgplotError(msg)

        stat_params = {}
        for p in recognized:
            stat_params[p] = kwargs[p]
        return stat_klass(geom=self.__class__.__name__[5:],
                          **stat_params)

    def _sanitize_arguments(self, args, kwargs):
        """
        Return kwargs with the mapping and data values
        """
        mapping, data = {}, None
        aes_err = ('Found more than one aes argument. '
                   'Expecting zero or one')
        data_err = 'More than one dataframe argument'

        # check args #
        for arg in args:
            if isinstance(arg, aes) and mapping:
                raise GgplotError(aes_err)
            if isinstance(arg, pd.DataFrame) and data:
                raise GgplotError(data_err)

            if isinstance(arg, aes):
                mapping = arg
            elif isinstance(arg, pd.DataFrame):
                data = arg
            else:
                msg = "Unknown argument of type '{0}'."
                raise GgplotError(msg.format(type(arg)))

        # check kwargs #
        # kwargs mapping has precedence over that in args
        if 'mapping' not in kwargs:
            kwargs['mapping'] = mapping

        if data is not None and 'data' in kwargs:
            raise GgplotError(data_err)
        elif 'data' not in kwargs:
            kwargs['data'] = data

        duplicates = set(kwargs['mapping']) & set(kwargs)
        if duplicates:
            msg = 'Aesthetics {} specified two times.'
            raise GgplotError(msg.format(duplicates))
        return kwargs

    def verify_arguments(self, kwargs):
        unknown = (six.viewkeys(kwargs) -
                   self.aesthetics() -                  # geom aesthetics
                   six.viewkeys(self.DEFAULT_PARAMS) -  # geom parameters
                   {'data', 'mapping'} -                # layer parameters
                   {'show_legend', 'inherit_aes'} -     # layer parameters
                   self._stat.aesthetics() -            # stat aesthetics
                   six.viewkeys(
                       self._stat.DEFAULT_PARAMS))      # stat parameters
        if unknown:
            msg = 'Unknown parameters {}'
            raise GgplotError(msg.format(unknown))

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

import pandas as pd

from ..components.aes import aes, make_labels, rename_aesthetics
from ..components.layer import layer
from ..utils.exceptions import GgplotError
from ..utils import gg_import, defaults, suppress
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
    guide_geom = 'point'

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
    # See: geom_point
    _units = set()

    def __init__(self, *args, **kwargs):
        kwargs = rename_aesthetics(kwargs)
        kwargs = self._sanitize_arguments(args, kwargs)
        self._cache = {'kwargs': kwargs}

        _kwargs = set(kwargs)
        duplicates = set(kwargs['mapping']) & _kwargs
        if duplicates:
            msg = 'Aesthetics {} specified two times.'
            raise GgplotError(msg.format(duplicates))

        # Create a stat if non has been passed in
        with suppress(KeyError):
            if isinstance(kwargs['stat'], stat):
                self._stat = kwargs['stat']

        try:
            self._stat
        except AttributeError:
            self._stat = self._make_stat()

        self.verify_arguments(kwargs)

        # separate aesthetics and parameters
        aparams = _kwargs & self.aesthetics
        gparams = _kwargs & set(self.DEFAULT_PARAMS)

        def set_params(d, which_params):
            for param in which_params:
                d[param] = kwargs[param]
            return d

        self.aes_params = set_params({}, aparams)
        self.params = set_params(deepcopy(self.DEFAULT_PARAMS), gparams)
        self.mapping = kwargs['mapping']
        self.data = kwargs['data']

    @property
    def aesthetics(self):
        """
        Return all the aesthetics for this geom
        """
        try:
            s = self._stat.REQUIRED_AES
        except AttributeError:
            s = set()
        return set(self.DEFAULT_AES) | self.REQUIRED_AES | s | {'group'}

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

    def draw_groups(self, data, scales, coordinates, ax, **params):
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
        coordinates : coord
            Coordinate (e.g. coord_cartesian) system of the
            geom
        ax : axes
            Axes on which to plot
        params : dict
            Combined parameters for the geom and stat. Also
            includes the 'zorder'.
        """
        for _, gdata in data.groupby('group'):
            pinfos = self._make_pinfos(gdata, params)
            for pinfo in pinfos:
                self.draw(pinfo, scales, coordinates, ax, **params)

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **params):
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

        for param in ('show_guide', 'inherit_aes'):
            if param in kwargs:
                lkwargs[param] = kwargs[param]
            else:
                with suppress(KeyError):
                    lkwargs[param] = DP[param]

        return layer(**lkwargs)

    def _make_stat(self):
        """
        Return stat instance for this geom
        """
        kwargs = self._cache['kwargs']
        name = 'stat_{}'.format(
            kwargs.get('stat', self.DEFAULT_PARAMS['stat']))
        stat_type = gg_import(name)
        params = {}
        for p in set(kwargs) & set(stat_type.DEFAULT_PARAMS):
            params[p] = kwargs[p]
        return stat_type(geom=self.__class__.__name__[5:],
                         **params)

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

        return kwargs

    def verify_arguments(self, kwargs):
        unknown = (set(kwargs) -
                   self.aesthetics -
                   set(self.DEFAULT_PARAMS) -
                   {'data', 'mapping'} -
                   {'show_guide', 'inherit_aes'} -  # layer
                   set(self._stat.DEFAULT_PARAMS))
        if unknown:
            msg = 'Unknown parameters {}'
            raise GgplotError(msg.format(unknown))

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
        # (default aesthetics + data), grouped into plottable units
        units = []
        for col in data.columns:
            if col in self._units:
                units.append(col)

        shrinkable = {'alpha', 'fill', 'color', 'size', 'linetype'}

        def shrink(pinfo):
            """
            Reduce shrinkable parameters to scalars if possible.
            """
            # If it is the same value in the list make it a scalar
            # This can help the matplotlib functions draw faster
            for ae in set(pinfo) & shrinkable:
                with suppress(TypeError, IndexError):
                    if all(pinfo[ae][0] == v for v in pinfo[ae]):
                        pinfo[ae] = pinfo[ae][0]
            return pinfo

        def prep(pinfo):
            """
            After data has been converted to a dict of lists
            prepare it for plotting
            """
            pinfo.update(self.aes_params)
            pinfo = shrink(pinfo)
            pinfo['zorder'] = kwargs['zorder']
            return pinfo

        out = []
        if units:
            for name, _data in data.groupby(units):
                pinfo = deepcopy(self.DEFAULT_AES)
                pinfo.update(_data.to_dict('list'))
                for ae in units:
                    pinfo[ae] = pinfo[ae][0]

                out.append(prep(pinfo))
        else:
            pinfo = deepcopy(self.DEFAULT_AES)
            pinfo.update(data.to_dict('list'))
            out.append(prep(pinfo))

        return out

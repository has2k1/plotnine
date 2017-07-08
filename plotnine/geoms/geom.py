from __future__ import absolute_import, division, print_function
from copy import deepcopy

import six
from six import add_metaclass

from ..stats.stat import stat
from ..aes import rename_aesthetics, is_valid_aesthetic
from ..layer import layer
from ..positions.position import position
from ..utils import data_mapping_as_kwargs, remove_missing
from ..utils import copy_keys, is_string, Registry
from ..exceptions import PlotnineError


@add_metaclass(Registry)
class geom(object):
    """Base class of all Geoms"""
    __base__ = True
    DEFAULT_AES = dict()     #: Default aesthetics for the geom
    REQUIRED_AES = set()     #: Required aesthetics for the geom
    DEFAULT_PARAMS = dict()  #: Required parameters for the geom

    data = None           #: geom/layer specific dataframe
    mapping = None        #: mappings i.e aes(x=col1, fill=col2, ...)
    aes_params = None     # setting of aesthetic
    params = None         # parameter settings

    # The geom responsible for the legend if draw_legend is
    # not implemented
    legend_geom = 'point'

    def __init__(self, *args, **kwargs):
        kwargs = rename_aesthetics(kwargs)
        kwargs = data_mapping_as_kwargs(args, kwargs)
        self._kwargs = kwargs  # Will be used to create stat & layer

        # separate aesthetics and parameters
        self.aes_params = copy_keys(kwargs, {}, self.aesthetics())
        self.params = copy_keys(kwargs, deepcopy(self.DEFAULT_PARAMS))
        self.mapping = kwargs['mapping']
        self.data = kwargs['data']
        self._stat = stat.from_geom(self)
        self._position = position.from_geom(self)
        self.verify_arguments(kwargs)     # geom, stat, layer

    @staticmethod
    def from_stat(stat):
        """
        Return an instantiated geom object

        Parameters
        ----------
        stat : stat
            `stat`

        Returns
        -------
        out : geom
            A geom object

        Raises :class:`PlotnineError` if unable to create a `geom`.
        """
        name = stat.params['geom']
        if issubclass(type(name), geom):
            return name

        if isinstance(name, type) and issubclass(name, geom):
            klass = name
        elif is_string(name):
            if not name.startswith('geom_'):
                name = 'geom_{}'.format(name)
            klass = Registry[name]
        else:
            raise PlotnineError(
                'Unknown geom of type {}'.format(type(name)))

        return klass(stat=stat, **stat._kwargs)

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
        old = self.__dict__
        new = result.__dict__

        for key, item in old.items():
            if key in {'data', '_kwargs'}:
                new[key] = old[key]
            else:
                new[key] = deepcopy(old[key], memo)

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
        for ae, value in self.aes_params.items():
            try:
                data[ae] = value
            except ValueError:
                # sniff out the special cases, like custom
                # tupled linetypes, shapes and colors
                if is_valid_aesthetic(value, ae):
                    data[ae] = [value]*len(data)
                else:
                    msg = ("'{}' does not look like a "
                           "valid value for `{}`")
                    raise PlotnineError(msg.format(value, ae))

        return data

    def draw_layer(self, data, layout, coord, **params):
        """
        Draw layer across all panels

        Parameters
        ----------
        data : DataFrame
            DataFrame specific for this layer
        layout : Lanel
            Layout object created when the plot is getting
            built
        coord : coord
            Type of coordinate axes
        params : dict
            Combined *geom* and *stat* parameters. Also
            includes the stacking order of the layer in
            the plot (*zorder*)
        """
        for pid, pdata in data.groupby('PANEL'):
            if len(pdata) == 0:
                continue
            pdata.is_copy = None
            ploc = pid - 1
            panel_params = layout.panel_params[ploc]
            ax = layout.axs[ploc]
            self.draw_panel(pdata, panel_params, coord, ax, **params)

    def draw_panel(self, data, panel_params, coord, ax, **params):
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
            self.draw_group(gdata, panel_params, coord, ax, **params)

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        """
        Plot data
        """
        msg = "The geom should implement this method."
        raise NotImplementedError(msg)

    @staticmethod
    def draw_unit(data, panel_params, coord, ax, **params):
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

    def __radd__(self, gg, inplace=False):
        gg = gg if inplace else deepcopy(gg)

        # create and add layer
        gg += layer.from_geom(self)
        return gg

    def verify_arguments(self, kwargs):
        keys = six.viewkeys
        unknown = (keys(kwargs) -
                   self.aesthetics() -                # geom aesthetics
                   keys(self.DEFAULT_PARAMS) -        # geom parameters
                   self._stat.aesthetics() -          # stat aesthetics
                   keys(self._stat.DEFAULT_PARAMS) -  # stat parameters
                   {'data', 'mapping',                # layer parameters
                    'show_legend', 'inherit_aes'})    # layer parameters
        if unknown:
            msg = ("Parameters {}, are not understood by "
                   "either the geom, stat or layer.")
            raise PlotnineError(msg.format(unknown))

    def handle_na(self, data):
        """
        Remove rows with NaN values

        Parameters
        ----------
        data : dataframe
            Data

        Returns
        -------
        out : dataframe
            Data without the NaNs

        Note
        ----
        Shows a warning if the any rows are removed and the
        `na_rm` parameter is False. It only takes into account
        the columns of the required aesthetics.
        """
        return remove_missing(data, self.params['na_rm'],
                              list(self.REQUIRED_AES),
                              self.__class__.__name__)

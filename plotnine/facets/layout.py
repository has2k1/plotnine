from __future__ import division

import numpy as np
from matplotlib.cbook import Bunch

from ..coords import coord_flip
from ..utils.exceptions import PlotnineError
from ..utils import match, suppress


class Layout(object):
    #: facet
    facet = None

    #: A dataframe with the layout information of the plot
    panel_layout = None

    #: A :class:`Bunch` of lists for x and y scales
    panel_scales = None

    #: Range & breaks information for each panel
    panel_params = None

    axs = None        # MPL axes

    def setup(self, layers, plot):
        """
        Create a layout for the panels

        The layout is a dataframe that stores all the
        structual information about the panels that will
        make up the plot. The actual layout depends on
        the type of facet.
        """
        self.facet = plot.facet
        data = [plot.data] + [l.data for l in layers]
        data = self.facet.setup_data(data)
        self.panel_layout = self.facet.train(data)
        self.panel_scales = Bunch(x=None, y=None)

        if len(self.panel_layout.columns.intersection(
                {'PANEL', 'SCALE_X', 'SCALE_Y'})) != 3:

            raise PlotnineError(
                "Facet layout has bad format. It must contains "
                "the columns 'PANEL', 'SCALE_X', and 'SCALE_Y'")

        # Special case of coord_flip - switch the layout scales
        if isinstance(plot.coordinates, coord_flip):
            _t = self.panel_layout
            _t['SCALE_X'], _t['SCALE_Y'] = _t['SCALE_Y'], _t['SCALE_X']

    def map(self, layers, plot):
        """
        Map layer data to the panels

        This method creates a dataframe copy (``layer.data``)
        for each layer.

        Parameters
        ----------
        plot : ggplot
            Object being built
        layers : Layers
            List of layers
        """
        for layer in layers:
            # Do not mess with the user supplied dataframes
            if layer.data is None:
                data = plot.data.copy()
            else:
                data = layer.data.copy()
            layer.data = self.facet.map(
                data, self.panel_layout)

    def train_position(self, layers, x_scale, y_scale):
        """
        Create all the required x & y panel_scales y_scales
        and set the ranges for each scale according to the data.

        Note
        ----
        The number of x or y scales depends on the facetting,
        particularly the scales parameter. e.g if `scales='free'`
        then each panel will have separate x and y scales, and
        if `scales='fixed'` then all panels will share an x
        scale and a y scale.
        """
        layout = self.panel_layout
        if self.panel_scales.x is None and x_scale:
            result = self.facet.init_scales(layout, x_scale, None)
            self.panel_scales.x = result.x

        if self.panel_scales.y is None and y_scale:
            result = self.facet.init_scales(layout, None, y_scale)
            self.panel_scales.y = result.y

        self.facet.train_position_scales(self, layers)

    def map_position(self, layers):
        """
        Map x & y (position) aesthetics onto the scales.

        e.g If the x scale is scale_x_log10, after this
        function all x, xmax, xmin, ... columns in data
        will be mapped onto log10 scale (log10 transformed).
        The real mapping is handled by the scale.map
        """
        _layout = self.panel_layout
        scales = self.panel_scales

        for layer in layers:
            data = layer.data
            match_id = match(data['PANEL'], _layout['PANEL'])
            if scales.x:
                x_vars = list(set(scales.x[0].aesthetics) &
                              set(data.columns))
                SCALE_X = _layout['SCALE_X'].iloc[match_id].tolist()
                scales.x.map(data, x_vars, SCALE_X)

            if scales.y:
                y_vars = list(set(scales.y[0].aesthetics) &
                              set(data.columns))
                SCALE_Y = _layout['SCALE_Y'].iloc[match_id].tolist()
                scales.y.map(data, y_vars, SCALE_Y)

    def get_scales(self, i):
        """
        Return x & y scales for panel i

        Parameters
        ----------
        i : int
          Panel id

        Returns
        -------
        scales : Bunch
          Class attributes *x* for the x scale and *y*
          for the y scale of the panel

        """
        # wrapping with np.asarray prevents an exception
        # on some datasets
        bool_idx = (np.asarray(self.panel_layout['PANEL']) == i)
        xsc = None
        ysc = None

        if self.panel_scales.x:
            idx = self.panel_layout.loc[bool_idx, 'SCALE_X'].values[0]
            xsc = self.panel_scales.x[idx-1]

        if self.panel_scales.y:
            idx = self.panel_layout.loc[bool_idx, 'SCALE_Y'].values[0]
            ysc = self.panel_scales.y[idx-1]

        return Bunch(x=xsc, y=ysc)

    def reset_position_scales(self):
        """
        Reset x and y scales
        """
        if not self.facet.shrink:
            return

        with suppress(AttributeError):
            self.panel_scales.x.reset()

        with suppress(AttributeError):
            self.panel_scales.y.reset()

    def setup_panel_params(self, coord):
        """
        Calculate the x & y range & breaks information for each panel

        Parameters
        ----------
        coord : coord
            Coordinate
        """
        if not self.panel_scales.x:
            raise PlotnineError('Missing an x scale')

        if not self.panel_scales.y:
            raise PlotnineError('Missing a y scale')

        self.panel_params = []
        cols = ['SCALE_X', 'SCALE_Y']
        for i, j in self.panel_layout[cols].itertuples(index=False):
            i, j = i-1, j-1
            params = coord.setup_panel_params(
                self.panel_scales.x[i],
                self.panel_scales.y[j])
            self.panel_params.append(params)

    def finish_data(self, layers):
        """
        Modify data before it is drawn out by the geom

        Parameters
        ----------
        layers : list
            List of layers
        """
        for layer in layers:
            layer.data = self.facet.finish_data(layer.data, self)

from __future__ import division

import numpy as np
from matplotlib.cbook import Bunch

from ..exceptions import PlotnineError
from ..utils import match, suppress


class Layout(object):
    #: facet
    facet = None

    #: coordinate system
    coord = None

    #: A dataframe with the layout information of the plot
    layout = None

    #: List of x scales
    panel_scales_x = None

    #: List of y scales
    panel_scales_y = None

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

        This method ensures that each layer has a copy of the
        data it needs in `layer.data`. That data is also has
        column `PANEL` that indicates the panel onto which each
        data row/item will be plotted.
        """
        data = [l.data for l in layers]

        # setup facets
        self.facet = plot.facet
        self.facet.setup_params(data)
        data = self.facet.setup_data(data)

        # setup coords
        self.coord = plot.coordinates
        self.coord.setup_params(data)
        data = self.coord.setup_data(data)

        # Generate panel layout
        data = self.facet.setup_data(data)
        self.layout = self.facet.compute_layout(data)
        self.layout = self.coord.setup_layout(self.layout)
        self.check_layout()

        # Map the data to the panels
        for layer, ldata in zip(layers, data):
            layer.data = self.facet.map(ldata, self.layout)

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
        layout = self.layout
        if self.panel_scales_x is None and x_scale:
            result = self.facet.init_scales(layout, x_scale, None)
            self.panel_scales_x = result.x

        if self.panel_scales_y is None and y_scale:
            result = self.facet.init_scales(layout, None, y_scale)
            self.panel_scales_y = result.y

        self.facet.train_position_scales(self, layers)

    def map_position(self, layers):
        """
        Map x & y (position) aesthetics onto the scales.

        e.g If the x scale is scale_x_log10, after this
        function all x, xmax, xmin, ... columns in data
        will be mapped onto log10 scale (log10 transformed).
        The real mapping is handled by the scale.map
        """
        _layout = self.layout

        for layer in layers:
            data = layer.data
            match_id = match(data['PANEL'], _layout['PANEL'])
            if self.panel_scales_x:
                x_vars = list(set(self.panel_scales_x[0].aesthetics) &
                              set(data.columns))
                SCALE_X = _layout['SCALE_X'].iloc[match_id].tolist()
                self.panel_scales_x.map(data, x_vars, SCALE_X)

            if self.panel_scales_y:
                y_vars = list(set(self.panel_scales_y[0].aesthetics) &
                              set(data.columns))
                SCALE_Y = _layout['SCALE_Y'].iloc[match_id].tolist()
                self.panel_scales_y.map(data, y_vars, SCALE_Y)

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
        bool_idx = (np.asarray(self.layout['PANEL']) == i)
        xsc = None
        ysc = None

        if self.panel_scales_x:
            idx = self.layout.loc[bool_idx, 'SCALE_X'].values[0]
            xsc = self.panel_scales_x[idx-1]

        if self.panel_scales_y:
            idx = self.layout.loc[bool_idx, 'SCALE_Y'].values[0]
            ysc = self.panel_scales_y[idx-1]

        return Bunch(x=xsc, y=ysc)

    def reset_position_scales(self):
        """
        Reset x and y scales
        """
        if not self.facet.shrink:
            return

        with suppress(AttributeError):
            self.panel_scales_x.reset()

        with suppress(AttributeError):
            self.panel_scales_y.reset()

    def setup_panel_params(self, coord):
        """
        Calculate the x & y range & breaks information for each panel

        Parameters
        ----------
        coord : coord
            Coordinate
        """
        if not self.panel_scales_x:
            raise PlotnineError('Missing an x scale')

        if not self.panel_scales_y:
            raise PlotnineError('Missing a y scale')

        self.panel_params = []
        cols = ['SCALE_X', 'SCALE_Y']
        for i, j in self.layout[cols].itertuples(index=False):
            i, j = i-1, j-1
            params = coord.setup_panel_params(
                self.panel_scales_x[i],
                self.panel_scales_y[j])
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

    def check_layout(self):
        required = {'PANEL', 'SCALE_X', 'SCALE_Y'}
        common = self.layout.columns.intersection(required)
        if len(required) != len(common):
            raise PlotnineError(
                "Facet layout has bad format. It must contain "
                "the columns '{}'".format(required))

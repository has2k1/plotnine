from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd

from .scales.scales import Scales
from .scales.scale import scale_continuous
from .utils import match, xy_panel_scales, is_waive


class Panel(object):
    # n = no. of visual panels
    layout = None     # table n rows, grid information

    # whether to shrink scales to fit
    # output of statistics, not raw data
    shrink = False

    ranges = None     # list of n dicts.
    x_scales = None   # scale object(s). 1 or n of them
    y_scales = None   # scale object(s). 1 or n of them

    def train_position(self, data, x_scale, y_scale):
        """
        Create all the required x_scales and y_scales
        and set the ranges for each scale according
        to the data
        """
        layout = self.layout
        # Initialise scales if needed, and possible.
        if not self.x_scales and x_scale:
            n = layout['SCALE_X'].max()
            self.x_scales = Scales([x_scale.clone() for i in range(n)])
        if not self.y_scales and y_scale:
            n = layout['SCALE_Y'].max()
            self.y_scales = Scales([y_scale.clone() for i in range(n)])

        # loop over each layer, training x and y scales in turn
        for layer_data in data:
            match_id = match(layer_data['PANEL'], layout['PANEL'])
            if x_scale:
                x_vars = list(set(x_scale.aesthetics) &
                              set(layer_data.columns))
                # the scale index for each data point
                SCALE_X = layout['SCALE_X'].iloc[match_id].tolist()
                self.x_scales.train(layer_data, x_vars, SCALE_X)

            if y_scale:
                y_vars = list(set(y_scale.aesthetics) &
                              set(layer_data.columns))
                # the scale index for each data point
                SCALE_Y = layout['SCALE_Y'].iloc[match_id].tolist()
                self.y_scales.train(layer_data, y_vars, SCALE_Y)
        return self

    def map_position(self, data, x_scale, y_scale):
        layout = self.layout

        for layer_data in data:
            match_id = match(layer_data['PANEL'], layout['PANEL'])
            if x_scale:
                x_vars = list(set(x_scale.aesthetics) &
                              set(layer_data.columns))
                SCALE_X = layout['SCALE_X'].iloc[match_id].tolist()
                self.x_scales.map(layer_data, x_vars, SCALE_X)

            if y_scale:
                y_vars = list(set(y_scale.aesthetics) &
                              set(layer_data.columns))
                SCALE_Y = layout['SCALE_Y'].iloc[match_id].tolist()
                self.y_scales.map(layer_data, y_vars, SCALE_Y)

        return data

    def panel_scales(self, i):
        """
        Return the x scale and y scale for panel i
        if they exist.
        """
        # wrapping with np.asarray prevents an exception
        # on some datasets !!!
        bool_idx = (np.asarray(self.layout['PANEL']) == i)
        xsc = None
        ysc = None

        if self.x_scales:
            idx = self.layout.loc[bool_idx, 'SCALE_X'].values[0]
            xsc = self.x_scales[idx-1]

        if self.y_scales:
            idx = self.layout.loc[bool_idx, 'SCALE_Y'].values[0]
            ysc = self.y_scales[idx-1]

        return xy_panel_scales(x=xsc, y=ysc)

    def calculate_stats(self, data, layers):
        """
        Calculate statistics

        Parameters
        ----------
        data :  list of dataframes
            one for each layer
        layers : list of layers

        Return
        ------
        data : list of dataframes
            dataframes with statistic columns
        """
        new_data = []

        def fn(panel_data, l):
            """
            For a specific panel with data 'panel_data',
            compute the statistics in layer 'l' and
            return the resulting dataframe
            """
            if len(panel_data) == 0:
                return pd.DataFrame()

            pscales = self.panel_scales(
                panel_data['PANEL'].as_matrix()[0])
            return l.calc_statistic(panel_data, pscales)

        # A dataframe in a layer can have rows split across
        # multiple panels(facets). For each layer and accompanying
        # data the statistics are calculated independently for
        # each panel.
        for (d, l) in zip(data, layers):
            df = d.groupby('PANEL').apply(fn, l)
            df.reset_index(drop=True, inplace=True)
            new_data.append(df)
        return new_data

    def reset_scales(self):
        """
        Reset x and y scales
        """
        if not self.shrink:
            return

        self.x_scales.reset()
        self.y_scales.reset()

    def train_ranges(self):
        """
        Calculate the x & y ranges for each panel
        """
        def compute_ranges(pos_scales):
            lst = []
            for sc in pos_scales:
                if sc._limits:
                    # NOTE: Should transform if/when scale.trans
                    # is enabled
                    rng = sc._limits
                elif is_waive(sc._expand):
                    if isinstance(sc, scale_continuous):
                        rng = sc.dimension((0.05, 0))
                    else:
                        # discrete scale
                        rng = sc.dimension((0, 0.6))
                else:
                    rng = sc.dimension(sc._expand)

                lst.append(rng)

            return lst

        self.ranges = [None] * len(self.layout)
        x_ranges = compute_ranges(self.x_scales)
        y_ranges = compute_ranges(self.y_scales)

        cols = ['PANEL', 'SCALE_X', 'SCALE_Y']
        for p, i, j in self.layout[cols].itertuples(index=False):
            self.ranges[p-1] = {'x': x_ranges[i-1],
                                'y': y_ranges[j-1]}

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd

from ..utils.exceptions import GgplotError
from ..utils import match, add_margins


def locate_wrap(data, panels, vars):
    if not len(data):
        data['PANEL'] = pd.Categorical([])
        data['PANEL'].cat.reorder_categories(panels['PANEL'].cat.categories)
        return data

    # The columns that are facetted
    vars_ = [v for v in vars if v in data.columns]
    facet_vals = data.loc[:, vars_].reset_index(drop=True)

    # When a dataframe a some layer does not have all
    # the facets variables, add the missing facet
    # variables and create new data where the points(duplicates)
    # are present in all the facets
    missing_facets = set(vars) - set(vars_)
    if missing_facets:
        to_add = panels.loc[:, missing_facets].drop_duplicates()
        to_add.reset_index(drop=True, inplace=True)

        # a point for each facet, [0, 1, ..., n-1, 0, 1, ..., n-1, ...]
        data_rep = np.tile(list(range(len(data))), len(to_add))
        # a facet for each point, [0, 0, 0, 1, 1, 1, ... n-1, n-1, n-1]
        facet_rep = np.repeat(list(range(len(to_add))), len(data))

        data = data.iloc[data_rep, :].reset_index(drop=True)
        facet_vals = facet_vals.iloc[data_rep, :].reset_index(drop=True)
        facet_vals.append(to_add.iloc[facet_rep, :])

    # assign each point to a panel
    keys_x = list(facet_vals.loc[:, vars].itertuples(index=False))
    keys_y = list(panels.loc[:, vars].itertuples(index=False))
    data['PANEL'] = match(keys_x, keys_y, start=1)

    # matching dtype
    data['PANEL'] = pd.Categorical(data['PANEL'])
    data['PANEL'].cat.reorder_categories(panels['PANEL'].cat.categories)
    data.sort(columns='PANEL', inplace=True)
    data.reset_index(drop=True, inplace=True)
    return data


def locate_grid(data, panels, rows=None, cols=None, margins=False):
    if not len(data):
        data['PANEL'] = pd.Categorical([])
        data['PANEL'].cat.reorder_categories(panels['PANEL'].cat.categories)
        return data
    vars = [x for x in rows + cols]

    rows = [] if rows is None else rows
    cols = [] if cols is None else cols
    margin_vars = [list(data.columns & rows),
                   list(data.columns & cols)]
    data = add_margins(data, margin_vars, margins)

    # The columns that are facetted
    vars_ = [v for v in vars if v in data.columns]
    facet_vals = data.loc[:, vars_].reset_index(drop=True)

    # When in a dataframe some layer does not have all
    # the facets variables, add the missing facet
    # variables and create new data where the points(duplicates)
    # are present in all the facets
    missing_facets = set(vars) - set(vars_)
    if missing_facets:
        to_add = panels.loc[:, missing_facets].drop_duplicates()
        to_add.reset_index(drop=True, inplace=True)

        # a point for each facet, [0, 1, ..., n-1, 0, 1, ..., n-1, ...]
        data_rep = np.tile(list(range(len(data))), len(to_add))
        # a facet for each point, [0, 0, 0, 1, 1, 1, ... n-1, n-1, n-1]
        facet_rep = np.repeat(list(range(len(to_add))), len(data))

        data = data.iloc[data_rep, :].reset_index(drop=True)
        facet_vals = facet_vals.iloc[data_rep, :].reset_index(drop=True)
        facet_vals.append(to_add.iloc[facet_rep, :])

    # assign each point to a panel
    if len(facet_vals) == 0:
        # Special case of no facetting
        data['PANEL'] = 1
    else:
        keys_x = list(facet_vals.loc[:, vars].itertuples(index=False))
        keys_y = list(panels.loc[:, vars].itertuples(index=False))
        data['PANEL'] = match(keys_x, keys_y, start=1)

    # matching dtype
    data['PANEL'] = pd.Categorical(data['PANEL'])
    data['PANEL'].cat.reorder_categories(panels['PANEL'].cat.categories)
    data.sort(columns='PANEL', inplace=True)
    data.reset_index(drop=True, inplace=True)
    return data

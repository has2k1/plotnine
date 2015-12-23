from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd

from ..utils import match, add_margins, join_keys


def locate_wrap(data, panels, vars):
    if not len(data):
        data['PANEL'] = pd.Categorical([])
        data['PANEL'].cat.reorder_categories(panels['PANEL'].cat.categories)
        return data

    data, facet_vals = add_missing_facets(data, panels, vars)

    # assign each point to a panel
    keys = join_keys(facet_vals, panels, vars)
    data['PANEL'] = match(keys['x'], keys['y'], start=1)

    # matching dtype
    data['PANEL'] = pd.Categorical(data['PANEL'])
    data['PANEL'].cat.reorder_categories(panels['PANEL'].cat.categories)
    data = data.sort_values('PANEL')
    data.reset_index(drop=True, inplace=True)
    return data


def locate_grid(data, panels, rows=None, cols=None, margins=False):
    if not len(data):
        data['PANEL'] = pd.Categorical([])
        data['PANEL'].cat.reorder_categories(panels['PANEL'].cat.categories)
        return data

    rows = [] if rows is None else rows
    cols = [] if cols is None else cols
    vars = [x for x in rows + cols]
    margin_vars = [list(data.columns & rows),
                   list(data.columns & cols)]
    data = add_margins(data, margin_vars, margins)
    data, facet_vals = add_missing_facets(data, panels, vars)

    # assign each point to a panel
    if len(facet_vals) == 0:
        # Special case of no facetting
        data['PANEL'] = 1
    else:
        keys = join_keys(facet_vals, panels, vars)
        data['PANEL'] = match(keys['x'], keys['y'], start=1)

    # matching dtype and
    # the categories(panel numbers) for the data should be in the
    # same order as the panels. i.e the panels are the reference, they "know"
    # the right order
    data['PANEL'] = pd.Categorical(data['PANEL'])
    ordered_categories = [c for c in panels['PANEL'].cat.categories
                          if c in data['PANEL'].cat.categories]
    data['PANEL'].cat.categories = ordered_categories
    data = data.sort_values('PANEL')
    data.reset_index(drop=True, inplace=True)
    return data


def add_missing_facets(data, panels, vars):
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
        data_rep = np.tile(np.arange(len(data)), len(to_add))
        # a facet for each point, [0, 0, 0, 1, 1, 1, ... n-1, n-1, n-1]
        facet_rep = np.repeat(np.arange(len(to_add)), len(data))

        data = data.iloc[data_rep, :].reset_index(drop=True)
        facet_vals = facet_vals.iloc[data_rep, :].reset_index(drop=True)
        to_add = to_add.iloc[facet_rep, :].reset_index(drop=True)
        facet_vals = pd.concat([facet_vals, to_add],
                               axis=1, ignore_index=False)

    return data, facet_vals

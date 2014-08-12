from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import itertools

import numpy as np
import pandas as pd

from ..utils.exceptions import GgplotError
from ..utils import ninteraction


def layout_null(data):
    return pd.DataFrame({'PANEL': pd.Categorical[1], 'ROW':  1, 'COL': 1})


def layout_wrap(data, vars=None, nrow=None, ncol=None,
                as_table=True, drop=True):
    """
    Layout panels in a 1d ribbon.

    Parameters
    ----------
    data : list
        list of dataframes with list[0] the default dataframe,
        list[1] dataframe for the 1st layer, ...
    vars : tuple | list
        facet variables
    nrow : int
        number of row
    ncol : int
        number of col
    as_table : bool
        d
    drop : bool
        Whether to exclude missing combinations of facet variables
        from the plot
    """
    if not vars:
        return layout_null(data)

    base = layout_base(data, vars, drop=drop)
    n = len(base)
    dims = wrap_dims(n, nrow, ncol)
    _id = np.arange(1, n+1)

    if as_table:
        row = (_id - 1) // dims[1] + 1
    else:
        row = dims[0] - (_id - 1) // dims[1]

    col = (_id - 1) % dims[1] + 1

    layout = pd.DataFrame({'PANEL': pd.Categorical(range(1, n+1)),
                           'ROW': row.astype(int),
                           'COL': col.astype(int)})
    panels = pd.concat([layout, base], axis=1)
    return panels


def layout_grid(data, rows=None, cols=None, margins=None,
                as_table=True, drop=True):
    """
    Layout panels in a 2d grid.

    Parameters
    ----------
    data : list
        list of dataframes with list[0] the default dataframe,
        list[1] dataframe for the 1st layer, ...
    rows : tuple | list
        number of row
    cols : tuple | list
        number of col
    as_table : bool
        d
    drop : bool
        Whether to exclude missing combinations of facet variables
        from the plot
    """
    if not rows and not cols:
        return layout_null(data)

    base_rows = layout_base(data, rows, drop=drop)
    if not as_table:
        # NOTE: This will only become effective when dataframes
        # have categorical columns and the columns have ordered levels.
        # layout_base above would return rows ordered according
        # to the levels of the facet variable

        # Reverse the order of the rows
        base_rows = base_rows.reindex(index=base_rows.index[::-1])
    base_cols = layout_base(data, cols, drop=drop)
    base = cross_join(base_rows, base_cols)

    if margins:
        # TODO: Implement this
        pass

    rows = 1 if rows is None else ninteraction(base[rows], drop=True)
    cols = 1 if cols is None else ninteraction(base[cols], drop=True)

    n = len(base)
    panels = pd.DataFrame({'PANEL': pd.Categorical(range(1, n+1)),
                           'ROW': rows,
                           'COL': cols})
    panels = pd.concat([panels, base], axis=1)
    return panels


def layout_base(data, vars=None, drop=True):
    """
    Base layout function that generates all combinations of data
    needed for facetting
    The first data frame in the list should be the default data
    for the plot. Other data frames in the list are ones that are
    added to the layers.
    """
    if not vars:
        return pd.DataFrame()

    # For each layer, compute the facet values
    values = []
    for df in data:
        if df is None:
            continue
        _lst = [x for x in vars if x in df]
        if _lst:
            values.append(df[_lst])

    # Form the base data frame which contains all combinations
    # of facetting variables that appear in the data
    has_all = [x.shape[1]==len(vars) for x in values]
    if not any(has_all):
        raise GgplotError(
            "At least one layer must contain all variables " +
            "used for facetting")
    base = pd.concat([x for i, x in enumerate(values) if has_all[i]],
                     axis=0)
    base.drop_duplicates(inplace=True)

    if not drop:
        base = unique_combs(base)

    # sorts according to order of factor levels
    base.sort(columns=list(base.columns), inplace=True)


    # Systematically add on missing combinations
    for i, value in enumerate(values):
        if has_all[i]:
            continue
        old = base.loc[:, base.columns - value.columns]
        new = value.loc[:, base.columns & value.columns].drop_duplicates()
        if not drop:
            new = unique_combs(new)
        base = base.append(cross_join(old, new), ignore_index=True)

    if len(base) == 0:
        raise GgplotError(
            "Faceting variables must have at least one value")

    base = base.reset_index(drop=True)
    return base


def unique_combs(df):
    """
    Return data frame with all possible combinations
    of the values in the columns
    """
    # A sliced copy with zero rows so as to
    # preserve the column dtypes
    _df = df.ix[0:-1, df.columns]

    # List of unique values from every column
    lst = map(lambda x: x.unique().tolist(), [df[c] for c in df])
    rows = itertools.product(*lst)
    for i, row in enumerate(rows):
        _df.loc[i] = row
    return _df


def cross_join(df1, df2):
    """
    Return a dataframe that is a cross between dataframes
    df1 and df2

    ref: https://github.com/pydata/pandas/issues/5401
    """
    # Add as lists so that the new index keeps the items in
    # the order that they are added together
    all_columns = pd.Index(list(df1.columns) + list(df2.columns))
    df1['key'] = 1
    df2['key'] = 1
    return pd.merge(df1, df2, on='key').loc[:, all_columns]


def wrap_dims(n, nrow=None, ncol=None):
    if not nrow and not ncol:
        nrow, ncol = n2mfrow(n)
    elif not ncol:
        ncol = int(np.ceil(n/nrow))
    elif not nrow:
        nrow = int(np.ceil(n/ncol))
    if not nrow * ncol >= n:
        raise GgplotError(
            'Allocated fewer panels than are required')
    return (nrow, ncol)


def n2mfrow(nr_plots):
    """
    Compute the rows and columns given the number
    of plots.

    This is a port of grDevices::n2mfrow from R
    """
    if nr_plots <= 3:
        nrow, ncol =  nr_plots, 1
    elif nr_plots <= 6:
        nrow, ncol = (nr_plots + 1) // 2, 2
    elif nr_plots <= 12:
        nrow, ncol = (nr.plots + 2) // 3, 3
    else:
        nrow = int(np.ceil(np.sqrt(nr_plots)))
        ncol = int(np.ceil(nr_plots/nrow))
    return (nrow, ncol)

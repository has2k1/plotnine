"""
Little functions used all over the codebase
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import itertools

import numpy as np
import pandas as pd
import pandas.core.common as com
import matplotlib.cbook as cbook
import six


discrete_dtypes = {'category', np.dtype('O'), np.bool}
continuous_dtypes = {np.number,
                     np.dtype('int16'), np.dtype('float16'),
                     np.dtype('int32'), np.dtype('float32'),
                     np.dtype('int64'), np.dtype('float64')}


def pop(dataframe, key, default):
    """
    Pop element *key* from dataframe and return it. Return default
    if it *key* not in dataframe
    """
    try:
        value = dataframe.pop(key)
    except KeyError:
        value = default
    return value


def is_scalar_or_string(val):
    """
    Return whether the given object is a scalar or string like.
    """
    return is_string(val) or not cbook.iterable(val)


def is_string(obj):
    """
    Return True if *obj* is a string
    """
    if isinstance(obj, six.string_types):
        return True
    return False


def is_sequence_of_strings(obj):
    """
    Returns true if *obj* is iterable and contains strings
    """
    # Note: cbook.is_sequence_of_strings has a bug because
    # a numpy array of strings is recognized as being
    # string_like and therefore not a sequence of strings
    if not cbook.iterable(obj):
        return False
    if not isinstance(obj, np.ndarray) and cbook.is_string_like(obj):
        return False
    for o in obj:
        if not cbook.is_string_like(o):
            return False
    return True


def is_sequence_of_booleans(obj):
    """
    Return True if *obj* is array-like and contains boolean values
    """
    if not cbook.iterable(obj):
        return False
    _it = (isinstance(x, bool) for x in obj)
    if all(_it):
        return True
    return False


def is_categorical(obj):
    """
    Return True if *obj* is array-like and has categorical values

    Categorical values include:
        - strings
        - booleans
    """
    if is_sequence_of_strings(obj):
        return True
    if is_sequence_of_booleans(obj):
        return True
    return False


def make_iterable(val):
    """
    Return [*val*] if *val* is not iterable

    Strings are not recognized as iterables
    """
    if cbook.iterable(val) and not is_string(val):
        return val
    return [val]


def make_iterable_ntimes(val, n):
    """
    Return [*val*, *val*, ...] if *val* is not iterable.

    If *val* is an iterable of length n, it is returned as is.
    Strings are not recognized as iterables

    Raises an exception if *val* is an iterable but has length
    not equal to n
    """
    if cbook.iterable(val) and not is_string(val):
        if len(val) != n:
            raise Exception(

                '`val` is an iterable of length not equal to n.')
        return val
    return [val] * n


_waiver_ = object()
def waiver(param=None):
    """
    When no parameter is passed, return an object to imply 'default'.
    When a parameter is passed, return True if that object implies use
    default and False otherwise.
    """
    if param is None:
        return _waiver_
    else:
        return param is _waiver_


def identity(*args):
    """
    Return whatever is passed in
    """
    return args if len(args) > 1 else args[0]


def match(v1, v2, nomatch=-1, incomparables=None, start=0):
    """
    Return a vector of the positions of (first)
    matches of its first argument in its second.

    Parameters
    ----------
    v1: array-like
        the values to be matched

    v2: array-like
        the values to be matched against

    nomatch: int
        the value to be returned in the case when
        no match is found.

    incomparables: array-like
        a list of values that cannot be matched.
        Any value in v1 matching a value in this list
        is assigned the nomatch value.
    start: int
        type of indexing to use. Most likely 0 or 1
    """
    lookup = {}
    for i, x in enumerate(v2):
        if not (x in lookup):
            lookup[x] = i

    lst = [nomatch] * len(v1)
    skip = set(incomparables) if incomparables else set()
    for i, x in enumerate(v1):
        if x in skip:
            continue
        try:
            lst[i] = lookup[x] + start
        except KeyError:
            pass
    return lst


def _margins(vars, margins=True):
    """
    Figure out margining variables.

    Given the variables that form the rows and
    columns, and a set of desired margins, works
    out which ones are possible. Variables that
    can't be margined over are dropped silently.

    Parameters
    ----------
    vars : list
        variable names for rows and columns
    margins : bool | list
        If true, margins over all vars, otherwise
        only those listed

    Return
    ------
    out : list
        All the margins to create.
    """
    if margins == False:
        return []

    def fn(_vars):
        "The margin variables for a given row or column"
        # The first item is and empty list for no margins
        dim_margins = [[]]
        # for each wanted variable, couple it with
        # all variables to the right
        for i, u in enumerate(_vars):
            if margins == True or u in margins:
                lst = [u] + [v for v in _vars[i+1:]]
                dim_margins.append(lst)
        return dim_margins

    # Margin variables for rows and columns
    row_margins = fn(vars[0])
    col_margins = fn(vars[1])

    # Cross the two
    lst = list(itertools.product(col_margins, row_margins))

    # Clean up -- merge the row and column variables
    pretty = []
    for c, r in lst:
        pretty.append(r + c)
    return pretty


def add_margins(df, vars, margins=True):
    """
    Add margins to a data frame.

    All margining variables will be converted to factors.

    Parameters
    ----------
    df : dataframe
        input data frame

    vars : list
        a list of 2 lists | tuples vectors giving the
        variables in each dimension

    margins : bool | list
        variable names to compute margins for.
        True will compute all possible margins.
    """
    margin_vars = _margins(vars, margins)
    if not margin_vars:
        return df

    # all margin columns become categoricals
    all_vars = set([v for vlst in margin_vars for v in vlst])
    for v in all_vars:
        df[v] = pd.Categorical(df[v])
        levels = df[v].cat.levels.tolist() + ['(all)']
        try:
            df[v].cat.reorder_levels(levels)
        except ValueError:
            # Already a categorical with '(all)' level
            pass

    # create margin dataframes
    margin_dfs = [df]
    for vlst in margin_vars[1:]:
        dfx = df.copy()
        for v in vlst:
            dfx.loc[0:, v] = '(all)'
        margin_dfs.append(dfx)

    merged = pd.concat(margin_dfs, axis=0)
    merged.reset_index(drop=True, inplace=True)
    return merged


def ninteraction(df, drop=False):
    """
    Compute a unique numeric id for each unique row in
    a data frame. The ids start at 1 -- in the spirit
    of `plyr::id`

    Parameters
    ----------
    df : dataframe
    columns : list
        The columns to consider for uniquness. If None, then
        it is all the columns

    Note
    ----
    So far there has been no need not to drop unused levels
    of categorical variables.
    """
    if len(df) == 0:
        return []

    # Special case for single variable
    if len(df) == 1:
        return _id_var(df, drop)

    # Calculate individual ids
    ids = df.apply(_id_var, axis=0)
    ids = ids.reindex(columns=reversed(ids.columns))
    p = ids.shape[1]

    # Calculate dimensions
    len_unique = lambda x: len(np.unique(x))
    ndistinct = ids.apply(len_unique, axis=0).as_matrix()
    n = ndistinct.prod()

    combs = np.matrix(
        np.hstack([1, ndistinct[:-1]]))
    mat = np.matrix(ids)
    res = (mat - 1) * combs.T + 1
    res = np.array(res).flatten().tolist()

    if drop:
        return _id_var(res, drop)
    else:
        return res


def _id_var(x, drop=False):
    if len(x) == 0:
        return []

    if com.is_categorical_dtype(x) and not drop:
        x = x.copy()
        x.cat.levels = range(1, len(x.cat.levels) + 1)
        lst = x.tolist()
    else:
        levels = np.sort(np.unique(x))
        lst = match(x, levels)
        lst = [item + 1 for item in lst]

    return lst

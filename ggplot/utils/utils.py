"""
Little functions used all over the codebase
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import collections
import itertools
import re
import importlib
import contextlib
import inspect

import six
import numpy as np
import pandas as pd
import pandas.core.common as com
import matplotlib as mpl
import matplotlib.cbook as cbook
from matplotlib.colors import colorConverter
from matplotlib.offsetbox import DrawingArea
from matplotlib.patches import Rectangle

from .exceptions import GgplotError, gg_warn


DISCRETE_KINDS = 'Ob'
CONTINUOUS_KINDS = 'if'

# The x scale and y scale of a panel. Each may be None
xy_panel_scales = collections.namedtuple('xy_panel_scales', 'x y')


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
    if cbook.is_string_like(obj) and not isinstance(obj, np.ndarray):
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
    return all(isinstance(o, bool) for o in obj)


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
            raise GgplotError(
                '`val` is an iterable of length not equal to n.')
        return val
    return [val] * n


class _waiver(object):
    def __repr__(self):
        return 'waiver()'

    def __deepcopy__(self, memo):
        return self


_waiver_ = _waiver()


def waiver():
    """
    Return an object to imply 'default'.
    """
    return _waiver_


def is_waive(x):
    """
    Return True if x object implies use
    default and False otherwise.
    """
    return x is _waiver_


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
        if x not in lookup:
            lookup[x] = i

    lst = [nomatch] * len(v1)
    skip = set(incomparables) if incomparables else set()
    for i, x in enumerate(v1):
        if x in skip:
            continue

        with suppress(KeyError):
            lst[i] = lookup[x] + start

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
    if margins is False:
        return []

    def fn(_vars):
        "The margin variables for a given row or column"
        # The first item is and empty list for no margins
        dim_margins = [[]]
        # for each wanted variable, couple it with
        # all variables to the right
        for i, u in enumerate(_vars):
            if margins is True or u in margins:
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
        try:
            df[v].cat.add_categories('(all)', inplace=True)
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

    # Calculate dimensions
    def len_unique(x):
        return len(np.unique(x))
    ndistinct = ids.apply(len_unique, axis=0).as_matrix()

    combs = np.matrix(
        np.hstack([1, np.cumprod(ndistinct[:-1])]))
    mat = np.matrix(ids)
    res = (mat - 1) * combs.T + 1
    res = np.array(res).flatten().tolist()

    if drop:
        return _id_var(res, drop)
    else:
        return res


def _id_var(x, drop=False):
    """
    Assign ids to items in x. If two items
    are the same, they get the same id.

    Parameters
    ----------
    x : array-like
        items to associate ids with
    drop : bool
        Whether to drop unused factor levels
    """
    if len(x) == 0:
        return []

    if com.is_categorical_dtype(x) and not drop:
        x = x.copy()
        x.cat.categories = range(1, len(x.cat.categories) + 1)
        lst = x.tolist()
    else:
        levels = np.sort(np.unique(x))
        lst = match(x, levels)
        lst = [item + 1 for item in lst]

    return lst


def check_required_aesthetics(required, present, name):
    missing_aes = set(required) - set(present)

    if missing_aes:
        msg = '{} requires the following missing aesthetics: {}'
        raise GgplotError(
            msg.format(name, ', '.join(missing_aes)))


def uniquecols(df):
    """
    Return unique columns

    This is used for figuring out which columns are
    constant within a group
    """
    bool_idx = df.apply(lambda col: len(np.unique(col)) == 1, axis=0)
    df = df.loc[:, bool_idx].iloc[0:1, :].reset_index(drop=True)
    return df


def defaults(d1, d2):
    """
    Update d1 with the contents of d2 that are not in d1.
    d1 and d2 are dictionary like objects.

    Parameters
    ----------
    d1 : dict | dataframe
    d2 : dict | dataframe

    Returns
    -------
    out : dict | dataframe
        type of d1
    """
    tolist = isinstance(d2, pd.DataFrame)
    for k in (set(d2.keys()) - set(d1.keys())):
        if tolist:
            d1[k] = d2[k].tolist()
        else:
            d1[k] = d2[k]

    return d1


def jitter(x, factor=1, amount=None):
    """
    Add a small amount of noise to values in an array_like
    """
    if len(x) == 0:
        return x

    x = np.asarray(x)

    try:
        z = np.ptp(x[np.isfinite(x)])
    except IndexError:
        z = 0

    if z == 0:
        z = np.abs(np.min(x))
    if z == 0:
        z = 1

    if amount is None:
        _x = np.round(x, 3-np.int(np.floor(np.log10(z)))).astype(np.int)
        xx = np.unique(np.sort(_x))
        d = np.diff(xx)
        if len(d):
            d = d.min()
        elif xx != 0:
            d = xx/10.
        else:
            d = z/10
        amount = factor/5. * abs(d)
    elif amount == 0:
        amount = factor * (z / 50.)

    return x + np.random.uniform(-amount, amount, len(x))


def gg_import(name):
    """
    Import and return ggplot component type.

    The understood components are of base classes the
    following base classes: geom, stat, scale, position, guide

    Raises an exception if the component is not understood.
    """
    # relative pathnames from this package
    lookup = {'geom': '..geoms',
              'stat': '..stats',
              'scale': '..scales',
              'position': '..positions',
              'guide': '..guides',
              'trans': '..scales.utils'}
    patterns = [re.compile('([a-z]+)_'),
                re.compile('_(trans)$')]
    base = None
    for p in patterns:
        match = re.search(p, name)
        if match and match.group(1) in lookup:
            base = match.group(1)
            break
    else:
        raise GgplotError("Cannot recognize '{}'".format(name))

    try:
        package = importlib.import_module(lookup[base], __package__)
    except ImportError:
        raise GgplotError("Failed to import '{}'".format(name))

    try:
        obj = getattr(package, name)
    except AttributeError:
        msg = "{} has no attribute '{}'"
        raise GgplotError(msg.format(package, name))
    return obj


def remove_missing(df, na_rm=False, vars=None, name='', finite=False):
    """
    Convenience function to remove missing values from a dataframe

    Parameters
    ----------
    df : dataframe
    na_rm : bool
        If False remove all non-complete rows with and show warning.
    vars : list-like
        columns to act on
    name : str
        Name of calling method for a more informative message
    finite : bool
        If True replace the infinite values in addition to the NaNs
    """
    n = len(df)

    if vars is None:
        vars = df.columns
    else:
        vars = [v for v in vars if v in df.columns]

    if finite:
        lst = [np.inf, -np.inf]
        to_replace = {v: lst for v in vars}
        df.replace(to_replace, np.nan, inplace=True)
        txt = 'non-finite'
    else:
        txt = 'missing'

    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    if len(df) < n and not na_rm:
        msg = '{} : Removed {} rows containing {} values.'
        gg_warn(msg.format(name, n-len(df), txt), stacklevel=3)
    return df


def round_any(x, accuracy, f=np.round):
    """
    Round to multiple of any number.
    """
    return f(x / accuracy) * accuracy


def seq(fromm=1, to=1, by=1, length_out=None):
    """
    Generate regular sequences

    Parameters
    ----------
    fromm : numeric
        start of the sequence.
    to : numeric
        end of the sequence.
    by : numeric
        increment of the sequence.
    length_out : int
        length of the sequence. If a float is supplied, it
        will be rounded up

    Meant to be the same as Rs seq to prevent
    discrepancies at the margins
    """
    if length_out is not None:
        if length_out < 0:
            raise GgplotError('length_out must be non-negative number')
        by = (to - fromm)/(np.ceil(length_out)-1)

    x = np.arange(fromm, to+by, by)
    if x[-1] > to:
        x = x[:-1]
    return x


def to_rgba(colors, alpha):
    """
    Covert hex colors to rgba values.

    Parameters
    ----------
    colors : iterable | str
        colors to convert
    alphas : iterable | float
        alpha values

    Returns
    -------
    out : ndarray | tuple
        rgba color(s)

    Note
    ----
    Matplotlib plotting functions only accept scalar
    alpha values. Hence no two objects with different
    alpha values may be plotted in one call. This would
    make plots with continuous alpha values innefficient.
    However :), the colors can be rgba list-likes and
    the alpha dimension will be respected.
    """
    if colors is None or colors == '':
        return colors

    def is_iterable(var):
        return cbook.iterable(var) and not is_string(var)

    cc = colorConverter
    if is_iterable(colors) and not is_iterable(alpha):
        return cc.to_rgba_array(colors, alpha)
    elif is_iterable(colors) and is_iterable(alpha):
        return [cc.to_rgba(c, a) for c, a in zip(colors, alpha)]
    elif not is_iterable(colors) and is_iterable(alpha):
        return [cc.to_rgba(colors, a) for a in alpha]
    else:  # not is_iterable(colors) and not is_iterable(alpha)
        return cc.to_rgba(colors, alpha)


def groupby_apply(df, cols, func, *args, **kwargs):
    """
    Groupby cols and call the function fn on each grouped dataframe.

    Parameters
    ----------
    cols : str | list of str
        columns to groupby
    func : function
        function to call on the grouped data
    *args : tuple
        positional parameters to pass to func
    **kwargs : dict
        keyword parameter to pass to func

    This is meant to avoid pandas df.groupby('col').apply(fn, *args),
    as it calls fn twice on the first dataframe. If the nested code also
    does the same thing, it can be very expensive
    """
    try:
        axis = kwargs.pop('axis')
    except KeyError:
        axis = 0

    lst = []
    for _, d in df.groupby(cols):
        # function fn should be free to modify dataframe d, therefore
        # do not mark d as a slice of df i.e no SettingWithCopyWarning
        d.is_copy = None
        lst.append(func(d, *args, **kwargs))
    return pd.concat(lst, axis=axis, ignore_index=True)


def make_line_segments(x, y, ispath=True):
    """
    Return an (n x 2 x 2) array of line segments

    Parameters
    ----------
    x : array-like
        x points
    y : array-like
        y points
    ispath : bool
        If True, the points represent a path from one point
        to the next until the last. If False, then each pair
        of successive(even-odd pair) points yields a line.
    """
    if ispath:
        num_segments = len(x)-1
        xs = [None] * (2*num_segments)
        ys = [None] * (2*num_segments)
        xs[::2], xs[1::2] = x[:-1], x[1:]
        ys[::2], ys[1::2] = y[:-1], y[1:]
    else:
        if len(x) % 2:
            raise GgplotError("Expects an even number of points")
        num_segments = len(x) // 2
        xs, ys = x, y
    segments = np.array(list(zip(xs, ys)))
    segments = segments.reshape(num_segments, 2, 2)
    return segments


class ColoredDrawingArea(DrawingArea):
    """
    A Drawing Area with a background color
    """
    def __init__(self, width, height, xdescent=0.0, ydescent=0.0,
                 clip=True, color='none'):

        super(ColoredDrawingArea, self).__init__(
            width, height, xdescent, ydescent, clip=clip)

        self.patch = Rectangle((0, 0), width=width,
                               height=height,
                               facecolor=color,
                               edgecolor='None',
                               linewidth=0,
                               antialiased=False)
        self.add_artist(self.patch)


@contextlib.contextmanager
def suppress(*exceptions):
    """
    Return a context manager that suppresses any of the
    specified exceptions if they occur in the body of a
    with statement and then resumes execution with the
    first statement following the end of the with statement.

    From python 3.4
    """
    try:
        yield
    except exceptions:
        pass


def copy_keys(source, destination, keys=None):
    """
    Add keys in source to destination

    Parameters
    ----------
    source : dict

    destination: dict

    keys : None | iterable
        The keys in source to be copied into destination. If
        None, then `keys = destination.keys()`
    """
    if keys is None:
        keys = destination.keys()
    for k in set(source) & set(keys):
        destination[k] = source[k]
    return destination


class RegisteredMeta(type):
    """
    Creates class that automatically registers all subclasses

    The subclasses are held in the `registry` attribute of the
    class. This is a `dict` of the form {name: class} and it
    is accessed as `createdclass.registry`
    """

    def __init__(cls, name, bases, dct):
        if not hasattr(cls, 'registry'):
            cls.registry = {}
        else:
            cls.registry[name] = cls
        super(RegisteredMeta, cls).__init__(name, bases, dct)


def get_kwarg_names(func):
    """
    Return a list of valid kwargs to function func
    """
    kwarg_names = []
    args, _, _, defaults = inspect.getargspec(func)
    if defaults:
        kwarg_names = args[:-len(defaults)]
    return kwarg_names


def get_valid_kwargs(func, potential_kwargs):
    """
    Return valid kwargs to function func
    """
    kwargs = {}
    for name in get_kwarg_names(func):
        with suppress(KeyError):
            kwargs[name] = potential_kwargs[name]
    return kwargs

"""
Little functions used all over the codebase
"""
from __future__ import annotations

import collections
import inspect
import itertools
import typing
import warnings
from contextlib import suppress
from warnings import warn
from weakref import WeakValueDictionary

import numpy as np
import pandas as pd

# missing in type stubs
from pandas.core.groupby import DataFrameGroupBy  # type: ignore

from .exceptions import PlotnineError, PlotnineWarning
from .mapping import aes

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Sequence

    import numpy.typing as npt
    from IPython.core.interactiveshell import InteractiveShell
    from typing_extensions import TypeGuard

    from plotnine.typing import DataLike, FloatArray, FloatArrayLike, IntArray


# Points and lines of equal size should give the
# same visual diameter (for points) and thickness
# (for lines). Given the adjustments in geom_point,
# this factor gives us the match.
SIZE_FACTOR = np.sqrt(np.pi)


def is_scalar_or_string(val):
    """
    Return whether the given object is a scalar or string like.
    """
    return is_string(val) or not np.iterable(val)


def is_string(obj: Any) -> TypeGuard[str]:
    """
    Return True if *obj* is a string
    """
    return isinstance(obj, str)


def is_list_like(obj: Any) -> bool:
    """
    Return True if *obj* is a list, tuple, series or array
    """
    return isinstance(obj, (list, tuple, pd.Series, np.ndarray))


def identity(*args: Any) -> Any:
    """
    Return whatever is passed in
    """
    return args if len(args) > 1 else args[0]


def match(
    v1, v2, nomatch=-1, incomparables=None, start=0
) -> npt.NDArray[np.int64]:
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
    # NOTE: This function gets called a lot. If it can
    # be optimised, it should.
    lookup = {}
    for i, x in enumerate(v2):
        if x not in lookup:
            lookup[x] = i

    if incomparables:
        skip = set(incomparables) if incomparables else set()
        lst = [
            lookup[x] + start if x not in skip and x in lookup else nomatch
            for x in v1
        ]
    else:
        lst = [lookup[x] + start if x in lookup else nomatch for x in v1]
    return np.array(lst)


def _margins(
    vars: tuple[list[str], list[str]], margins: bool | list[str] = True
):
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
                lst = [u] + list(_vars[i + 1 :])
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


def add_margins(
    df: pd.DataFrame,
    vars: tuple[list[str], list[str]],
    margins: bool | list[str] = True,
) -> pd.DataFrame:
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

    # create margin dataframes
    margin_dfs = [df]
    for vlst in margin_vars[1:]:
        dfx = df.copy()
        for v in vlst:
            dfx.loc[0:, v] = "(all)"
        margin_dfs.append(dfx)

    merged = pd.concat(margin_dfs, axis=0)
    merged.reset_index(drop=True, inplace=True)

    # All margin columns become categoricals. The margin indicator
    # (all) needs to be added as the last level of the categories.
    categories = {}
    for v in itertools.chain(*vars):
        col = df[v]
        if not isinstance(df[v].dtype, pd.CategoricalDtype):
            col = pd.Categorical(df[v])
        categories[v] = col.categories
        if "(all)" not in categories[v]:
            categories[v] = categories[v].insert(len(categories[v]), "(all)")

    for v in merged.columns.intersection(list(categories.keys())):
        merged[v] = merged[v].astype(pd.CategoricalDtype(categories[v]))

    return merged


def ninteraction(df: pd.DataFrame, drop: bool = False) -> list[int]:
    """
    Compute a unique numeric id for each unique row in
    a data frame. The ids start at 1 -- in the spirit
    of `plyr::id`

    Parameters
    ----------
    df : dataframe
        Rows
    drop : bool
        If true, drop unused categorical levels leaving no
        gaps in the assignments.

    Returns
    -------
    out : list
        Row asssignments.

    Notes
    -----
    So far there has been no need not to drop unused levels
    of categorical variables.
    """
    if len(df) == 0:
        return []

    # Special case for single variable
    if len(df.columns) == 1:
        return _id_var(df[df.columns[0]], drop)

    # Calculate individual ids
    ids = df.apply(_id_var, axis=0)
    ids = ids.reindex(columns=list(reversed(ids.columns)))

    # Calculate dimensions
    def len_unique(x):
        return len(np.unique(x))

    ndistinct: IntArray = ids.apply(len_unique, axis=0).to_numpy()

    combs = np.array(np.hstack([1, np.cumprod(ndistinct[:-1])]))
    mat = np.array(ids)
    res = (mat - 1) @ combs.T + 1
    res = np.array(res).flatten().tolist()

    if drop:
        return _id_var(res, drop)
    else:
        return list(res)


def _id_var(x: pd.Series[Any], drop: bool = False) -> list[int]:
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

    if array_kind.categorical(x):
        if drop:
            x = x.cat.remove_unused_categories()
            lst = list(x.cat.codes + 1)
        else:
            has_nan = any(np.isnan(i) for i in x if isinstance(i, float))
            if has_nan:
                # NaNs are -1, we give them the highest code
                nan_code = -1
                new_nan_code = np.max(x.cat.codes) + 1
                lst = [val if val != nan_code else new_nan_code for val in x]
            else:
                lst = list(x.cat.codes + 1)
    else:
        try:
            levels = sorted(set(x))
        except TypeError:
            from mizani.utils import multitype_sort

            # x probably has NANs
            levels = multitype_sort(set(x))

        lst = match(x, levels)
        lst = [item + 1 for item in lst]

    return lst


def join_keys(x, y, by=None):
    """
    Join keys.

    Given two data frames, create a unique key for each row.

    Parameters
    -----------
    x : dataframe
    y : dataframe
    by : list-like
        Column names to join by

    Returns
    -------
    out : dict
        Dictionary with keys x and y. The values of both keys
        are arrays with integer elements. Identical rows in
        x and y dataframes would have the same key in the
        output. The key elements start at 1.
    """
    if by is None:
        by = slice(None, None, None)

    if isinstance(by, tuple):
        by = list(by)

    joint = pd.concat([x[by], y[by]], ignore_index=True)
    keys = ninteraction(joint, drop=True)
    keys = np.asarray(keys)
    nx, ny = len(x), len(y)
    return {"x": keys[np.arange(nx)], "y": keys[nx + np.arange(ny)]}


def check_required_aesthetics(required, present, name):
    missing_aes = set(required) - set(present)

    if missing_aes:
        msg = "{} requires the following missing aesthetics: {}"
        raise PlotnineError(msg.format(name, ", ".join(missing_aes)))


def uniquecols(df):
    """
    Return unique columns

    This is used for figuring out which columns are
    constant within a group
    """
    bool_idx = df.apply(lambda col: len(np.unique(col)) == 1, axis=0)
    df = df.loc[:, bool_idx].iloc[0:1, :].reset_index(drop=True)
    return df


def jitter(x, factor=1, amount=None, random_state=None):
    """
    Add a small amount of noise to values in an array_like

    Parameters
    ----------
    x : array_like
        Values to apply a jitter
    factor : float
        Multiplicative value to used in automatically determining
        the `amount`. If the `amount` is given then the `factor`
        has no effect.
    amount : float
        This defines the range ([-amount, amount]) of the jitter to
        apply to the values. If `0` then ``amount = factor * z/50``.
        If `None` then ``amount = factor * d/5``, where d is about
        the smallest difference between `x` values and `z` is the
        range of the `x` values.
    random_state : int or ~numpy.random.RandomState, optional
        Seed or Random number generator to use. If ``None``, then
        numpy global generator :class:`numpy.random` is used.

    References:

        - Chambers, J. M., Cleveland, W. S., Kleiner, B. and Tukey,
          P.A. (1983) *Graphical Methods for Data Analysis*. Wadsworth;
          figures 2.8, 4.22, 5.4.
    """
    if len(x) == 0:
        return x

    if random_state is None:
        random_state = np.random
    elif isinstance(random_state, int):
        random_state = np.random.RandomState(random_state)

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
        _x = np.round(x, 3 - int(np.floor(np.log10(z)))).astype(int)
        xx = np.unique(np.sort(_x))
        d = np.diff(xx)
        if len(d):
            d = d.min()
        elif xx != 0:
            d = xx / 10.0
        else:
            d = z / 10
        amount = factor / 5.0 * abs(d)
    elif amount == 0:
        amount = factor * (z / 50.0)

    return x + random_state.uniform(-amount, amount, len(x))


def remove_missing(
    df: pd.DataFrame,
    na_rm: bool = False,
    vars: Sequence[str] | None = None,
    name: str = "",
    finite: bool = False,
) -> pd.DataFrame:
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
        vars = df.columns.to_list()
    else:
        vars = df.columns.intersection(list(vars)).to_list()

    if finite:
        lst = [np.inf, -np.inf]
        to_replace = {v: lst for v in vars}
        df.replace(to_replace, np.nan, inplace=True)
        txt = "non-finite"
    else:
        txt = "missing"

    df = df.dropna(subset=vars)
    df.reset_index(drop=True, inplace=True)
    if len(df) < n and not na_rm:
        msg = "{} : Removed {} rows containing {} values."
        warn(msg.format(name, n - len(df), txt), PlotnineWarning, stacklevel=3)
    return df


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

    Notes
    -----
    Matplotlib plotting functions only accept scalar
    alpha values. Hence no two objects with different
    alpha values may be plotted in one call. This would
    make plots with continuous alpha values innefficient.
    However :), the colors can be rgba hex values or
    list-likes and the alpha dimension will be respected.
    """

    def is_iterable(var):
        return np.iterable(var) and not is_string(var)

    def has_alpha(c):
        if isinstance(c, tuple):
            if len(c) == 4:
                return True
        elif isinstance(c, str):
            if c[0] == "#" and len(c) == 9:
                return True
        return False

    def no_color(c):
        return c is None or c == "" or c.lower() == "none"

    def to_rgba_hex(c, a):
        """
        Conver rgb color to rgba hex value

        If color c has an alpha channel, then alpha value
        a is ignored
        """
        from matplotlib.colors import colorConverter, to_hex

        if c in ("None", "none"):
            return c

        _has_alpha = has_alpha(c)
        c = to_hex(c, keep_alpha=_has_alpha)

        if not _has_alpha:
            arr = colorConverter.to_rgba(c, a)
            return to_hex(arr, keep_alpha=True)

        return c

    if is_iterable(colors):
        if all(no_color(c) for c in colors):
            return "none"

        if is_iterable(alpha):
            return [to_rgba_hex(c, a) for c, a in zip(colors, alpha)]
        else:
            return [to_rgba_hex(c, alpha) for c in colors]
    else:
        if no_color(colors):
            return colors
        if is_iterable(alpha):
            return [to_rgba_hex(colors, a) for a in alpha]
        else:
            return to_rgba_hex(colors, alpha)


def groupby_apply(
    df: pd.DataFrame,
    cols: str | list[str],
    func: Callable[..., pd.DataFrame],
    *args: tuple[Any],
    **kwargs: Any,
) -> pd.DataFrame:
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
    if df.empty:
        return df.copy()

    try:
        axis = kwargs.pop("axis")
    except KeyError:
        axis = 0

    lst = []
    for _, d in df.groupby(cols, observed=True):
        # function fn should be free to modify dataframe d, therefore
        # do not mark d as a slice of df i.e no SettingWithCopyWarning
        lst.append(func(d, *args, **kwargs))
    return pd.concat(lst, axis=axis, ignore_index=True)


def pivot_apply(df, column, index, func, *args, **kwargs):
    """
    Apply a function to each group of a column

    The function is kind of equivalent to R's *tapply*.

    Parameters
    ----------
    df : dataframe
        Dataframe to be pivoted
    column : str
        Column to apply function to.
    index : str
        Column that will be grouped on (and whose unique values
        will make up the index of the returned dataframe)
    func : function
        Function to apply to each column group. It *should* return
        a single value.
    *args : tuple
        Arguments to ``func``
    **kwargs : dict
        Keyword arguments to ``func``

    Returns
    -------
    out : dataframe
        Dataframe with index ``index`` and column ``column`` of
        computed/aggregate values .
    """

    def _func(x):
        return func(x, *args, **kwargs)

    return df.pivot_table(column, index, aggfunc=_func)[column]


def make_line_segments(
    x: FloatArrayLike, y: FloatArrayLike, ispath=True
) -> FloatArray:
    """
    Return an (n x 2 x 2) array of n line segments

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
    # Series objects would otherwise require .iloc
    x = np.asarray(x)
    y = np.asarray(y)
    if ispath:
        x = interleave(x[:-1], x[1:])
        y = interleave(y[:-1], y[1:])
    elif len(x) % 2:
        raise PlotnineError("Expects an even number of points")

    n = len(x) // 2
    segments = np.reshape(list(zip(x, y)), [n, 2, 2])
    return segments


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


class RegistryMeta(type):
    """
    Make a metaclass scriptable
    """

    _registry: WeakValueDictionary[str, Any] = WeakValueDictionary()

    # In here "self" refers to the meta class although it is never
    # instantiated
    def __getitem__(self, key):
        try:
            return self._registry[key]
        except KeyError:
            msg = (
                "'{}' Not in Registry. Make sure the module in "
                "which it is defined has been imported."
            )
            raise PlotnineError(msg.format(key))

    def __setitem__(self, key, value):
        self._registry[key] = value

    def __iter__(self):
        return self._registry.__iter__()

    def keys(self):
        return self._registry.keys()

    def values(self):
        return self._registry.values()

    def items(self):
        return self._registry.items()


class Registry(type, metaclass=RegistryMeta):
    """
    Creates class that automatically registers all subclasses

    To prevent the base class from showing up in the registry,
    it should have an attribute `__base__ = True`. This metaclass
    uses a single dictionary to register all types of subclasses.

    To access the registered objects, use:

        obj = Registry['name']

    To explicitly register objects

        Registry['name'] = obj

    Notes
    -----
    When objects are deleted, they are automatically removed
    from the Registry.
    """

    # namespace is of the class that subclasses Registry (or a
    # subclasses a subclass of Registry, ...) being created
    # e.g. geom, geom_point, ...
    def __new__(cls, name, bases, namespace):
        sub_cls = super().__new__(cls, name, bases, namespace)
        if not namespace.pop("__base__", False):
            cls._registry[name] = sub_cls
        return sub_cls


class RegistryHierarchyMeta(type):
    """
    Create a class that registers subclasses and the Hierarchy

    The class has gets two properties:

    1. ``_registry`` a dictionary of all the subclasses of the
       base class. The keys are the names of the classes and
       the values are the class objects.
    2. ``_hierarchy`` a dictionary (default) that holds the
       inheritance hierarchy of each class. Each key is a class
       and the value is a list of classes. The first name in the
       list is that of the key class.

    The goal of the ``_hierarchy`` object to facilitate the
    lookup of themeable properties taking into consideration the
    inheritance hierarchy. For example if `strip_text_x` inherits
    from `strip_text` which inherits from `text`, then if a property
    of `strip_text_x` is requested, the lookup should fallback to
    the other two if `strip_text_x` is not present or is missing
    the requested property.
    """

    def __init__(cls, name, bases, namespace):
        if not hasattr(cls, "_registry"):
            cls._registry = {}
            cls._hierarchy = collections.defaultdict(list)
        else:
            cls._registry[name] = cls
            cls._hierarchy[name].append(name)
            for base in bases:
                for base2 in base.mro()[:-2]:
                    cls._hierarchy[base2.__name__].append(name)


def alias(name, class_object):
    """
    Create an alias of a class object

    The objective of this method is to have
    an alias that is Registered. i.e If we have

        class_b = class_a

    Makes `class_b` an alias of `class_a`, but if
    `class_a` is registered by its metaclass,
    `class_b` is not. The solution

        alias('class_b', class_a)

    is equivalent to:

        class_b = class_a
        Register['class_b'] = class_a
    """
    module = inspect.getmodule(class_object)
    module.__dict__[name] = class_object
    if isinstance(class_object, Registry):
        Registry[name] = class_object


def get_kwarg_names(func):
    """
    Return a list of valid kwargs to function func
    """
    sig = inspect.signature(func)
    kwonlyargs = [
        p.name for p in sig.parameters.values() if p.default is not p.empty
    ]
    return kwonlyargs


def get_valid_kwargs(func, potential_kwargs):
    """
    Return valid kwargs to function func
    """
    kwargs = {}
    for name in get_kwarg_names(func):
        with suppress(KeyError):
            kwargs[name] = potential_kwargs[name]
    return kwargs


def copy_missing_columns(df, ref_df):
    """
    Copy missing columns from ref_df to df

    If df and ref_df are the same length, the columns are
    copied in the entirety. If the length ofref_df is a
    divisor of the length of df, then the values of the
    columns from ref_df are repeated.

    Otherwise if not the same length, df gets a column
    where all elements are the same as the first element
    in ref_df

    Parameters
    ----------
    df : dataframe
        Dataframe to which columns will be added
    ref_df : dataframe
        Dataframe from which columns will be copied
    """
    cols = ref_df.columns.difference(df.columns)
    _loc = ref_df.columns.get_loc

    l1, l2 = len(df), len(ref_df)
    if l1 >= l2 and l1 % l2 == 0:
        idx = np.tile(range(l2), l1 // l2)
    else:
        idx = np.repeat(0, l1)

    for col in cols:
        df[col] = ref_df.iloc[idx, _loc(col)].values


def data_mapping_as_kwargs(args, kwargs):
    """
    Return kwargs with the mapping and data values

    Parameters
    ----------
    args : tuple
        Arguments to :class:`geom` or :class:`stat`.
    kwargs : dict
        Keyword arguments to :class:`geom` or :class:`stat`.

    Returns
    -------
    out : dict
        kwargs that includes 'data' and 'mapping' keys.
    """
    data, mapping = order_as_data_mapping(*args)

    # check kwargs #
    if mapping is not None:
        if "mapping" in kwargs:
            raise PlotnineError("More than one mapping argument.")
        else:
            kwargs["mapping"] = mapping
    else:
        if "mapping" not in kwargs:
            mapping = aes()

    if kwargs.get("mapping", None) is None:
        kwargs["mapping"] = mapping

    if data is not None and "data" in kwargs:
        raise PlotnineError("More than one data argument.")
    elif "data" not in kwargs:
        kwargs["data"] = data

    duplicates = set(kwargs["mapping"]) & set(kwargs)
    if duplicates:
        msg = "Aesthetics {} specified two times."
        raise PlotnineError(msg.format(duplicates))
    return kwargs


def ungroup(data: DataLike) -> DataLike:
    """Return an ungrouped DataFrame, or pass the original data back."""

    if isinstance(data, DataFrameGroupBy):
        return data.obj  # type: ignore

    return data


def order_as_data_mapping(
    arg1: DataLike | aes | None,
    arg2: DataLike | aes | None,
) -> tuple[DataLike | None, aes | None]:
    """
    Reorder args to ensure (data, mapping) order

    This function allow the user to pass mapping and data
    to ggplot and geom in any order.

    Parameter
    ---------
    arg1 : pd.DataFrame | aes
        Dataframe or aes Mapping
    arg2 : pd.DataFrame | aes
        Dataframe or aes Mapping

    Returns
    -------
    data : pd.DataFrame | callable
    mapping : aes
    """
    # Valid types for the values are:
    #   - None, None
    #   - Dataframe, None
    #   - None, DataFrame
    #   - aes, None
    #   - None, aes
    #   - DataFrame, aes
    data: DataLike | None = None
    mapping: aes | None = None

    for arg in [arg1, arg2]:
        if isinstance(arg, aes):
            if mapping is None:
                mapping = arg
            else:
                raise TypeError(
                    "Expected a single aesthetic mapping, found two"
                )
        elif is_data_like(arg):
            if data is None:
                data = arg
            else:
                raise TypeError("Expected a single dataframe, found two")
        elif arg is not None:
            raise TypeError(
                f"Bad type of argument {arg!r}, expected a dataframe "
                "or a mapping."
            )

    return data, mapping


# Returning a type guard here is not fully sound, because if `obj`
# is a callable, we aren't checking that it has no required args
# and we can't check the return value's type.
def is_data_like(obj: Any) -> TypeGuard[DataLike]:
    """
    Return True if obj could be data

    Parameters
    ----------
    obj : object
        Object that could be data

    Returns
    -------
    out : bool
        Whether obj could represent data as expected by
        ggplot(), geom() or stat().
    """
    return (
        isinstance(obj, pd.DataFrame)
        or callable(obj)
        or hasattr(obj, "to_pandas")
    )


def interleave(*arrays):
    """
    Interleave arrays

    All arrays/lists must be the same length

    Parameters
    ----------
    arrays : tup
        2 or more arrays to interleave

    Return
    ------
    out : np.array
        Result from interleaving the input arrays
    """
    return np.column_stack(arrays).ravel()


def resolution(x, zero=True):
    """
    Compute the resolution of a data vector

    Resolution is smallest non-zero distance between adjacent values

    Parameters
    ----------
    x    : 1D array-like
    zero : Boolean
        Whether to include zero values in the computation

    Result
    ------
    res : resolution of x
        If x is an integer array, then the resolution is 1
    """
    from mizani.bounds import zero_range

    x = np.asarray(x)

    # (unsigned) integers or an effective range of zero
    _x = x[~pd.isna(x)]
    _x = (x.min(), x.max())
    if x.dtype.kind in ("i", "u") or zero_range(_x):
        return 1

    x = np.unique(x)
    if zero:
        x = np.unique(np.hstack([0, x]))

    return np.min(np.diff(np.sort(x)))


def cross_join(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
    Return a dataframe that is a cross between dataframes
    df1 and df2

    ref: https://github.com/pydata/pandas/issues/5401
    """
    if len(df1) == 0:
        return df2

    if len(df2) == 0:
        return df1

    # Add as lists so that the new index keeps the items in
    # the order that they are added together
    all_columns = list(pd.Index(list(df1.columns) + list(df2.columns)))
    df1["key"] = 1
    df2["key"] = 1
    return pd.merge(df1, df2, on="key").loc[:, all_columns]


def to_inches(value: float, units: str) -> float:
    """
    Convert value to inches

    Parameters
    ----------
    value : float
        Value to be converted
    units : str
        Units of value. Must be one of
        `['in', 'cm', 'mm']`.
    """
    lookup: dict[str, Callable[[float], float]] = {
        "in": lambda x: x,
        "cm": lambda x: x / 2.54,
        "mm": lambda x: x / (2.54 * 10),
    }
    try:
        return lookup[units](value)
    except KeyError:
        raise PlotnineError(f"Unknown units '{units}'")


def from_inches(value: float, units: str) -> float:
    """
    Convert value in inches to given units

    Parameters
    ----------
    value : float
        Value to be converted
    units : str
        Units to convert value to. Must be one of
        `['in', 'cm', 'mm']`.
    """
    lookup: dict[str, Callable[[float], float]] = {
        "in": lambda x: x,
        "cm": lambda x: x * 2.54,
        "mm": lambda x: x * 2.54 * 10,
    }
    try:
        return lookup[units](value)
    except KeyError:
        raise PlotnineError(f"Unknown units '{units}'")


class array_kind:
    @staticmethod
    def discrete(arr):
        """
        Return True if array is discrete

        Parameters
        ----------
        arr : numpy.array
            Must have a dtype

        Returns
        -------
        out : bool
            Whether array `arr` is discrete
        """
        return arr.dtype.kind in "ObUS"

    @staticmethod
    def continuous(arr):
        """
        Return True if array is continuous

        Parameters
        ----------
        arr : numpy.array or pandas.series
            Must have a dtype

        Returns
        -------
        out : bool
            Whether array `arr` is continuous
        """
        return arr.dtype.kind in "ifuc"

    @staticmethod
    def datetime(arr):
        return arr.dtype.kind == "M"

    @staticmethod
    def timedelta(arr):
        return arr.dtype.kind == "m"

    @staticmethod
    def ordinal(arr):
        """
        Return True if array is an ordered categorical

        Parameters
        ----------
        arr : numpy.array
            Must have a dtype

        Returns
        -------
        out : bool
            Whether array `arr` is an ordered categorical
        """
        if isinstance(arr.dtype, pd.CategoricalDtype):
            return arr.cat.ordered
        return False

    @staticmethod
    def categorical(arr):
        """
        Return True if array is a categorical

        Parameters
        ----------
        arr : list-like
            List

        Returns
        -------
        bool
            Whether array `arr` is a categorical
        """
        if not hasattr(arr, "dtype"):
            return False

        return isinstance(arr.dtype, pd.CategoricalDtype)


def log(x, base=None):
    """
    Calculate the log

    Parameters
    ----------
    x : float or array_like
        Input values
    base : int or float (Default: None)
        Base of the log. If `None`, the natural logarithm
        is computed (`base=np.e`).

    Returns
    -------
    out : float or ndarray
        Calculated result
    """
    if base == 10:
        return np.log10(x)
    elif base == 2:
        return np.log2(x)
    elif base is None or base == np.e:
        return np.log(x)
    else:
        return np.log(x) / np.log(base)


class ignore_warnings:
    """
    Ignore Warnings Context Manager

    Wrap around warnings.catch_warnings to make ignoring
    warnings easier.

    Parameters
    ----------
    *categories : tuple
        Warning categories to ignore e.g UserWarning,
        FutureWarning, RuntimeWarning, ...
    """

    _cm: warnings.catch_warnings

    def __init__(self, *categories):
        self.categories = categories
        self._cm = warnings.catch_warnings()

    def __enter__(self):
        self._cm.__enter__()
        for c in self.categories:
            warnings.filterwarnings("ignore", category=c)

    def __exit__(self, type, value, traceback):
        return self._cm.__exit__(type, value, traceback)


def get_ipython() -> "InteractiveShell" | None:
    """
    Return running IPython instance or None
    """
    try:
        from IPython.core.getipython import get_ipython
    except ImportError:
        return None
    return get_ipython()

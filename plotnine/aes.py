from __future__ import absolute_import, division, print_function
import re
from copy import deepcopy

import six

from .utils import suppress

__all__ = ['aes']

all_aesthetics = {
    'alpha', 'angle', 'color', 'colour', 'fill', 'group', 'intercept',
    'label', 'lineheight', 'linetype', 'lower', 'middle', 'radius',
    'sample', 'shape', 'size', 'slope', 'stroke', 'upper', 'weight', 'x',
    'xend', 'xintercept', 'xmax', 'xmin', 'y', 'yend', 'yintercept',
    'ymax', 'ymin'}

scaled_aesthetics = {
    'x', 'y', 'alpha', 'color', 'colour', 'fill',
    'linetype', 'shape', 'size', 'stroke'
}

CALCULATED_RE = re.compile(r'\.\.([a-zA-Z0-9_]+)\.\.')


class aes(dict):
    """
    Create aesthetic mappings

    Parameters
    ----------
    x : str | array_like | scalar | str-expression
        x aesthetic mapping
    y : str | array_like | scalar | str-expression
        y aesthetic mapping

    **kwargs : dict
        Other aesthetic mappings


    The value of each mapping must be one of;

    - **string**::

            import pandas as pd
            import numpy as np

            arr = [11, 12, 13]
            df = pd.DataFrame({'alpha': [1, 2, 3],
                               'beta': [1, 2, 3],
                               'gam ma': [1, 2, 3]})

            # Refer to a column in a dataframe
            ggplot(df, aes(x='alpha', y='beta'))

    - **array_like**::

            # A variable
            ggplot(df, aes(x='alpha', y=[4, 5, 6]))

            # or an inplace list
            ggplot(df, aes(x='alpha', y=arr))

    - **scalar**::

            # A scalar value/variable
            ggplot(df, aes(x='alpha', y=4))

            # The above statement is equivalent to
            ggplot(df, aes(x='alpha', y=[4, 4, 4]))

    - **String expression**::

            ggplot(df, aes(x='alpha', y='2*beta'))
            ggplot(df, aes(x='alpha', y='np.sin(beta)'))
            ggplot(df, aes(x='df.index', y='beta'))

      The strings in the expression can refer to;

        1. columns in the dataframe
        2. variables in the namespace

      with the column names having precedence over the variables.
      For expressions, columns in the dataframe that are mapped to
      must have names that would be valid python variable names.

      This is okay::

        # 'gam ma' is a column in the dataframe
        ggplot(df, aes(x='df.index', y='gam ma'))

      While this is not::

        # 'gam ma' is a column in the dataframe, but not
        # valid python variable name
        ggplot(df, aes(x='df.index', y='np.sin(gam ma)'))

    .. rubric:: The group aesthetic

    ``group`` is a special aesthetic that the user can *map* to.
    It is used to group the plotted items. If not specified, it
    is automatically computed and in most cases the computed
    groups are sufficient. However, there may be cases were it is
    handy to map to it.

    Note
    ----
    Only the **x** and **y** aesthetic mappings can be specified as
    positional arguments. All the rest must be keyword arguments.
    """

    def __init__(self, *args, **kwargs):
        kwargs = rename_aesthetics(kwargs)
        kwargs.update(zip(('x', 'y'), args))
        self.update(kwargs)

    def __deepcopy__(self, memo):
        """
        Deep copy without copying the environment
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        # Just copy the keys and point to the env
        for key, item in self.items():
            result[key] = deepcopy(self[key], memo)

        return result

    def __radd__(self, gg, inplace=False):
        gg = gg if inplace else deepcopy(gg)
        self = deepcopy(self)
        gg.mapping.update(self)
        gg.labels.update(make_labels(self))
        return gg


def rename_aesthetics(d):
    with suppress(KeyError):
        d['color'] = d.pop('colour')

    with suppress(KeyError):
        d['outlier_color'] = d.pop('outlier_colour')
    return d


def is_calculated_aes(aesthetics):
    """
    Return a list of the aesthetics that are calculated
    """
    calculated_aesthetics = []
    for k, v in aesthetics.items():
        if not isinstance(v, six.string_types):
            continue
        if CALCULATED_RE.search(v):
            calculated_aesthetics.append(k)
    return calculated_aesthetics


def strip_dots(value):
    """
    Remove dots(if any) that mark calculated aesthetics

    Parameters
    ----------
    value : object
        Aesthetic value. In most cases this will be a string
        but other types will pass through unmodified.

    Return
    ------
    out : object
        Aesthetic value with the dots removed.
    """
    with suppress(TypeError):
        value = CALCULATED_RE.sub(r'\1', value)
    return value


def aes_to_scale(var):
    """
    Look up the scale that should be used for a given aesthetic
    """
    if var in {'x', 'xmin', 'xmax', 'xend', 'xintercept'}:
        var = 'x'
    elif var in {'y', 'ymin', 'ymax', 'yend', 'yintercept'}:
        var = 'y'
    return var


def is_position_aes(vars_):
    """
    Figure out if an aesthetic is a position aesthetic or not
    """
    try:
        return all([aes_to_scale(v) in {'x', 'y'} for v in vars_])
    except TypeError:
        return aes_to_scale(vars_) in {'x', 'y'}


def make_labels(mapping):
    """
    Convert aesthetic mapping into text labels
    """
    labels = mapping.copy()
    for ae in labels:
        labels[ae] = strip_dots(labels[ae])
    return labels


def is_valid_aesthetic(value, ae):
    """
    Return True if `value` looks valid.

    Parameters
    ----------
    value : object
        Value to check
    ae : str
        Aesthetic name

    Returns
    -------
    out : bool
        Whether the value is of a valid looking form.

    Note
    ----
    There are no guarantees that he value is spot on
    valid.
    """

    if ae == 'linetype':
        named = {'solid', 'dashed', 'dashdot', 'dotted',
                 '_', '--', '-.', ':', 'None', ' ', ''}
        if value in named:
            return True

        # tuple of the form (offset, (on, off, on, off, ...))
        # e.g (0, (1, 2))
        conditions = [isinstance(value, tuple),
                      isinstance(value[0], int),
                      isinstance(value[1], tuple),
                      len(value[1]) % 2 == 0,
                      all(isinstance(x, int) for x in value[1])]
        if all(conditions):
            return True
        return False

    elif ae == 'shape':
        if isinstance(value, six.string_types):
            return True

        # tuple of the form (numsides, style, angle)
        # where style is in the range [0, 3]
        # e.g (4, 1, 45)
        conditions = [isinstance(value, tuple),
                      all(isinstance(x, int) for x in value),
                      0 <= value[1] < 3]
        if all(conditions):
            return True
        return False

    elif ae in {'color', 'fill'}:
        if isinstance(value, six.string_types):
            return True
        with suppress(TypeError):
            if (isinstance(value, (tuple, list)) and
                    all(0 <= x <= 1 for x in value)):
                return True
        return False

    # For any other aesthetics we return False to allow
    # for special cases to be discovered and then coded
    # for appropriately.
    return False

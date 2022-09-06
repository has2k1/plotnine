import numbers

import numpy as np
import pandas as pd
import pandas.api.types as pdtypes

from ..exceptions import PlotnineError

__all__ = ['after_stat', 'after_scale', 'stage']

_TPL_EVAL_FAIL = """\
Could not evaluate the '{}' mapping: '{}' \
(original error: {})"""

_TPL_BAD_EVAL_TYPE = """\
The '{}' mapping: '{}' produced a value of type '{}',\
but only single items and lists/arrays can be used. \
(original error: {})"""


class stage:
    """
    Stage allows you evaluating mapping at more than one stage

    You can evaluate an expression of a variable in a dataframe, and
    later evaluate an expression that modifies the values mapped to
    the scale.

    Parameters
    ----------
    start : expression | array_like | scalar
        Aesthetic expression using primary variables from the layer
        data.
    after_stat : expression
        Aesthetic expression using variables calculated by the stat.
    after_scale : expression
        Aesthetic expression using aesthetics of the layer.
    """

    def __init__(self, start=None, after_stat=None, after_scale=None):
        self.start = start
        self.after_stat = after_stat
        self.after_scale = after_scale

    def __repr__(self):
        """
        Repr for staged mapping
        """
        # Shorter representation when the mapping happens at a
        # single stage
        if self.after_stat is None and self.after_scale is None:
            return f'{repr(self.start)}'
        if self.start is None and self.after_scale is None:
            return f'after_stat({repr(self.after_stat)})'
        if self.start is None and self.after_stat is None:
            return f'after_scale({repr(self.after_scale)})'
        return (
            f'stage(start={repr(self.start)}, '
            f'after_stat={repr(self.after_stat)}, '
            f'after_scale={repr(self.after_scale)})'
        )


def after_stat(x):
    """
    Evaluate mapping after statistic has been calculated

    Parameters
    ----------
    x : str
        An expression

    See Also
    --------
    :func:`after_scale` : For how to alter aesthetics after the data has been
        mapped by the scale.
    :class:`stage` : For how to map to aesthetics at more than one stage of
        the plot building pipeline.
    """
    return stage(after_stat=x)


def after_scale(x):
    """
    Evaluate mapping after variable has been mapped to the scale

    This gives the user a chance to alter the value of a variable
    in the final units of the scale e.g. the rgb hex color.

    Parameters
    ----------
    x : str
        An expression

    See Also
    --------
    :func:`after_stat` : For how to map aesthetics to variable calculated
        by the stat
    :class:`stage` : For how to map to aesthetics at more than one stage of
        the plot building pipeline.
    """
    return stage(after_scale=x)


def reorder(x, y, fun=np.median, ascending=True):
    """
    Reorder categorical by sorting along another variable

    It is the order of the categories that changes. Values in x
    are grouped by categories and summarised to determine the
    new order.

    Credit: Copied from plydata

    Parameters
    ----------
    x : list-like
        Values that will make up the categorical.
    y : list-like
        Values by which ``c`` will be ordered.
    fun : callable
        Summarising function to ``x`` for each category in ``c``.
        Default is the *median*.
    ascending : bool
        If ``True``, the ``c`` is ordered in ascending order of ``x``.

    Examples
    --------
    >>> c = list('abbccc')
    >>> x = [11, 2, 2, 3, 33, 3]
    >>> cat_reorder(c, x)
    [a, b, b, c, c, c]
    Categories (3, object): [b, c, a]
    >>> cat_reorder(c, x, fun=max)
    [a, b, b, c, c, c]
    Categories (3, object): [b, a, c]
    >>> cat_reorder(c, x, fun=max, ascending=False)
    [a, b, b, c, c, c]
    Categories (3, object): [c, a, b]
    >>> c_ordered = pd.Categorical(c, ordered=True)
    >>> cat_reorder(c_ordered, x)
    [a, b, b, c, c, c]
    Categories (3, object): [b < c < a]
    >>> cat_reorder(c + ['d'], x)
    Traceback (most recent call last):
        ...
    ValueError: Lengths are not equal. len(c) is 7 and len(x) is 6.
    """
    if len(x) != len(y):
        raise ValueError(
            f"Lengths are not equal. {len(x)=}, {len(x)=}"
        )
    summary = (pd.Series(y)
               .groupby(x)
               .apply(fun)
               .sort_values(ascending=ascending)
               )
    cats = summary.index.to_list()
    return pd.Categorical(x, categories=cats)


# These are function that can be called by the user inside the aes()
# mapping. This is meant to make the variable transformations as easy
# as they are in ggplot2
AES_INNER_NAMESPACE = {
    'factor': pd.Categorical,
    'reorder': reorder
}


def evaluate(aesthetics, data, env):
    """
    Evaluate aesthetics

    Parameters
    ----------
    aesthetics : dict-like
        Aesthetics to evaluate. They must be of the form {name: expr}
    data : pd.DataFrame
        Dataframe whose columns are/may-be variables in the aesthetic
        expressions i.e. it is a namespace with variables.
    env : ~patsy.Eval.Environment
        Environment in which the aesthetics are evaluated

    Returns
    -------
    evaled : pd.DataFrame
        Dataframe of the form {name: result}, where each column is the
        result from evaluating an expression.

    Examples
    --------
    >>> import patsy
    >>> var1 = 2
    >>> env = patsy.eval.EvalEnvironment.capture()
    >>> df = pd.DataFrame({'x': range(1, 6)})
    >>> aesthetics = {'y': 'x**var1'}
    >>> evaluate(aesthetics, df, env)
        y
    0   1
    1   4
    2   9
    3  16
    4  25
    """
    env = env.with_outer_namespace(AES_INNER_NAMESPACE)

    # Using `type` preserves the subclass of pd.DataFrame
    evaled = type(data)(index=data.index)

    # If a column name is not in the data, it is evaluated/transformed
    # in the environment of the call to ggplot
    for ae, col in aesthetics.items():
        if isinstance(col, str):
            if col in data:
                evaled[ae] = data[col]
            else:
                try:
                    new_val = env.eval(col, inner_namespace=data)
                except Exception as e:
                    raise PlotnineError(
                        _TPL_EVAL_FAIL.format(ae, col, str(e)))

                try:
                    evaled[ae] = new_val
                except Exception as e:
                    raise PlotnineError(
                        _TPL_BAD_EVAL_TYPE.format(
                            ae, col, str(type(new_val)), str(e)))
        elif pdtypes.is_list_like(col):
            n = len(col)
            if len(data) and n != len(data) and n != 1:
                raise PlotnineError(
                    "Aesthetics must either be length one, " +
                    "or the same length as the data")
            # An empty dataframe does not admit a scalar value
            elif len(evaled) and n == 1:
                col = col[0]
            evaled[ae] = col
        elif is_known_scalar(col):
            if not len(evaled):
                col = [col]
            evaled[ae] = col
        else:
            msg = "Do not know how to deal with aesthetic '{}'"
            raise PlotnineError(msg.format(ae))

    return evaled


def is_known_scalar(value):
    """
    Return True if value is a type we expect in a dataframe
    """
    def _is_datetime_or_timedelta(value):
        # Using pandas.Series helps catch python, numpy and pandas
        # versions of these types
        return pd.Series(value).dtype.kind in ('M', 'm')

    return not np.iterable(value) and (isinstance(value, numbers.Number) or
                                       _is_datetime_or_timedelta(value))

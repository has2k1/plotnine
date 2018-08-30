import pandas as pd
from contextlib import suppress

from ..exceptions import PlotnineError


def collapse_label_lines(label_info):
    """
    Concatenate all items in series into one item
    """
    return pd.Series([', '.join(label_info)])


def label_value(label_info, multi_line=True):
    """
    Convert series values to str and maybe concatenate them

    Parameters
    ----------
    label_info : series
        Series whose values will be returned
    multi_line : bool
        Whether to place each variable on a separate line

    Returns
    -------
    out : series
        Label text strings
    """
    label_info = label_info.astype(str)
    if not multi_line:
        label_info = collapse_label_lines(label_info)

    return label_info


def label_both(label_info, multi_line=True, sep=': '):
    """
    Concatenate the index and the value of the series.

    Parameters
    ----------
    label_info : series
        Series whose values will be returned. It must have
        an index made of variable names.
    multi_line : bool
        Whether to place each variable on a separate line
    sep :  str
        Separation between variable name and value

    Returns
    -------
    out : series
        Label text strings
    """
    label_info = label_info.astype(str)
    for var in label_info.index:
        label_info[var] = '{0}{1}{2}'.format(var, sep, label_info[var])

    if not multi_line:
        label_info = collapse_label_lines(label_info)

    return label_info


def label_context(label_info, multi_line=True, sep=': '):
    """
    Create an unabiguous label string

    If facetting over a single variable, `label_value` is
    used, if two or more variables then `label_both` is used.

    Parameters
    ----------
    label_info : series
        Series whose values will be returned. It must have
        an index made of variable names
    multi_line : bool
        Whether to place each variable on a separate line
    sep :  str
        Separation between variable name and value

    Returns
    -------
    out : str
        Contatenated label values (or pairs of variable names
        & values)
    """
    if len(label_info) == 1:
        return label_value(label_info, multi_line)
    else:
        return label_both(label_info, multi_line, sep)


LABELLERS = {
    'label_value': label_value,
    'label_both': label_both,
    'label_context': label_context}


def as_labeller(x, default=label_value, multi_line=True):
    """
    Coerse to labeller function

    Parameters
    ----------
    x : function | dict
        Object to coerce
    default : function | str
        Default labeller. If it is a string,
        it should be the name of one the labelling
        functions provided by plotnine.
    multi_line : bool
        Whether to place each variable on a separate line

    Returns
    -------
    out : function
        Labelling function
    """
    if x is None:
        x = default

    # One of the labelling functions as string
    with suppress(KeyError, TypeError):
        x = LABELLERS[x]

    # x is a labeller
    with suppress(AttributeError):
        if x.__name__ == '_labeller':
            return x

    def _labeller(label_info):
        label_info = pd.Series(label_info).astype(str)

        if callable(x) and x.__name__ in LABELLERS:
            # labellers in this module
            return x(label_info)
        elif hasattr(x, '__contains__'):
            # dictionary lookup
            for var in label_info.index:
                if label_info[var] in x:
                    label_info[var] = x[label_info[var]]
            return label_info
        elif callable(x):
            # generic function
            for var in label_info.index:
                label_info[var] = x(label_info[var])
            return label_info
        else:
            msg = "Could not use '{0}' for labelling."
            raise PlotnineError(msg.format(x))

    return _labeller


def labeller(rows=None, cols=None, multi_line=True,
             default=label_value, **kwargs):
    """
    Return a labeller function

    Parameters
    ----------
    rows : str | function | None
        How to label the rows
    cols : str | function | None
        How to label the columns
    multi_line : bool
        Whether to place each variable on a separate line
    default : function | str
        Fallback labelling function. If it is a string,
        it should be the name of one the labelling
        functions provided by plotnine.
    kwargs : dict
        {variable name : function | string} pairs for
        renaming variables. A function to rename the variable
        or a string name.

    Returns
    -------
    out : function
        Function to do the labelling
    """
    # Sort out the labellers along each dimension
    rows_labeller = as_labeller(rows, default, multi_line)
    cols_labeller = as_labeller(cols, default, multi_line)

    def _labeller(label_info):
        # When there is no variable specific labeller,
        # use that of the dimension
        if label_info._meta['dimension'] == 'rows':
            margin_labeller = rows_labeller
        else:
            margin_labeller = cols_labeller

        # Labelling functions expect string values
        label_info = label_info.astype(str)

        # Each facetting variable is labelled independently
        for name, value in label_info.iteritems():
            func = as_labeller(kwargs.get(name), margin_labeller)
            new_info = func(label_info[[name]])
            label_info[name] = new_info[name]

        if not multi_line:
            label_info = collapse_label_lines(label_info)

        return label_info

    return _labeller

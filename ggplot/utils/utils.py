"""
Little functions used all over the codebase
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import matplotlib.cbook as cbook
import six


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

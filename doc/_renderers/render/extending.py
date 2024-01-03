"""
Extending the rendering
"""
from types import CellType, FunctionType
from typing import Any, Type

# Attributes that should not be copied when extending a base class
EXCLUDE_ATTRIBUTES = {"__module__", "__dict__", "__weakref__", "__doc__"}


def extend_base_class(cls: Type):
    """
    Class decorator to help extend (customise) the render classes

    Parameters
    ----------
    cls :
        Class (Base class) being extended (sub-classed).
    """
    base = cls.mro()[1]
    attrs = [name for name in vars(cls) if name not in EXCLUDE_ATTRIBUTES]
    for name in attrs:
        set_class_attr(base, name, getattr(cls, name))


def set_class_attr(cls: Type, name: str, value: Any):
    """
    Set class attribute

    Unlike the builtin setattr, this function make sure that values that
    are functions/methods, that use super() will work on the class on
    which they are attached.

    Parameters
    ----------
    cls :
        Class on which to attach the attribute
    name :
        Name of attribute.
    value :
        The value to set he attribute to.
    """
    # When a method uses super(), the python compiler wraps that method as
    # a closure over the __class__ in which the method is defined. If a
    # function is a closure, we rebuild it with __class__ changed to the
    # class being attached to.
    if isinstance(value, FunctionType) and value.__closure__:
        value = FunctionType(
            value.__code__.replace(co_freevars=("__class__",)),
            value.__globals__,
            closure=(CellType(cls),),
        )

    setattr(cls, name, value)

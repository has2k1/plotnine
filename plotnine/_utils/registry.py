from __future__ import annotations

from abc import ABCMeta
from collections import defaultdict
from typing import TYPE_CHECKING
from weakref import WeakValueDictionary

from ..exceptions import PlotnineError

if TYPE_CHECKING:
    from typing import TypeVar

    T = TypeVar("T")


def alias(cls: type[T]) -> type[T]:
    """
    Add docstring that class is an alias of its base class
    """
    if cls.__doc__ is not None:
        return cls

    base = cls.__bases__[0]
    name = base.__name__
    qualname = f"{base.__module__}.{name}"
    cls.__doc__ = f"alias of [{name}](`{qualname}`)"
    return cls


class _Registry(WeakValueDictionary):
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError as e:
            msg = (
                f"'{key}' Not in Registry. Make sure the module in "
                "which it is defined has been imported."
            )
            raise PlotnineError(msg) from e


Registry = _Registry()


class Register(ABCMeta):
    """
    Creates class that automatically registers all subclasses

    To prevent the base class from showing up in the registry,
    it should inherit from ABC. This metaclass uses a single
    dictionary to register all types of subclasses.

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
        is_base_class = len(bases) and bases[0].__name__ == "ABC"
        if not is_base_class:
            Registry[name] = sub_cls
        return sub_cls


class RegistryHierarchyMeta(type):
    """
    Create a class that registers subclasses and the Hierarchy

    The class has gets two properties:

    1. `_registry` a dictionary of all the subclasses of the
       base class. The keys are the names of the classes and
       the values are the class objects.
    2. `_hierarchy` a dictionary (default) that holds the
       inheritance hierarchy of each class. Each key is a class
       and the value is a list of classes. The first name in the
       list is that of the key class.

    The goal of the `_hierarchy` object to facilitate the
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
            cls._hierarchy = defaultdict(list)
        else:
            cls._registry[name] = cls
            cls._hierarchy[name].append(name)
            for base in bases:
                for base2 in base.mro()[:-2]:
                    cls._hierarchy[base2.__name__].append(name)

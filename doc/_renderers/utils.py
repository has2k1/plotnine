from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    TypeGuard,
    TypeVar,
)

from griffe import dataclasses as dc
from griffe import expressions as expr
from quartodoc import layout
from quartodoc.pandoc.inlines import Link

from .typing import DocMemberType, DocType  # noqa: TCH001

T = TypeVar("T")


@dataclass
class InterLink(Link):
    """
    Link with target enclosed in colons

    These targets of these links are interlink references
    that are finally resolved by the interlinks filter.
    """

    def __post_init__(self):
        self.target = f"`{self.target}`"


def shortcode(name: str, *args: str, **kwargs: str):
    """
    Create pandoc shortcode

    Parameters
    ----------
    str:
        Name of the shortcode
    *args:
        Arguments to the shortcode
    **kwargs:
        Named arguments for the shortcode

    References
    ----------
    https://quarto.org/docs/extensions/shortcodes.html
    """

    _args = " ".join(args)
    _kwargs = " ".join(f"{k}={v}" for k, v in kwargs.items())
    content = f"{name} {_args} {_kwargs}".strip()
    return f"{{{{< {content} >}}}}"


def is_typealias(obj: dc.Object | dc.Alias) -> bool:
    """
    Return True if obj is a declaration of a TypeAlias
    """
    # TODO:
    # Figure out if this handles new-style typealiases introduced
    # in python 3.12 to handle
    if not (isinstance(obj, dc.Attribute) and obj.annotation):
        return False
    elif isinstance(obj.annotation, expr.ExprName):
        return obj.annotation.name == "TypeAlias"
    elif isinstance(obj.annotation, str):
        return True
    return False


def is_protocol(obj: dc.Object | dc.Alias) -> bool:
    """
    Return True if obj is a class defining a typing Protocol
    """
    return (
        isinstance(obj, dc.Class)
        and isinstance(obj.bases, list)
        and len(obj.bases) > 0
        and isinstance(obj.bases[-1], expr.ExprName)
        and obj.bases[-1].canonical_path == "typing.Protocol"
    )


def is_typevar(obj: dc.Object | dc.Alias) -> bool:
    """
    Return True if obj is a declaration of a TypeVar
    """
    return (
        isinstance(obj, dc.Attribute)
        and hasattr(obj, "value")
        and isinstance(obj.value, expr.ExprCall)
        and isinstance(obj.value.function, expr.ExprName)
        and obj.value.function.name == "TypeVar"
    )


class isDoc:
    """
    TypeGuards for layout.Doc objects
    """

    @staticmethod
    def Function(el: DocMemberType) -> TypeGuard[layout.DocFunction]:
        return el.obj.is_function

    @staticmethod
    def Class(el: DocMemberType) -> TypeGuard[layout.DocClass]:
        return el.obj.is_class

    @staticmethod
    def Attribute(el: DocMemberType) -> TypeGuard[layout.DocAttribute]:
        return el.obj.is_attribute

    @staticmethod
    def Module(el: DocMemberType) -> TypeGuard[layout.DocModule]:
        return el.obj.is_attribute


def griffe_to_doc(obj: dc.Object | dc.Alias) -> DocType:
    """
    Convert griffe object to a quartodoc documentable type

    The function recursively includes all members.
    """
    return layout.Doc.from_griffe(
        obj.name,
        obj,
        members=[griffe_to_doc(m) for m in obj.all_members.values()],
    )


def no_init(default: T) -> T:
    """
    Set defaut value of a dataclass field that will not be __init__ed
    """
    return field(init=False, default=default)

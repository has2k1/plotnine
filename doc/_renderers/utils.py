from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Sequence

from griffe import dataclasses as dc
from griffe import expressions as expr
from quartodoc.pandoc.components import Attr
from quartodoc.pandoc.inlines import Code, Inlines, Link, Span

from .format import pretty_code, repr_obj
from .typing import DisplayNameFormat, DocObjectKind  # noqa: TCH001


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


def interlink_ref_to_link(interlink_ref: tuple[str | None, str]) -> InterLink:
    """
    Convert an rst reference to a quoted link

    The interlink has been parsed into a tuple form.

    e.g.

    1. Written as - ":meth:`class.some_method`:"
       Parsed value - ("class.some_method", "meth")
       Return value is a link with target - "`:meth:class.some_method`"

    2. Written as - "class.some_method"
       Parsed value - ("class.some_method", None)
       Return value is a link with target - "`class.some_method`"

    This method creates a link that can be represented in
    markdown and that is later processed by the lua interlinks
    filter into its final form.
    """
    name, role = interlink_ref
    target = f":{role}:{name}:" if role else f"{name}"
    return InterLink(content=name, target=target)


def build_signature_parameter(
    name: str, annotation: Optional[str], default: Optional[str | expr.Expr]
) -> str:
    """
    Create code snippet that defines a parameter
    """
    if default:
        default = repr_obj(default)  # type: ignore

    parts = []
    if name:
        parts.append(name)
    if annotation:
        parts.append(f": {annotation}")
        if default:
            parts.append(f" = {default}")
    elif default:
        parts.append(f"={default}")

    return "".join(parts)


def build_docstring_parameter(
    name: str, annotation: Optional[str], default: Optional[str | expr.Expr]
) -> str:
    """
    Create code snippet that defines a parameter
    """
    lst = []
    if name:
        lst.append(Span(name, Attr(classes=["doc-parameter-name"])))
    if annotation:
        if name:
            lst.append(
                Span(":", Attr(classes=["doc-parameter-annotation-sep"]))
            )
        annotation = pretty_code(annotation)
        lst.append(
            Span(annotation, Attr(classes=["doc-parameter-annotation"]))
        )
    if default:
        default = pretty_code(repr_obj(default))  # type: ignore
        lst.extend(
            [
                Span("=", Attr(classes=["doc-parameter-default-sep"])),
                Span(default, Attr(classes=["doc-parameter-default"])),
            ]
        )
    return str(Inlines(lst))


def get_object_display_name(
    el: dc.Alias | dc.Object, format: DisplayNameFormat = "relative"
) -> str:
    """
    Return a name to use for the object

    Parameters
    ----------
    el:
        A griffe Alias or Object
    format:
        The format to use for the object's name.
    """
    if format in ("name", "short"):
        res = el.name
    elif format == "relative":
        res = ".".join(el.path.split(".")[1:])
    elif format == "full":
        res = el.path
    elif format == "canonical":
        res = el.canonical_path
    else:
        raise ValueError(f"Unknown format {format!r} for an object name.")
    return res


def get_object_kind(el: dc.Alias | dc.Object) -> DocObjectKind:
    """
    Get an objects kind
    """
    kind: DocObjectKind = el.kind.value  # type: ignore
    if el.is_function and el.parent and el.parent.is_class:
        kind = "method"
    return kind


def get_method_parameters(el: dc.Function) -> dc.Parameters:
    """
    Return the parameters of a method

    Parameters
    ----------
    el:
        A griffe function / method
    """
    # adapted from mkdocstrings-python jinja tempalate
    if not len(el.parameters) > 0 or not el.parent:
        return el.parameters

    param = el.parameters[0].name
    omit_first_parameter = (
        el.parent.is_class and param in ("self", "cls")
    ) or (el.parent.is_module and el.is_class and param == "self")

    if omit_first_parameter:
        return dc.Parameters(*list(el.parameters)[1:])

    return el.parameters


def get_object_labels(el: dc.Alias | dc.Object) -> Sequence[str]:
    """
    Return labels for an object (iff object is a function/method)

    Parameters
    ----------
    el:
        A griffe object
    """
    # Only check for the labels we care about
    lst = (
        "cached",
        "property",
        "classmethod",
        "staticmethod",
        "abstractmethod",
        "typing.overload",
    )
    if el.is_function:
        return tuple(
            label.replace(".", "-") for label in lst if label in el.labels
        )
    elif el.is_attribute and is_typealias(el):
        return ("TypeAlias",)
    elif el.is_class and is_protocol(el):
        return ("Protocol",)
    else:
        return ()


def get_canonical_path_lookup(el: expr.Expr) -> dict[str, str]:
    """
    Return lookup table for the canonical path of identifiers in expression
    """
    lookup = {"TypeAlias": "typing.TypeAlias"}
    for o in el.iterate():
        # Assumes that name of an expresssion is a valid python
        # identifier
        if isinstance(o, expr.ExprName):
            lookup[o.name] = o.canonical_path
    return lookup


def make_doc_labels(labels: Sequence[str]) -> Span | Literal[""]:
    """
    Create codes used for doc labels

    Given the label names, it returns a Code object that
    creates the following HTML
    <span class="doc-labels">
        <code class="doc-label doc-label-name1"></code>
        <code class="doc-label doc-label-name2"></code>
    </span>
    """
    if not labels:
        return ""

    codes = [
        Code(" ", Attr(classes=["doc-label", f"doc-label-{label}"]))
        for label in labels
    ]
    return Span(codes, Attr(classes=["doc-labels"]))

from __future__ import annotations

from dataclasses import dataclass
from textwrap import indent
from typing import Optional, Sequence

from griffe import dataclasses as dc
from griffe import expressions as expr
from quartodoc.pandoc.inlines import Link

from .typing import DisplayNameFormat, DocObjectKind


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


def build_parameter(
    name: str, annotation: Optional[str], default: Optional[str | expr.Expr]
) -> str:
    """
    Create code snippet that defines a parameter
    """
    if not name and annotation:
        # e.g. Return values may not have a name
        return f"{annotation}"

    if default is None:
        if annotation:
            param = f"{name}: {annotation}"
        else:
            param = f"{name}"
    else:
        default = use_double_qoutes(str(default))

        if annotation:
            param = f"{name}: {annotation} = {default}"
        else:
            param = f"{name}={default}"

    return param


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
        return el.name
    elif format == "relative":
        return ".".join(el.path.split(".")[1:])
    elif format == "full":
        return el.path
    elif format == "canonical":
        return el.canonical_path
    else:
        raise ValueError(f"Unknown format {format!r} for an object name.")


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
        return tuple(label for label in lst if label in el.labels)
    else:
        return tuple()


def use_double_qoutes(s: str) -> str:
    """
    Change a repr str to use double quotes

    Parameters
    ----------
    s:
        A repr string
    """
    if len(s) >= 2:
        if s[0] == s[-1] == "'":
            s = f'"{s[1:-1]}"'
    return s


def make_formatted_signature(name: str, params_lst: list[str]) -> str:
    # Format to a maximum width of 78 chars
    # It fails when a parameter declarations is longer than 78
    opening = f"{name}("
    params_string = ", ".join(params_lst)
    closing = ")"
    pad = " " * 4
    if len(opening) + len(params_string) > 78:
        line_pad = f"\n{pad}"
        # One parameter per line
        if len(params_string) > 74:
            params_string = f",{line_pad}".join(params_lst)
        params_string = f"{line_pad}{params_string}"
        closing = f"\n{closing}"
    sig = f"{opening}{params_string}{closing}"
    return sig

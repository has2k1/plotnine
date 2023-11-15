from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from griffe import dataclasses as dc
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
    name: str, annotation: Optional[str], default: Optional[str]
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
    if el.parent and el.parent.is_class and len(el.parameters) > 0:
        if el.parameters[0].name in {"self", "cls"}:
            return dc.Parameters(*list(el.parameters)[1:])

    return el.parameters

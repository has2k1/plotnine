import re

import griffe.dataclasses as dc
import griffe.expressions as expr
from plum import dispatch
from quartodoc.pandoc.components import Attr
from quartodoc.pandoc.inlines import Span

# Pickout python identifiers from a string of code
IDENTIFIER_RE = re.compile(r"\b(?P<identifier>[^\W\d]\w*)", flags=re.UNICODE)

# Pickout quoted strings from a string of code
STRING_RE = re.compile(
    r"(?P<string>"  # group
    # Within quotes, match any character that has been backslashed
    # or that is not a double quote or backslash
    r'"(?:\\.|[^"\\])*"'  # double-quoted
    r"|"  # or
    r"'(?:\\.|[^'\\])*'"  # single-queoted
    ")",
    flags=re.UNICODE,
)

# quotes in inline <code> are converted to curly quotes.
# This translation table maps the quotes to html escape sequences
QUOTES_TRANSLATION = str.maketrans({'"': "&quot;", "'": "&apos;"})

# Characters that can appear that the start of a markedup string
MARKDOWN_START_CHARS = {"_", "*"}


def escape_quotes(s: str) -> str:
    """
    Replace double & single quotes with html escape sequences
    """
    return s.translate(QUOTES_TRANSLATION)


def escape_indents(s: str) -> str:
    """
    Convert indent spaces & newlines to &nbsp; and <br>

    The goal of this function is to convert a few spaces as is required
    to preserve the formatting.
    """
    return s.replace(" " * 4, "&nbsp;" * 4).replace("\n", "<br>")


def markdown_escape(s: str) -> str:
    """
    Escape string that may be interpreted as markdown

    This function is deliberately not robust to all possibilities. It
    will improve as needed.
    """
    if s and s[0] in MARKDOWN_START_CHARS:
        s = rf"\{s}"
    return s


def string_match_highlight_func(m: re.Match) -> str:
    """
    Return matched group(string) wrapped in a Span for a string
    """
    string_str = m.group("string")
    return str(Span(string_str, Attr(classes=["st"])))


def highlight_strings(s: str) -> str:
    """
    Wrap quoted sub-strings in s with a hightlight group for strings
    """
    return STRING_RE.sub(string_match_highlight_func, s)


@dispatch
def repr_obj(obj: expr.Expr):  # type: ignore
    """
    Representation of an expression as code
    """
    # We expect the obj expression to consist of
    # a combination of only strings and name expressions
    return "".join(repr_obj(x) for x in obj.iterate())  # type: ignore


@dispatch
def repr_obj(s: str) -> str:  # type: ignore
    """
    Repr of str enclosed double quotes
    """
    if len(s) >= 2 and (s[0] == s[-1] == "'"):
        s = f'"{s[1:-1]}"'
    return s


@dispatch
def repr_obj(obj: expr.ExprName) -> str:
    """
    A named expression
    """
    return obj.name


def canonical_path_lookup_table(el: expr.Expr):
    # Create lookup table
    lookup = {"TypeAlias": "typing.TypeAlias"}
    for o in el.iterate():
        # Assumes that name of an expresssion is a valid python
        # identifier
        if isinstance(o, expr.ExprName):
            lookup[o.name] = o.canonical_path
    return lookup


def formatted_signature(name: str, params: list[str]) -> str:
    """
    Return a formatted signature of function/method

    Parameters
    ----------
    name :
        Name of function/method/class(for the __init__ method)
    params :
        Parameters to the function. A each parameter is a
        string. e.g. a, *args, *, /, b=2, c=3, **kwargs
    """
    # Format to a maximum width of 78 chars
    # It fails when a parameter declarations is longer than 78
    opening = f"{name}("
    params_string = ", ".join(params)
    closing = ")"
    pad = " " * 4
    if len(opening) + len(params_string) > 78:
        line_pad = f"\n{pad}"
        # One parameter per line
        if len(params_string) > 74:
            params_string = f",{line_pad}".join(params)
        params_string = f"{line_pad}{params_string}"
        closing = f"\n{closing}"
    sig = f"{opening}{params_string}{closing}"
    return sig


def pretty_code(s: str) -> str:
    """
    Make code that will not be highlighted by pandoc pretty

    code inside html <code></code> tags (and without <pre> tags)
    makes it possible to have links & interlinks. But the white
    spaces and newlines in the code are squashed. And this code
    is also not highlighted by pandoc.

    Parameters
    ----------
    s :
        Code to be modified. It should already have markdown for
        the links, but should not be wrapped inside the <code>
        tags. Those tags should wrap the output of this function.
    """
    return escape_quotes(escape_indents(highlight_strings(s)))


def interlink_identifiers(el: dc.Attribute) -> str:
    """
    Render expression with identifiers in them interlinked
    """
    from .utils import InterLink

    if not el.value or isinstance(el.value, str):
        return str(el.value)

    lookup = canonical_path_lookup_table(el.value)

    def interlink_func(m: re.Match) -> str:
        identifier_str = m.group("identifier")
        try:
            canonical_path = lookup[identifier_str]
        except KeyError:
            return identifier_str
        return str(InterLink(identifier_str, canonical_path))

    definition_str = "\n".join(el.lines)
    return IDENTIFIER_RE.sub(interlink_func, definition_str)

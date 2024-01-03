from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property, singledispatchmethod
from typing import TYPE_CHECKING, cast

import griffe.expressions as expr
from griffe import dataclasses as dc
from griffe.docstrings import dataclasses as ds  # noqa: TCH002
from quartodoc import ast as qast
from quartodoc import layout
from quartodoc.pandoc.blocks import (
    Block,
    BlockContent,
    Blocks,
    CodeBlock,
    Div,
    Header,
)
from quartodoc.pandoc.components import Attr
from quartodoc.pandoc.inlines import Code, Inline, Inlines, Link, Span

from ..format import (
    markdown_escape,
    pretty_code,
    repr_obj,
)
from ..typing import DocObjectKind
from ..utils import InterLink, is_protocol, is_typealias, is_typevar, no_init
from .base import RenderBase

if TYPE_CHECKING:
    from typing import Literal, Optional, Sequence

    from ..typing import Annotation


@dataclass
class __RenderDoc(RenderBase):
    """
    Render a layout.Doc object
    """

    show_title: bool = no_init(True)
    """
    Whether to show the title of the object

    The title includes:

        1. symbol for the object
        2. name of the object
        3. labels the object

    Each of this can be independently turned off.
    """

    show_signature: bool = no_init(True)
    """Whether to show the signature"""

    show_signature_name: bool = no_init(True)
    """Whether to show the name of the object in the signature"""

    show_signature_annotation: bool = no_init(False)
    """
    Where to show type annotations in the signature

    The default is False because they are better displayed in the
    parameter definitions.
    """

    show_body: bool = no_init(True)
    """Whether to show the body of the object"""

    show_object_name: bool = no_init(True)
    """
    Whether to show the name of the object

    This is part of the title
    """

    show_object_symbol: bool = no_init(True)
    """
    Whether to show the symbol of the object

    This is part of the title
    """

    show_object_labels: bool = no_init(True)
    """
    Whether to show the labels of the object

    This is part of the title
    """

    def __post_init__(self):
        # The layout_obj is too general. It is typed to include all
        # classes of documentable objects. And for layout.Doc objects,
        # the core object is a griffe object contained within.
        # For convenience, we create attributes with narrower types
        # using cast instead of TypeAlias so that subclasses can
        # create narrower types.
        self.doc = cast(layout.Doc, self.layout_obj)
        """Doc Object"""

        self.obj = cast(dc.Object | dc.Alias, self.doc.obj)
        """Griffe object"""

        self.path = f"{self.obj.name}.qmd"
        """Name of the page where this object will be written"""

        self.show_signature = self.renderer.show_signature

    @cached_property
    def kind(self) -> DocObjectKind:
        """
        Return the object's kind
        """
        obj = self.obj
        kind = cast(DocObjectKind, obj.kind.value)
        if obj.is_function and obj.parent and obj.parent.is_class:
            kind = "method"
        if kind == "attribute":
            if is_typealias(obj):
                kind = "type"
            elif is_typevar(obj):
                kind = "typevar"
        return kind

    @cached_property
    def labels(self) -> Sequence[str]:
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
        if self.obj.is_function:
            return tuple(
                label.replace(".", "-")
                for label in lst
                if label in self.obj.labels
            )
        elif self.obj.is_class and is_protocol(self.obj):
            return ("Protocol",)
        else:
            return ()

    @cached_property
    def display_name(self) -> str:
        format = self.renderer.display_name_format
        if format == "auto":
            format = "full" if self.level == 1 else "name"
        return self.format_name(format)

    @cached_property
    def raw_title(self) -> str:
        format = "canonical" if self.level == 1 else "name"
        return markdown_escape(self.format_name(format))

    @cached_property
    def signature_name(self) -> str:
        return self.format_name(self.renderer.signature_name_format)

    def format_name(self, format="relative") -> str:
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
            res = self.obj.name
        elif format == "relative":
            res = ".".join(self.obj.path.split(".")[1:])
        elif format == "full":
            res = self.obj.path
        elif format == "canonical":
            res = self.obj.canonical_path
        else:
            raise ValueError(f"Unknown format {format!r} for an object name.")
        return res

    def render_labels(self) -> Span | Literal[""]:
        """
        Create codes used for doc labels

        Given the label names, it returns a Code object that
        creates the following HTML
        <span class="doc-labels">
            <code class="doc-label doc-label-name1"></code>
            <code class="doc-label doc-label-name2"></code>
        </span>
        """
        if not self.labels:
            return ""

        codes = [
            Code(" ", Attr(classes=["doc-label", f"doc-label-{l.lower()}"]))
            for l in self.labels
        ]
        return Span(codes, Attr(classes=["doc-labels"]))

    def render_annotation(
        self, annotation: Optional[Annotation] = None
    ) -> Inline | str:
        """
        Render an annotation

        This can be used to renderer the annotation of:

            1. self - if it is an Attribute & annotation is None
            2. annotation - annotation of a parameter in the signature
               of self
        """
        if annotation is None:
            if not isinstance(self.obj, dc.Attribute):
                msg = f"Cannot render annotation for type {type(self.obj)}."
                raise TypeError(msg)

            self.obj = cast(dc.Attribute, self.obj)
            annotation = self.obj.annotation

        def _render(ann):
            # Recursively render annotation
            if ann is None:
                return ""
            elif isinstance(ann, str):
                return repr_obj(ann)
            elif isinstance(ann, expr.ExprName):
                return InterLink(markdown_escape(ann.name), ann.canonical_path)
            elif isinstance(ann, expr.Expr):
                # A type annotation with ~ removes the qualname prefix
                path_str = ann.canonical_path
                if path_str[0] == "~":
                    return InterLink(ann.canonical_name, path_str[1:])
                return "".join(str(_render(a)) for a in ann)
            else:
                msg = f"Cannot render annotation for type {type(ann)}."
                raise TypeError(msg)

        return _render(annotation)

    def render_variable_definition(
        self,
        name: str,
        annotation: Optional[str],
        default: Optional[str | expr.Expr],
    ) -> Inline:
        """
        Create code snippet that declares a variable

        This applies to function parameters and module/class attributes

        Parameters
        ----------
        name :
            Name of the variable

        annotation :
            Type Annotation of the variable or parameter

        default :
            Default value of the variable/parameter.
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

        # Equal sign depends on name and annotation
        if name:
            eq = " = " if annotation else "="
            equals = Span(eq, Attr(classes=["doc-parameter-default-sep"]))
        else:
            equals = None

        if default:
            default = pretty_code(repr_obj(default))
            lst.extend(
                [
                    equals,
                    Span(default, Attr(classes=["doc-parameter-default"])),
                ]
            )
        return Inlines(lst)

    def render_title(self) -> Header:
        """
        Render the header of a docstring, including any anchors
        """
        symbol = (
            Code(
                # Pandoc requires some space to create empty code tags
                " ",
                Attr(classes=["doc-symbol", f"doc-symbol-{self.kind}"]),
            )
            if self.show_object_symbol
            else None
        )

        name = (
            Span(
                self.raw_title,
                Attr(classes=["doc-object-name", f"doc-{self.kind}-name"]),
            )
            if self.show_object_name
            else None
        )

        labels = self.render_labels() if self.show_object_labels else None

        classes = ["title", "doc-object", f"doc-{self.kind}"]
        if hasattr(self.obj, "members") and self.obj.members:
            classes.append("doc-has-member-docs")

        return Header(
            level=self.level,
            content=Inlines([symbol, name, labels]),
            attr=Attr(identifier=self.obj.path, classes=classes),
        )

    def render_body(self) -> BlockContent:
        """
        Render the docsting of the Doc object
        """
        if not self.obj.docstring:
            return None

        sections: list[Block] = []
        patched_sections = qast.transform(self.obj.docstring.parsed)
        for section in patched_sections:  # type: ignore
            title = (section.title or section.kind.value).title()
            body = self.render_section(section) or ""
            slug = title.lower().replace(" ", "-")
            section_classes = [f"doc-{slug}"]

            if title in ("Text", "Deprecated"):
                content = Div(body, Attr(classes=section_classes))
            else:
                header = Header(
                    self.level + 1,
                    title,
                    Attr(classes=section_classes),
                )
                content = Blocks([header, body])
            sections.append(content)

        return Blocks(sections)

    @singledispatchmethod
    def render_section(self, el: ds.DocstringSection) -> BlockContent:
        new_el = qast.transform(el)
        if isinstance(new_el, qast.ExampleCode):
            return CodeBlock(el.value, Attr(classes=["python"]))
        return el.value

    @render_section.register
    def _(self, el: ds.DocstringSectionExamples):
        return Blocks(
            [self.render_section(qast.transform(c)) for c in el.value]
        )

    @render_section.register
    def _(self, el: ds.DocstringSectionDeprecated):
        content = Div(
            Inlines(
                [
                    Span(
                        f"Deprecated since version {el.value.version}:",
                        Attr(classes=["versionmodified", "deprecated"]),
                    ),
                    el.value.description.strip(),
                ]
            ),
            Attr(classes=["doc-deprecated"]),
        )
        return str(content)

    def render_summary(self):
        """
        Return a line item that summarises the object
        """
        # The page where this object will be written
        link = Link(
            markdown_escape(self.doc.name), f"{self.path}#{self.doc.anchor}"
        )
        return [(str(link), self._describe_object(self.obj))]


class RenderDoc(__RenderDoc):
    """
    Extend Rendering of a layout.Doc
    """

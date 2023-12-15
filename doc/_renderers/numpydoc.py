from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, Optional, TypeAlias
from warnings import warn

from griffe import dataclasses as dc
from griffe import expressions as expr
from griffe.docstrings import dataclasses as ds
from numpydoc.docscrape import NumpyDocString
from plum import dispatch
from quartodoc import ast as qast
from quartodoc import layout
from quartodoc.pandoc.blocks import (
    Block,
    Blocks,
    CodeBlock,
    DefinitionItem,
    DefinitionList,
    Div,
    Header,
)
from quartodoc.pandoc.components import Attr
from quartodoc.pandoc.inlines import (
    Code,
    Inlines,
    Link,
    Span,
)
from quartodoc.renderers.base import Renderer
from quartodoc.renderers.md_renderer import _has_attr_section
from tabulate import tabulate

from .format import formatted_signature, markdown_escape, repr_obj
from .typing_modules import TypingModules
from .utils import (
    InterLink,
    build_docstring_parameter,
    build_signature_parameter,
    get_method_parameters,
    get_object_display_name,
    get_object_kind,
    get_object_labels,
    interlink_ref_to_link,
    make_doc_labels,
)

SummaryRow: TypeAlias = tuple[str, str]

if TYPE_CHECKING:
    from .typing import DisplayNameFormat

# NOTE
# Attribute
#    show_signature_annotations: bool
# Has been removed until we can find a way to do it where the
# annotations do not make signature significantly less readable.


@dataclass
class NumpyDocRenderer(Renderer):
    """
    Render strings to markdown in Numpydoc style
    """

    header_level: int = 1
    show_signature: bool = True
    display_name_format: DisplayNameFormat | Literal["auto"] = "auto"
    signature_name_format: DisplayNameFormat = "name"
    typing_module_paths: list[str] = field(default_factory=list)

    # style: str = field(default="numpydoc", init=False)
    style: str = "numpydoc"

    @contextmanager
    def _increment_header_level(self, n=1):
        """
        Create a context for a sub-section
        """
        self.header_level += n

        if self.header_level > 6:
            warn(
                f"Created header_level={self.header_level}. "
                "In HTML there are no tags for header levels > 6."
            )

        try:
            yield
        finally:
            self.header_level -= n

    # render_annotation method ------------------------------------------------

    @dispatch
    def render_annotation(self, el: str) -> str:  # type: ignore
        """Special hook for rendering a type annotation.

        Parameters
        ----------
        el:
            An object representing a type annotation.
        """
        return repr_obj(el)  # type: ignore

    @dispatch
    def render_annotation(self, el: None) -> str:  # type: ignore
        return ""

    @dispatch
    def render_annotation(self, el: expr.ExprName):  # type: ignore
        return str(InterLink(markdown_escape(el.name), el.canonical_path))

    @dispatch
    def render_annotation(self, el: expr.Expr) -> str:
        # A type annotation with ~ removes the qualname prefix
        path_str = el.canonical_path
        if path_str[0] == "~":
            return str(InterLink(el.canonical_name, path_str[1:]))
        return "".join(self.render_annotation(a) for a in el)  # type: ignore

    # signature method --------------------------------------------------------

    @dispatch
    def signature(self, el: layout.Doc) -> str:  # type: ignore
        return self.signature(el.obj)  # type: ignore

    @dispatch
    def signature(  # type: ignore
        self, el: dc.Alias, source: Optional[dc.Alias] = None
    ) -> str:
        """Return a string representation of an object's signature."""
        return self.signature(el.final_target, el)  # type: ignore

    @dispatch
    def signature(  # type: ignore
        self, el: dc.Class | dc.Function, source: Optional[dc.Alias] = None
    ) -> str:
        if not self.show_signature:
            return ""

        name = get_object_display_name(
            source or el, self.signature_name_format
        )
        params = self.render(get_method_parameters(el))  # type: ignore
        sig_str = formatted_signature(name, params)  # type: ignore
        sig = Div(
            CodeBlock(sig_str, Attr(classes=["py"])),
            Attr(classes=["doc-signature"]),
        )
        return str(sig)

    @dispatch
    def signature(
        self, el: dc.Module, source: Optional[dc.Alias] = None
    ) -> str:
        name = get_object_display_name(
            source or el, self.signature_name_format
        )
        if not name:
            return ""

        sig = Div(
            CodeBlock(name, Attr(classes=["py"])),
            Attr(classes=["doc-signature"]),
        )
        return str(sig)

    @dispatch
    def signature(
        self, el: dc.Attribute, source: Optional[dc.Alias] = None
    ) -> str:
        """
        Render an attribute
        """
        name = get_object_display_name(
            source or el, self.signature_name_format
        )
        annotation = self.render_annotation(el.annotation)  # type: ignore
        declaration = build_docstring_parameter(name, annotation, el.value)
        sig = Div(Code(declaration).html, Attr(classes=["doc-signature"]))
        return str(sig)

    # render_header method ----------------------------------------------------

    @dispatch
    def render_header(self, el: layout.Doc) -> Header:
        """Render the header of a docstring, including any anchors."""
        kind = get_object_kind(el.obj)
        labels = get_object_labels(el.obj)
        display_name_format = self.display_name_format
        if display_name_format == "auto":
            display_name_format = "full" if self.header_level == 1 else "name"

        name = get_object_display_name(el.obj, display_name_format)
        symbol_code = Code(
            # Pandoc requires some space to create empty code tags
            " ",
            Attr(
                classes=[
                    "doc-symbol",
                    "doc-symbol-heading",
                    f"doc-symbol-{kind}",
                ]
            ),
        )
        object_name = Span(
            markdown_escape(name),
            Attr(classes=["doc-object-name", f"doc-{kind}-name"]),
        )

        doc_labels = make_doc_labels(labels)
        classes = ["doc", "doc-object", f"doc-{kind}"]
        if hasattr(el, "members") and el.members:
            classes.append("doc-has-member-docs")

        h = Header(
            level=self.header_level,
            content=Inlines([symbol_code, object_name, doc_labels]),
            attr=Attr(identifier=el.obj.path, classes=classes),
        )
        return h

    # render method -----------------------------------------------------------

    @dispatch
    def render(self, el):  # type: ignore
        """Return a string representation of an object, or layout element."""
        raise NotImplementedError(f"Unsupported type: {type(el)}")

    @dispatch
    def render(self, el: str):  # type: ignore
        return el

    # render layouts ----------------------------------------------------------

    @dispatch
    def render(self, el: layout.Doc):  # type: ignore
        raise NotImplementedError(f"Unsupported Doc type: {type(el)}")

    @dispatch
    def render(self, el: layout.DocClass | layout.DocModule):  # type: ignore
        """
        Render documentation for a class or a module

        Whether to include members (attributes, classes or methods) is based
        on the config.
        """
        header = self.render_header(el)
        sig = self.signature(el)
        body = self.render(el.obj)  # type: ignore

        attr_docs = []
        class_docs = []
        meth_docs = []

        if el.members:
            raw_attrs = [x for x in el.members if x.obj.is_attribute]
            raw_classes = [x for x in el.members if x.obj.is_class]
            raw_meths = [x for x in el.members if x.obj.is_function]

            # The tables in all sections have these two columns
            header_row = ("Name", "Description")

            if raw_attrs and not _has_attr_section(el.obj.docstring):
                section_header = Header(
                    self.header_level + 1,
                    "Attributes",
                    Attr(classes=["doc-attributes"]),
                )
                rows: list[SummaryRow] = [
                    self.summarize(a)  # type: ignore
                    for a in raw_attrs
                ]
                attr_table = tabulate(rows, header_row, "grid")
                attr_docs = [section_header, str(attr_table)]

            if raw_classes:
                section_header = Header(
                    self.header_level + 1,
                    "Classes",
                    Attr(classes=["doc-classes"]),
                )
                rows: list[SummaryRow] = [
                    self.summarize(a)  # type: ignore
                    for a in raw_classes
                ]
                summary_table = tabulate(rows, header_row, "grid")

                n = 1 if el.flat else 2
                with self._increment_header_level(n):
                    docs = [
                        self.render(m)
                        for m in raw_classes
                        if isinstance(m, layout.Doc)
                    ]
                class_docs = [section_header, str(summary_table), *docs]

            if raw_meths:
                if isinstance(el, layout.DocClass):
                    section_name = "Methods"
                else:
                    section_name = "Functions"

                section_header = Header(
                    self.header_level + 1,
                    section_name,
                    Attr(classes=["doc-methods"]),
                )
                rows: list[SummaryRow] = [  # type: ignore
                    self.summarize(m) for m in raw_meths
                ]
                meth_table = tabulate(rows, header_row, "grid")

                n = 1 if el.flat else 2
                with self._increment_header_level(n):
                    docs: list[str] = [  # type: ignore
                        self.render(m)
                        for m in raw_meths
                        if isinstance(m, layout.Doc)
                    ]
                meth_docs = [section_header, str(meth_table), *docs]

        return str(
            Blocks([header, sig, body, *attr_docs, *class_docs, *meth_docs])
        )

    @dispatch
    def render(self, el: layout.Page):  # type: ignore
        if el.summary:
            header = Header(
                self.header_level, markdown_escape(el.summary.name)
            )
            desc = el.summary.desc
        else:
            header, desc = "", ""

        contents = [self.render(c) for c in el.contents]  # type: ignore
        page = Blocks([header, desc, *contents])  # type: ignore
        return str(page)

    @dispatch
    def render(self, el: layout.Section):  # type: ignore
        header = Header(self.header_level, el.title)

        with self._increment_header_level():
            contents = [self.render(c) for c in el.contents]  # type: ignore

        section = Blocks([header, el.desc, *contents])  # type: ignore
        return str(section)

    @dispatch
    def render(  # type: ignore
        self, el: layout.DocFunction | layout.DocAttribute
    ):
        title = self.render_header(el)
        signature = self.signature(el)  # type: ignore
        doc = self.render(el.obj)  # type: ignore
        return str(Blocks([title, signature, doc]))  # type: ignore

    # render griffe objects ---------------------------------------------------

    @dispatch
    def render(self, el: dc.Object | dc.Alias):  # type: ignore
        """
        Render high level objects representing functions, classes, etc
        """
        sections: list[Block] = []

        if el.docstring:
            patched_sections = qast.transform(el.docstring.parsed)
            # Parameters, Returns, Notes, See Also ... sections
            for section in patched_sections:  # type: ignore
                title = (section.title or section.kind.value).title()
                body = self.render(section)
                slug = title.lower().replace(" ", "-")
                section_classes = [f"doc-{slug}"]

                if title in ("Text", "Deprecated"):
                    content = Div(body, Attr(classes=section_classes))
                else:
                    header = Header(
                        self.header_level + 1,
                        title,
                        Attr(classes=section_classes),
                    )
                    content = Blocks([header, body])
                sections.append(content)

        return str(Blocks(sections))

    # signature parts ---------------------------------------------------------
    @dispatch
    def render(self, el: dc.Parameters) -> list[str]:  # type: ignore
        """
        All parameters in a function/ method signature

        i.e. The stuff in the brackets of func(a, b, c=3, d=4, **kwargs)
        """
        params: list[str] = []
        prev, cur = 0, 1
        state = (dc.ParameterKind.positional_or_keyword,) * 2

        for parameter in el:
            state = state[cur], parameter.kind
            append_transition_token = (
                state[prev] != state[cur]
                and state[prev] != dc.ParameterKind.var_positional
            )

            if append_transition_token:
                if state[cur] == dc.ParameterKind.positional_only:
                    params.append("/")
                if state[cur] == dc.ParameterKind.keyword_only:
                    params.append("*")

            params.append(self.render(parameter))  # type: ignore

        return params

    @dispatch
    def render(self, el: dc.Parameter):  # type: ignore
        """
        Parameter for the function/method signature

        i.e. A single item in the brackets of func(a, b, c=3, d=4, **kwargs)
        """
        if el.kind == dc.ParameterKind.var_keyword:
            name = f"**{el.name}"
        elif el.kind == dc.ParameterKind.var_positional:
            name = f"*{el.name}"
        else:
            name = el.name

        default = None
        if el.default is not None:
            variable_kind = {
                dc.ParameterKind.var_keyword,
                dc.ParameterKind.var_positional,
            }
            if el.kind not in variable_kind:
                default = el.default

        return build_signature_parameter(name, None, default)

    # render docstring parts --------------------------------------------------

    @dispatch
    def render(  # type: ignore
        self,
        el: (
            ds.DocstringSectionParameters
            | ds.DocstringSectionOtherParameters
            | ds.DocstringSectionReturns
            | ds.DocstringSectionYields
            | ds.DocstringSectionReceives
            | ds.DocstringSectionRaises
            | ds.DocstringSectionWarns
            | ds.DocstringSectionAttributes
        ),
    ):
        """
        Return parameters docstring as a definition list

        output-format: quarto/pandoc
        """
        list_items: list[DefinitionItem] = [
            self.render(ds_parameter)  # type: ignore
            for ds_parameter in el.value
        ]
        div = Div(
            DefinitionList(list_items),
            Attr(classes=["doc-definition-items"]),
        )
        return str(div)

    # text ----
    # note this can be a number of things. for example, opening docstring text,
    # or a section with a header not included in the numpydoc standard
    @dispatch
    def render(self, el: ds.DocstringSectionText):  # type: ignore
        new_el = qast.transform(el)
        if isinstance(new_el, ds.DocstringSectionText):
            # ensures we don't recurse forever
            return el.value

        return self.render(new_el)  # type: ignore

    @dispatch
    def render(self, el: ds.DocstringSectionDeprecated) -> str:  # type: ignore
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

    @dispatch
    def render(  # type: ignore
        self,
        el: (
            ds.DocstringParameter
            | ds.DocstringAttribute
            | ds.DocstringReturn
            | ds.DocstringYield
            | ds.DocstringReceive
            | ds.DocstringRaise
            | ds.DocstringWarn
        ),
    ) -> DefinitionItem:
        """
        Parse docstring elements that have definitions
        """
        name = getattr(el, "name", None) or ""
        annotation = self.render_annotation(el.annotation)  # type: ignore
        default = getattr(el, "default", None)
        term = build_docstring_parameter(name, annotation, default)

        # Annotations are expressed in html so that contained interlink
        # references can be processed. Pandoc does not recognise any form
        # of markup within backquotes `...`, but it does it the markup is
        # withing html code tags.
        return Code(term).html, el.description

    @dispatch
    def render(  # type: ignore
        self,
        el: qast.DocstringSectionSeeAlso,  # noqa: F811
    ):
        """
        Parse See Also

        https://numpydoc.readthedocs.io/en/latest/format.html#see-also
        """
        lines = el.value.split("\n")

        # each entry in result has form:
        # ([('func1', '<directive>'), ...], <description>)
        try:
            parsed_see_also_lines = NumpyDocString("")._parse_see_also(lines)
        except ValueError:
            return el.value

        list_items = []
        for interlink_refs, description_parts in parsed_see_also_lines:
            term_links = [
                str(interlink_ref_to_link(ref)) for ref in interlink_refs
            ]
            term = ", ".join(term_links)
            desc = " ".join(description_parts)
            list_items.append((term, desc))

        div = Div(
            DefinitionList(list_items),
            Attr(classes=["doc-definition-items"]),
        )
        return str(div)

    @dispatch
    def render(self, el: qast.DocstringSectionNotes):  # type: ignore
        return el.value

    # render examples ---------------------------------------------------------
    @dispatch
    def render(self, el: ds.DocstringSectionExamples):  # type: ignore
        content = [
            self.render(qast.transform(c))  # type: ignore
            for c in el.value
        ]
        return str(Blocks(content))

    @dispatch
    def render(self, el: qast.ExampleCode):  # type: ignore
        return str(CodeBlock(el.value, Attr(classes=["python"])))

    @dispatch
    def render(self, el: qast.ExampleText):
        return el.value

    # summarize method --------------------------------------------------------

    @dispatch
    def summarize(self, el):  # type: ignore
        """Produce a summary table."""
        raise NotImplementedError(f"Unsupported type: {type(el)}")

    @dispatch
    def summarize(self, el: layout.Layout) -> Block:  # type: ignore
        """
        Summarize a Layout

        A Layout consists of a sequence of layout sections and/or layout pages
        """
        return Blocks([self.summarize(s) for s in el.sections])  # type: ignore

    @dispatch
    def summarize(self, el: layout.Section) -> Block:  # type: ignore
        """
        Summarize a section of content on the reference index page
        """
        desc = el.desc or ""
        header = ""
        content = ""

        if el.title:
            header = Header(2, f"{el.title}", Attr(classes=["doc-summary"]))
        elif el.subtitle:
            header = Header(
                3, f"{el.subtitle}", Attr(classes=["doc-summary-subgroup"])
            )

        if el.contents:
            rows: list[SummaryRow] = []
            for child in el.contents:
                rows.extend(self.summarize(child))  # type: ignore
            content = Div(
                str(tabulate(rows, tablefmt="grid")),
                Attr(classes=["doc-summary-table"]),
            )

        return Blocks([header, desc, content])

    @dispatch
    def summarize(self, el: layout.Page) -> list[SummaryRow]:  # type: ignore
        """
        Summarize a Page that is part of a Layout
        """
        if el.summary is not None:
            link = Link(markdown_escape(el.summary.name), f"{el.path}.qmd")
            return [(str(link), el.summary.desc)]

        if len(el.contents) > 1 and not el.flatten:
            raise ValueError(
                "Cannot summarize Page. Either set its `summary` attribute "
                "with name and description details, or set `flatten` to True."
            )

        items: list[SummaryRow] = [
            self.summarize(c, el.path)  # type: ignore
            for c in el.contents
        ]
        return items

    @dispatch
    def summarize(self, el: layout.MemberPage) -> tuple[str, str]:  # type: ignore
        # TODO: model should validate these only have a single entry
        return self.summarize(el.contents[0], el.path)  # type: ignore

    @dispatch
    def summarize(  # type: ignore
        self, el: layout.Doc, path: Optional[str] = None
    ) -> tuple[str, str]:
        # TODO: assumes that files end with .qmd
        path = f"{path}.qmd" if path else ""
        link = Link(markdown_escape(el.name), f"{path}#{el.anchor}")
        description = self.summarize(el.obj)  # type: ignore
        return (str(link), description)

    @dispatch
    def summarize(self, el: layout.Link) -> tuple[str, str]:  # type: ignore
        """
        Summarise a layout Link to an interlink reference

        Returns an interlink and a description of the object/reference
        """
        link = InterLink(None, markdown_escape(el.name))
        description = self.summarize(el.obj)
        return (str(link), description)

    @dispatch
    def summarize(self, obj: dc.Object | dc.Alias) -> str:
        """
        One line description of an object

        This is the first line of a docstring
        """
        parts = obj.docstring.parsed if obj.docstring else []
        section = parts[0] if parts else None
        if isinstance(section, ds.DocstringSectionText):
            return section.value.split("\n")[0]

        return ""

    def _pages_written(self, builder):
        """
        Render typing information and the interlinks
        """
        mods = TypingModules(self, builder)
        mods.render_information_pages()

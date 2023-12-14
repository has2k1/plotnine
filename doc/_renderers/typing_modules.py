from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import cast

from griffe import dataclasses as dc
from quartodoc import layout
from quartodoc.autosummary import Builder, get_object
from quartodoc.pandoc.blocks import (
    Block,
    Blocks,
    Div,
    Header,
)
from quartodoc.pandoc.components import Attr
from quartodoc.pandoc.inlines import Code, Inlines
from quartodoc.renderers.base import Renderer

from .format import interlink_identifiers, pretty_code
from .utils import is_protocol, is_typealias, make_doc_labels


@dataclass
class TypingModule:
    """
    Make document items out of the type aliases in a module

    Parameters
    ----------
    module_path :
        Qualified path to module
    builder :
        The current quartodoc builder
    """

    module_path: str
    renderer: Renderer
    builder: Builder

    def __post_init__(self):
        self.package = self.builder.package
        self.dir = self.builder.dir

    @cached_property
    def base_uri(self) -> str:
        """
        Relative base filepath (w.r.t) to the build directory

        It does not have an extenstion.

        With the right extensions, this is where:
            - the module's aliases should be written (.qmd)
            - the interlinks should point (.html#anchor)
        """
        path = self.module_path
        if path.startswith(self.package):
            path = path[len(self.package) + 1 :]
        return f"{self.dir}/{path}"

    @cached_property
    def obj(self):
        """
        Module griffe object
        """
        return get_object(self.module_path)

    def _make_items(
        self,
        obj_it: Iterable[dc.Object],
    ) -> list[layout.Item]:
        """
        Return items of typing objects
        """
        items = [
            layout.Item(
                name=obj.canonical_path,
                obj=obj,
                uri=f"{self.base_uri}.html#{obj.canonical_path}",
                dispname=obj.canonical_path,
            )
            for obj in obj_it
        ]
        return items

    @cached_property
    def typealias_documentation_items(self) -> list[layout.Item]:
        """
        TypeAliases that should be documentation items and interlinked
        """
        typealiases = (
            obj for obj in self.obj.attributes.values() if is_typealias(obj)
        )
        return self._make_items(typealiases)

    @cached_property
    def protocol_documentation_items(self) -> list[layout.Item]:
        """
        Typing Protocols that should be documentation items and interlinked
        """
        protocols = (
            obj for obj in self.obj.classes.values() if is_protocol(obj)
        )
        return self._make_items(protocols)

    def render_information_page(self):
        """
        Render a typing information page for a single typing module
        """
        title = Header(
            level=1,
            content="Typing Information",
            attr=Attr(classes=["doc", "doc-typing"]),
        )
        page_content: list[Block] = [title]

        protocol_items = self.protocol_documentation_items
        if protocol_items:
            content = ProtocolsDoc(protocol_items, self.renderer).render()
            page_content.append(content)
            self.builder.items.extend(protocol_items)

        typealias_items = self.typealias_documentation_items
        if typealias_items:
            content = TypeAliasesDoc(typealias_items).render()
            page_content.append(content)
            self.builder.items.extend(typealias_items)

        filepath = Path(self.base_uri).with_suffix(".qmd")
        filepath.write_text(str(Blocks(page_content)))


@dataclass
class TypingModules(list[TypingModule]):
    """
    A collection of TypingModules
    """

    renderer: Renderer
    builder: Builder

    def __post_init__(self):
        """
        Create the list from the module_paths
        """
        for module_path in self.renderer.typing_module_paths:  # type: ignore
            self.append(TypingModule(module_path, self.renderer, self.builder))

    def render_information_pages(self):
        """
        Render all typing information pages
        """
        for typing_module in self:
            typing_module.render_information_page()


@dataclass
class ProtocolDoc:
    """
    Document a single Protocol
    """

    obj: dc.Class
    """Protocol Object"""

    renderer: Renderer
    """Renderer that is documenting the package"""

    def __post_init__(self):
        """
        Create layout.Doc object for the Protocol
        """
        from_griffe = layout.Doc.from_griffe
        members = [from_griffe(m.name, m) for m in self.obj.members.values()]
        self.doc = from_griffe(self.obj.name, self.obj, members)

    def render(self) -> Block:
        """
        Return the documentation
        """
        with self.renderer._increment_header_level(2):  # type: ignore
            res = self.renderer.render(self.doc)
        return Blocks([res])


@dataclass
class ProtocolsDoc(list[ProtocolDoc]):
    """
    Document Protocols for the type information page
    """

    items: list[layout.Item]
    """Documentation Items with Protocol objects"""

    renderer: Renderer
    """Renderer that is documenting the package"""

    def __post_init__(self):
        """
        Create the list of TypingProtocol
        """
        for item in self.items:
            obj = cast(dc.Class, item.obj)
            self.append(ProtocolDoc(obj, self.renderer))

    def render(self) -> Block:
        """
        Return the documentation for all the Protocols
        """
        if not self:
            return Blocks([])

        title = Header(
            level=2,
            content="Protocols",
            attr=Attr(classes=["doc", "doc-typing-protocols"]),
        )
        definitions = [tpd.render() for tpd in self]
        return Blocks([title, definitions])


@dataclass
class TypeAliasDoc:
    """
    Document a single TypeAlias
    """

    obj: dc.Attribute
    """TypeAlias Object"""

    def __post_init__(self):
        """
        Create layout.Doc object for the Protocol
        """
        from_griffe = layout.Doc.from_griffe
        members = [from_griffe(m.name, m) for m in self.obj.members.values()]
        self.doc = from_griffe(self.obj.name, self.obj, members)

    def render(self) -> Block:
        """
        Return the documentation
        """
        header = Header(
            level=3,
            content=Inlines(
                [self.obj.name, make_doc_labels(["typing-typealias"])]
            ),
            attr=Attr(
                self.obj.canonical_path, classes=["doc-typing-typealias"]
            ),
        )
        stmt = interlink_identifiers(self.obj)
        value = stmt[stmt.find("=") + 1 :].strip()
        definition = Div(
            Code(
                pretty_code(value),
                Attr(classes=["doc-typing-typealias-definition"]),
            ).html,
            Attr(classes=["sourceCode"]),
        )
        return Blocks([header, definition])


@dataclass
class TypeAliasesDoc(list[TypeAliasDoc]):
    """
    Document multiple TypeAliases
    """

    items: list[layout.Item]
    """Documentation Items with TypeAlias objects"""

    def __post_init__(self):
        """
        Create list of TypeAlias
        """
        for item in self.items:
            obj = cast(dc.Attribute, item.obj)
            self.append(TypeAliasDoc(obj))

    def render(self) -> Blocks:
        """
        Return the documentation for all the Protocols
        """
        if not self:
            return Blocks([])

        title = Header(
            level=2,
            content="Type Aliases",
            attr=Attr(classes=["doc", "doc-typing-typealiases"]),
        )
        definitions = [t.render() for t in self]
        return Blocks([title, definitions])

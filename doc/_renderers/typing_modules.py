from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import cast

from griffe import dataclasses as dc
from griffe import expressions as expr
from quartodoc import layout
from quartodoc.autosummary import Builder, get_object
from quartodoc.pandoc.blocks import (
    Block,
    Blocks,
    CodeBlock,
    Div,
    Header,
)
from quartodoc.pandoc.components import Attr
from quartodoc.pandoc.inlines import Code, Inlines

from .format import interlink_identifiers, pretty_code, repr_obj
from .utils import make_doc_labels


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
    builder: Builder

    @cached_property
    def base_uri(self) -> str:
        """
        Relative base filepath (w.r.t) to the build directory

        It does not have an extenstion.

        With the right extensions, this is where:
            - the module's aliases should be written (.qmd)
            - the interlinks should point (.html#anchor)
        """
        dir = self.builder.dir
        package = self.builder.package
        path = self.module_path
        if path.startswith(package):
            path = path[len(package) + 1 :]
        return f"{dir}/{path}"

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
            _title = Header(
                level=2,
                content="Protocols",
                attr=Attr(classes=["doc", "doc-typing-protocols"]),
            )
            _definitions = render_protocol_definitions(protocol_items)

            page_content.extend([_title, _definitions])
            self.builder.items.extend(protocol_items)

        typealias_items = self.typealias_documentation_items
        if typealias_items:
            _title = Header(
                level=2,
                content="Type Aliases",
                attr=Attr(classes=["doc", "doc-typing-typealiases"]),
            )
            _definitions = render_typealias_definitions(typealias_items)

            page_content.extend([_title, _definitions])
            self.builder.items.extend(typealias_items)

        filepath = Path(self.base_uri).with_suffix(".qmd")
        filepath.write_text(str(Blocks(page_content)))


@dataclass
class TypingModules(list[TypingModule]):
    """
    A collection of TypingModules
    """

    module_paths: list[str]
    builder: Builder

    def __post_init__(self):
        """
        Create the list from the module_paths
        """
        for module_path in self.module_paths:
            self.append(TypingModule(module_path, self.builder))

    def render_information_pages(self):
        """
        Render all typing information pages
        """
        for typing_module in self:
            typing_module.render_information_page()


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
        and isinstance(obj.bases[-1], expr.ExprName)
        and obj.bases[-1].canonical_path == "typing.Protocol"
    )


def render_typealias_definition(el: dc.Object | dc.Alias) -> Div:
    """
    Turn the code that defines a TypeAlias into markdown
    """
    if isinstance(el, dc.Attribute):
        content = pretty_code(interlink_identifiers(el))
    else:
        content = str(el)
    return Div(
        Code(content, Attr(classes=["doc-typing-typealias-definition"])).html,
        Attr(classes=["sourceCode"]),
    )


def render_typealias_definitions(items: list[layout.Item]) -> Blocks:
    """
    Turn TypeAliases into markdown
    """
    aliases = []
    Header(1, content=[Code("a")])

    for item in items:
        header = Header(
            level=3,
            content=Inlines(
                [item.obj.name, make_doc_labels(["typing-typealias"])]
            ),
            attr=Attr(
                item.obj.canonical_path, classes=["doc-typing-typealias"]
            ),
        )

        definition = render_typealias_definition(item.obj)

        if item.obj.docstring:
            docstring = Div(
                item.obj.docstring.value,
                Attr(classes=["doc-typing-typealias-docstring"]),
            )
        else:
            docstring = ""

        aliases.extend([header, definition, docstring])

    return Blocks(aliases)


def render_protocol_definition(el: dc.Class) -> CodeBlock:
    """
    Turn the code that a TypeAlias into markdown
    """
    return CodeBlock(el.source, Attr(classes=["python"]))


def render_protocol_definitions(items: list[layout.Item]) -> Blocks:
    """
    Turn Typing Protocols into markdown
    """
    protocols = []

    for item in items:
        header = Header(
            level=3,
            content=Inlines(
                [item.obj.name, make_doc_labels(["typing-protocol"])]
            ),
            attr=Attr(
                item.obj.canonical_path, classes=["doc-typing-protocol"]
            ),
        )
        obj = cast(dc.Class, item.obj)
        definition = render_protocol_definition(obj)
        protocols.extend([header, definition])

    return Blocks(protocols)

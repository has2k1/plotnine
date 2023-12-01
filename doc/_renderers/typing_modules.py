from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

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
from quartodoc.pandoc.inlines import Code

from .format import interlink_identifiers, pretty_code, repr_obj


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

    @cached_property
    def typealias_documentation_items(self) -> list[layout.Item]:
        """
        Documentation items that should be added to the interlinks
        inventory.
        """
        mod = self.obj
        typealiases = (
            obj for obj in self.obj.attributes.values() if is_typealias(obj)
        )

        items = [
            layout.Item(
                name=obj.canonical_path,
                obj=obj,
                uri=f"{self.base_uri}.html#{obj.canonical_path}",
                dispname=obj.canonical_path,
            )
            for obj in typealiases
        ]
        return items

    def render_information_page(self):
        """
        Render a typing information page for a single typing module
        """
        items = self.typealias_documentation_items

        title = Header(
            level=1,
            content="Typing Information",
            attr=Attr(classes=["doc", "doc-typing"]),
        )

        typealias_definitions = render_typealias_definitions(items)
        content = str(Blocks([title, typealias_definitions]))
        Path(self.base_uri).with_suffix(".qmd").write_text(content)
        self.builder.items.extend(items)


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


def render_typealias_definition(el: dc.Object | dc.Alias) -> Div:
    """
    Turn the code that defines a TypeAlias into markdown
    """
    if isinstance(el, dc.Attribute):
        content = pretty_code(interlink_identifiers(el))
    else:
        content = str(el)
    return Div(Code(content).html, Attr(classes=["sourceCode"]))


def render_typealias_definitions(items: list[layout.Item]) -> Blocks:
    """
    Turn TypeAliases into markdown
    """
    aliases = []

    for item in items:
        header = Header(
            level=3,
            content=item.obj.name,
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

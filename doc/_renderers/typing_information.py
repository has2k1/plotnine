from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, cast

from quartodoc import layout
from quartodoc.autosummary import Builder, get_object
from quartodoc.pandoc.blocks import (
    Block,
    BlockContent,
    Blocks,
    Header,
)

from .pandoc.blocks import Meta
from .render import (
    RenderDocAttribute,
    RenderDocClass,
    get_render_type,
)
from .utils import griffe_to_doc, is_protocol, is_typealias, is_typevar

if TYPE_CHECKING:
    from griffe import dataclasses as dc

    from .numpydoc import NumpyDocRenderer


@dataclass
class TypeSections(Block):
    protocols_items: list[layout.Item]
    typevars_items: list[layout.Item]
    typealiases_items: list[layout.Item]
    renderer: NumpyDocRenderer

    def __post_init__(self):
        def make_render(item: layout.Item):
            """
            Create RenderDoc object
            """
            docable = griffe_to_doc(item.obj)
            return get_render_type(docable)(docable, self.renderer, 3)

        self.typevars_renders = cast(
            list[RenderDocAttribute],
            [make_render(item) for item in self.typevars_items],
        )
        self.protocols_renders = cast(
            list[RenderDocClass],
            [make_render(item) for item in self.protocols_items],
        )
        self.typealiases_renders = cast(
            list[RenderDocAttribute],
            [make_render(item) for item in self.typealiases_items],
        )

        # Turn off unnessary information
        for r in self.protocols_renders:
            r.show_members_summary = False

        for r in self.typevars_renders:
            r.show_signature_name = False

        for r in self.typealiases_renders:
            r.show_signature_name = False
            r.show_signature_annotation = False

    def __str__(self):
        return str(self.render_body())

    @cached_property
    def items(self) -> list[layout.Item]:
        """
        Return all type information items
        """
        return [
            *self.protocols_items,
            *self.typevars_items,
            *self.typealiases_items,
        ]

    def render_body(self) -> BlockContent:
        content: list[Block | str] = []

        if self.protocols_renders:
            content.extend(
                [
                    Header(2, "Protocols"),
                    *[str(r) for r in self.protocols_renders],
                ]
            )

        if self.typevars_renders:
            content.extend(
                [
                    Header(2, "Type Variables"),
                    *[str(r) for r in self.typevars_renders],
                ]
            )

        if self.typealiases_renders:
            content.extend(
                [
                    Header(2, "Type Aliases"),
                    *[str(r) for r in self.typealiases_renders],
                ]
            )

        return Blocks(content)


@dataclass
class TypeInformation(Block):
    module_path: str
    renderer: NumpyDocRenderer
    builder: Builder

    def __post_init__(self):
        self.package = self.builder.package
        self.dir = self.builder.dir

    def __str__(self):
        return str(self.content)

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
    def sections(self) -> TypeSections:
        def make_item(obj: dc.Object | dc.Alias) -> layout.Item:
            """
            Return item of typing object
            """
            return layout.Item(
                name=obj.canonical_path,
                obj=obj,
                uri=f"{self.base_uri}.html#{obj.canonical_path}",
                dispname=obj.canonical_path,
            )

        members = list(get_object(self.module_path).members.values())
        return TypeSections(
            protocols_items=[make_item(m) for m in members if is_protocol(m)],
            typevars_items=[make_item(m) for m in members if is_typevar(m)],
            typealiases_items=[
                make_item(m) for m in members if is_typealias(m)
            ],
            renderer=self.renderer,
        )

    @cached_property
    def content(self) -> BlockContent:
        meta = Meta({"title": "Typing Information"})
        return Blocks([meta, self.sections])

    def write(self):
        """
        Write typing information to qmd file
        """
        self.builder.items.extend(self.sections.items)
        filepath = Path(self.base_uri).with_suffix(".qmd")
        filepath.write_text(str(self))

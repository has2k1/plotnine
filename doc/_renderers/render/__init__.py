from typing import Type, TypeAlias, overload

from quartodoc.layout import (
    DocAttribute,
    DocClass,
    DocFunction,
    DocModule,
    Layout,
    Link,
    Page,
    Section,
)

from .doc import RenderDoc
from .docattribute import RenderDocAttribute
from .docclass import RenderDocClass
from .docfunction import RenderDocFunction
from .docmodule import RenderDocModule
from .extending import extend_base_class
from .layout import RenderLayout
from .mixin_call import RenderDocCallMixin
from .mixin_members import RenderDocMembersMixin
from .page import RenderPage
from .section import RenderSection

__all__ = (
    "RenderDoc",
    "RenderDocClass",
    "RenderDocFunction",
    "RenderDocAttribute",
    "RenderDocModule",
    "RenderDocCallMixin",
    "RenderDocMembersMixin",
    "RenderLayout",
    "RenderPage",
    "RenderSection",
    "extend_base_class",
)

Documentable: TypeAlias = (
    # _Docable, Doc
    DocClass
    | DocFunction
    | DocAttribute
    | DocModule
    # _Docable
    | Link
    # Structual
    | Page
    | Section
    | Layout
)

RenderObjType: TypeAlias = (
    RenderDoc
    | RenderDocClass
    | RenderDocFunction
    | RenderDocAttribute
    | RenderDocModule
    | RenderLayout
    | RenderPage
    | RenderSection
)

_class_mapping: dict[Type[Documentable], Type[RenderObjType]] = {
    DocClass: RenderDocClass,
    DocFunction: RenderDocFunction,
    DocAttribute: RenderDocAttribute,
    DocModule: RenderDocModule,
    Layout: RenderLayout,
    Page: RenderPage,
    Section: RenderSection,
}


@overload
def get_render_type(obj: DocClass) -> Type[RenderDocClass]:
    ...


@overload
def get_render_type(obj: DocFunction) -> Type[RenderDocFunction]:
    ...


@overload
def get_render_type(obj: DocAttribute) -> Type[RenderDocAttribute]:
    ...


@overload
def get_render_type(obj: DocModule) -> Type[RenderDocModule]:
    ...


@overload
def get_render_type(obj: Layout) -> Type[RenderLayout]:
    ...


@overload
def get_render_type(obj: Page) -> Type[RenderPage]:
    ...


@overload
def get_render_type(obj: Section) -> Type[RenderSection]:
    ...


def get_render_type(obj: Documentable) -> Type[RenderObjType]:
    if type(obj) in _class_mapping:
        return _class_mapping[type(obj)]
    else:
        msg = f"Cannot document object of type {type(obj)}"
        raise ValueError(msg)

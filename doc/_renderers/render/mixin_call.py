from __future__ import annotations

from typing import TYPE_CHECKING, cast

from griffe import dataclasses as dc
from quartodoc import layout
from quartodoc.pandoc.blocks import (
    CodeBlock,
    DefinitionItem,
    DefinitionList,
    Div,
)
from quartodoc.pandoc.components import Attr
from quartodoc.pandoc.inlines import Code

from ..format import formatted_signature, repr_obj
from ..typing import DocstringSectionWithDefinitions  # noqa: TCH001
from .doc import RenderDoc

if TYPE_CHECKING:
    from ..typing import DocstringDefinitionType


class __RenderDocCallMixin(RenderDoc):
    """
    Mixin to render Doc objects that can be called

    i.e. classes (for the __init__ method) and functions/methods
    """

    def __post_init__(self):
        super().__post_init__()
        self.doc = cast(layout.DocFunction | layout.DocClass, self.doc)
        self.obj = cast(dc.Function, self.obj)

    @RenderDoc.render_section.register  # type: ignore
    def _(self, el: DocstringSectionWithDefinitions):
        """
        Render docstring sections that have a list of definitions

        e.g. Parameters, Other Parameters, Returns, Yields, Receives,
             Warns, Attributes
        """

        def render_section_item(el: DocstringDefinitionType) -> DefinitionItem:
            """
            Render a single definition in a section
            """
            name = getattr(el, "name", None) or ""
            default = getattr(el, "default", None)
            annotation = (
                str(self.render_annotation(el.annotation))
                if el.annotation
                else None
            )
            term = str(
                self.render_variable_definition(name, annotation, default)
            )

            # Annotations are expressed in html so that contained interlink
            # references can be processed. Pandoc does not process any markup
            # within backquotes `...`, but it does if the markup is within
            # html code tags.
            return Code(term).html, el.description

        items = [render_section_item(item) for item in el.value]
        return Div(
            DefinitionList(items),
            Attr(classes=["doc-definition-items"]),
        )

    def get_function_parameters(self) -> dc.Parameters:
        """
        Return the parameters of the function
        """
        obj = self.obj

        # adapted from mkdocstrings-python jinja tempalate
        if not len(obj.parameters) > 0 or not obj.parent:
            return obj.parameters

        param = obj.parameters[0].name
        omit_first_parameter = (
            obj.parent.is_class and param in ("self", "cls")
        ) or (obj.parent.is_module and obj.is_class and param == "self")

        if omit_first_parameter:
            return dc.Parameters(*list(obj.parameters)[1:])

        return obj.parameters

    def render_signature(self):
        name = self.signature_name if self.show_signature_name else ""
        sig = formatted_signature(name, self.render_signature_parameters())
        return Div(
            CodeBlock(sig, Attr(classes=["py"])),
            Attr(classes=["doc-signature"]),
        )

    def render_signature_parameters(self) -> list[str]:
        """
        Render parameters in a function / method signature

        i.e. The stuff in the brackets of func(a, b, c=3, d=4, **kwargs)
        """
        parameters = self.get_function_parameters()

        params: list[str] = []
        prev, cur = 0, 1
        state = (dc.ParameterKind.positional_or_keyword,) * 2

        for parameter in parameters:
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

            params.append(self.render_signature_parameter(parameter))
        return params

    def render_signature_parameter(self, el: dc.Parameter) -> str:
        """
        Parameter for the function/method signature

        This is a single item in the brackets of

            func(a, b, c=3, d=4, **kwargs)

        """
        default = None
        if el.kind == dc.ParameterKind.var_keyword:
            name = f"**{el.name}"
        elif el.kind == dc.ParameterKind.var_positional:
            name = f"*{el.name}"
        else:
            name = el.name
            if el.default is not None:
                default = el.default

        if self.show_signature_annotation and el.annotation is not None:
            annotation, equals = f" : {el.annotation}", " = "
        else:
            annotation, equals = "", "="

        default = (default and f"{equals}{repr_obj(default)}") or ""
        return f"{name}{annotation}{default}"


class RenderDocCallMixin(__RenderDocCallMixin):
    """
    Extend Rendering of objects that can be called
    """

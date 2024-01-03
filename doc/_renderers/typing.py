from __future__ import annotations

from typing import Literal, TypeAlias

import griffe.expressions as expr
from griffe.docstrings import dataclasses as ds
from quartodoc.layout import (
    Doc,
    DocAttribute,
    DocClass,
    DocFunction,
    DocModule,
    Link,
    MemberPage,
)

DisplayNameFormat: TypeAlias = Literal[
    "full", "name", "short", "relative", "canonical"
]
DocObjectKind: TypeAlias = Literal[
    "module",
    "class",
    "method",
    "function",
    "attribute",
    "alias",
    "type",
    "typevar",
]

DocstringSectionWithDefinitions: TypeAlias = (
    ds.DocstringSectionParameters
    | ds.DocstringSectionOtherParameters
    | ds.DocstringSectionReturns
    | ds.DocstringSectionYields
    | ds.DocstringSectionReceives
    | ds.DocstringSectionRaises
    | ds.DocstringSectionWarns
    | ds.DocstringSectionAttributes
)

DocstringDefinitionType: TypeAlias = (
    ds.DocstringParameter
    | ds.DocstringAttribute
    | ds.DocstringReturn
    | ds.DocstringYield
    | ds.DocstringReceive
    | ds.DocstringRaise
    | ds.DocstringWarn
)

Annotation: TypeAlias = str | expr.Expr

DocType: TypeAlias = DocClass | DocFunction | DocAttribute | DocModule

DocMemberType: TypeAlias = MemberPage | Doc | Link

SummaryItem: TypeAlias = tuple[str, str]

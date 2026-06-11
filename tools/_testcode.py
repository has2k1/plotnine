"""
Static extraction of the test code behind an image-comparison test

An image-comparison test identifies its image with a string literal,
``assert p == "params"`` (see ``tests/conftest.py``). Given that name,
this module recovers a readable snippet: the test function together
with the class-level and module-level assignments it relies on.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["CodeSnippet", "extract_test_code", "get_test_code"]

FunctionNode = ast.FunctionDef | ast.AsyncFunctionDef


@dataclass(frozen=True)
class CodeSnippet:
    """
    Test code that produced an image, ready for display

    Not named ``Test*`` so pytest never tries to collect it.
    """

    source: str
    """Assembled snippet: setup assignments, then the test function"""

    lineno: int
    """Line in the test file where the test function starts"""


def extract_test_code(source: str, name: str) -> CodeSnippet | None:
    """
    Extract the code of the test that creates image `name`

    Parameters
    ----------
    source :
        Contents of a test file.
    name :
        Identifier of the test image, i.e. the string the plot is
        compared against.

    Returns
    -------
    :
        The snippet, or None when `source` does not parse or no test
        function mentions `name`.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    return _extract(source, tree, name)


def get_test_code(test_file: Path, name: str) -> CodeSnippet | None:
    """
    Extract the code of the test in `test_file` that creates image `name`

    Returns None when the file is missing or unparseable. Files are
    read and parsed once per process.
    """
    parsed = _parse_file(test_file)
    if parsed is None:
        return None
    source, tree = parsed
    return _extract(source, tree, name)


@lru_cache(maxsize=None)
def _parse_file(test_file: Path) -> tuple[str, ast.Module] | None:
    try:
        source = test_file.read_text(encoding="utf-8")
        return source, ast.parse(source)
    except (OSError, SyntaxError):
        return None


def _extract(source: str, tree: ast.Module, name: str) -> CodeSnippet | None:
    lines = source.split("\n")
    found = _find_test_function(tree, name)
    if found is None:
        return None
    func, cls = found

    loaded = _loaded_names(func)
    chunks = [
        _segment(lines, stmt)
        for targets, stmt in _module_assignments(tree)
        if targets & loaded
    ]

    if cls is None:
        chunks.append(_segment(lines, func))
    else:
        class_chunks = [
            _segment(lines, stmt)
            for stmt in cls.body
            if isinstance(stmt, (ast.Assign, ast.AnnAssign))
        ]
        body = "\n\n".join([*class_chunks, _segment(lines, func)])
        chunks.append(f"class {cls.name}:\n{body}")

    return CodeSnippet(source="\n\n".join(chunks), lineno=func.lineno)


def _find_test_function(
    tree: ast.Module, name: str
) -> tuple[FunctionNode, ast.ClassDef | None] | None:
    """
    The test function that identifies its image as `name`

    A function comparing a plot to `name` wins; a function that merely
    contains the string (e.g. in a list of names) is the fallback.
    """
    constant_match = None
    for func, cls in _iter_functions(tree):
        in_compare, as_constant = _name_mentions(func, name)
        if in_compare:
            return func, cls
        if as_constant and constant_match is None:
            constant_match = (func, cls)
    return constant_match


def _iter_functions(
    tree: ast.Module,
) -> list[tuple[FunctionNode, ast.ClassDef | None]]:
    """
    Test-file functions paired with their enclosing class (if any)
    """
    out: list[tuple[FunctionNode, ast.ClassDef | None]] = []
    for stmt in tree.body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append((stmt, None))
        elif isinstance(stmt, ast.ClassDef):
            out.extend(
                (sub, stmt)
                for sub in stmt.body
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef))
            )
    return out


def _name_mentions(func: FunctionNode, name: str) -> tuple[bool, bool]:
    """
    How `func` mentions `name`: (in a comparison, as any constant)
    """
    in_compare = False
    as_constant = False
    for node in ast.walk(func):
        if isinstance(node, ast.Constant) and node.value == name:
            as_constant = True
        if isinstance(node, ast.Compare):
            operands = [node.left, *node.comparators]
            if any(
                isinstance(o, ast.Constant) and o.value == name
                for o in operands
            ):
                in_compare = True
    return in_compare, as_constant


def _loaded_names(func: FunctionNode) -> set[str]:
    """
    Names that `func` reads, i.e. its candidate setup dependencies
    """
    return {
        node.id
        for node in ast.walk(func)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }


def _module_assignments(
    tree: ast.Module,
) -> list[tuple[set[str], ast.stmt]]:
    """
    Module-level assignments as (target names, statement) pairs
    """
    out: list[tuple[set[str], ast.stmt]] = []
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            targets = {t.id for t in stmt.targets if isinstance(t, ast.Name)}
        elif isinstance(stmt, ast.AnnAssign) and isinstance(
            stmt.target, ast.Name
        ):
            targets = {stmt.target.id}
        else:
            continue
        if targets:
            out.append((targets, stmt))
    return out


def _segment(lines: list[str], node: ast.stmt) -> str:
    """
    Source text of `node`, including any decorators
    """
    start = node.lineno
    for deco in getattr(node, "decorator_list", []):
        start = min(start, deco.lineno)
    return "\n".join(lines[start - 1 : node.end_lineno])

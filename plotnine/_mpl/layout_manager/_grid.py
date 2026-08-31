from __future__ import annotations

from dataclasses import InitVar, dataclass
from typing import (
    TYPE_CHECKING,
    Callable,
    Generic,
    Literal,
    Sequence,
    TypeVar,
    overload,
)

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Iterator

    from plotnine.typing import Side

T = TypeVar("T")

Rect = tuple[int, int, int, int]
"""Inclusive (r0, r1, c0, c1) rectangle in grid coordinates."""


@dataclass
class Grid(Generic[T]):
    """
    Rectangular grid of items that occupy individual cells

    Items fill the grid in row-major or column-major order. Unfilled cells
    contain `None`.
    """

    nrow: InitVar[int]
    """Number of rows in the grid"""

    ncol: InitVar[int]
    """Number of columns in the grid"""

    items: InitVar[Sequence[T]]
    """Items to place in the grid"""

    order: InitVar[Literal["row_major", "col_major"]] = "row_major"
    """Order in which to fill the cells"""

    def __post_init__(
        self,
        nrow: int,
        ncol: int,
        items: Sequence[T],
        order: Literal["row_major", "col_major"],
    ):
        self._grid = np.empty((nrow, ncol), dtype=object)

        r, c = 0, 0
        if order == "row_major":
            for item in items:
                self[r, c] = item
                c += 1
                if c >= ncol:
                    r, c = r + 1, 0
        else:
            for item in items:
                self[r, c] = item
                r += 1
                if r >= nrow:
                    r, c = 0, c + 1

    @overload
    def __getitem__(self, index: tuple[int, int]) -> T | None: ...

    @overload
    def __getitem__(self, index: tuple[int, slice]) -> list[T | None]: ...

    @overload
    def __getitem__(self, index: tuple[slice, int]) -> list[T | None]: ...

    @overload
    def __getitem__(
        self,
        index: tuple[slice, slice],
    ) -> list[list[T | None]]: ...

    def __getitem__(
        self, index: tuple[int | slice, int | slice]
    ) -> T | None | list[T | None] | list[list[T | None]]:
        """
        Access grid items with 2D indexing:
        """
        return self._grid[index]  # pyright: ignore[reportReturnType]

    def __setitem__(
        self,
        index: tuple[int | slice, slice | int],
        value: T | None | list[T | None] | list[list[T | None]],
    ) -> None:
        self._grid[index] = value

    def iter_rows(self) -> Iterator[list[T | None]]:
        """
        Row by row
        """
        n = self._grid.shape[0]
        for row in range(n):
            yield self[row, :]

    def iter_cols(self) -> Iterator[list[T | None]]:
        """
        Column by column
        """
        n = self._grid.shape[1]
        for col in range(n):
            yield self[:, col]

    def reduce_cols(
        self,
        fn: Callable[[T], float],
        default: float,
    ) -> list[float]:
        """
        One value per column: the largest `fn(item)` in that column

        Parameters
        ----------
        fn
            Mapping from an item to the numeric value being compared.
        default
            Value used for columns whose cells are all None.

        Returns
        -------
        out
            One value per column, in left-to-right order.
        """
        out: list[float] = []
        for c in range(self._grid.shape[1]):
            items = [n for n in self[:, c] if n is not None]
            out.append(max(fn(n) for n in items) if items else default)
        return out

    def reduce_rows(
        self,
        fn: Callable[[T], float],
        default: float,
    ) -> list[float]:
        """
        One value per row: the largest `fn(item)` in that row

        Parameters
        ----------
        fn
            Mapping from an item to the numeric value being compared.
        default
            Value used for rows whose cells are all None.

        Returns
        -------
        out
            One value per row, in top-to-bottom order.
        """
        out: list[float] = []
        for r in range(self._grid.shape[0]):
            items = [n for n in self[r, :] if n is not None]
            out.append(max(fn(n) for n in items) if items else default)
        return out

    def items_on_edge(
        self,
        side: Side,
        idx: int,
    ) -> list[T]:
        """
        Items whose `side` edge sits at row/col `idx`

        In a grid where no item spans more than one cell, an item in
        row `r` has both its top and bottom edges at row `r`, and
        analogously for columns; so all four sides return the same
        items for that row or column.

        Parameters
        ----------
        side
            Which edge of an item to match: `"top"` and `"bottom"`
            select by row, `"left"` and `"right"` select by column.
        idx
            Row index when `side` is `"top"` or `"bottom"`; column
            index when `side` is `"left"` or `"right"`.

        Returns
        -------
        out
            The matching items, with None cells filtered out.
        """
        cells = self[idx, :] if side in ("top", "bottom") else self[:, idx]
        return [n for n in cells if n is not None]

    def _rect_of(self, item: T) -> Rect:
        """
        Return the inclusive cell bounds occupied by an item

        Return the first matching cell when the same object occupies
        more than one cell.

        Parameters
        ----------
        item
            Item to find. Identity matching supports objects with custom
            equality.

        Returns
        -------
        out
            Inclusive `(r0, r1, c0, c1)` cell bounds.

        Raises
        ------
        ValueError
            If the item is not in the grid.
        """
        nrow, ncol = self._grid.shape
        for r in range(nrow):
            for c in range(ncol):
                if self._grid[r, c] is item:
                    return (r, r, c, c)
        raise ValueError(f"{item!r} is not in the grid")

    def is_outermost(self, item: T, side: Side) -> bool:
        """
        Return whether no item lies beyond `item` on `side`

        An item is outermost on its bottom when every cell below the
        columns it covers is empty, and correspondingly for the other
        three sides. In a full grid this is the last row or column; in a
        ragged one an item can be outermost from an interior cell.

        Parameters
        ----------
        item
            Item to inspect, matched by identity.
        side
            Side of the grid to look beyond.

        Returns
        -------
        out
            Whether every cell beyond the item on that side is empty.
        """
        r0, r1, c0, c1 = self._rect_of(item)
        if side == "top":
            beyond = self._grid[:r0, c0 : c1 + 1]
        elif side == "bottom":
            beyond = self._grid[r1 + 1 :, c0 : c1 + 1]
        elif side == "left":
            beyond = self._grid[r0 : r1 + 1, :c0]
        else:
            beyond = self._grid[r0 : r1 + 1, c1 + 1 :]
        return all(n is None for n in beyond.flat)

    def edge_index(self, item: T, side: Side) -> int:
        """
        Return the row or column of `item`'s `side` edge

        The inverse of `items_on_edge`: the index it returns is the one
        that would list `item` for that side.

        Parameters
        ----------
        item
            Item in the grid, matched by identity.
        side
            Side of the item to locate.

        Returns
        -------
        out
            Row index for `"top"` and `"bottom"`, column index for
            `"left"` and `"right"`.
        """
        r0, r1, c0, c1 = self._rect_of(item)
        return {"top": r0, "bottom": r1, "left": c0, "right": c1}[side]


class DesignGrid(Grid[T]):
    """
    Grid where items span rectangular regions

    Each item is associated with an inclusive rectangle
    `(r0, r1, c0, c1)` and placed at every cell within it; this
    keeps base-class `__getitem__`, `iter_rows`, and `iter_cols`
    working as in `Grid`. The reductions are overridden to be
    span-aware: an item spanning multiple columns contributes its
    measurement divided by its column span to each column it
    covers (and analogously for rows).

    Parameters
    ----------
    nrow
        Number of rows in the grid.
    ncol
        Number of columns in the grid.
    items
        Items to place. One per rectangle, in the order rectangles
        appear in `rects`.
    rects
        Inclusive `(r0, r1, c0, c1)` rectangle for each item.
        Trusted: overlap and shape are not validated here.
    """

    # Bypass Grid's dataclass __init__ — rectangle expansion is a
    # different placement scheme than row/col-major.
    def __init__(
        self,
        nrow: int,
        ncol: int,
        items: Sequence[T],
        rects: Sequence[Rect],
    ):
        if len(items) != len(rects):
            raise ValueError(
                f"Got {len(items)} items but {len(rects)} rectangles"
            )
        self._grid = np.empty((nrow, ncol), dtype=object)
        self._items: list[T] = list(items)
        self._rects: list[Rect] = list(rects)
        # Place each item at every cell of its rectangle so the base
        # class's __getitem__ / iter_rows / iter_cols keep working.
        for item, (r0, r1, c0, c1) in zip(self._items, self._rects):
            self._grid[r0 : r1 + 1, c0 : c1 + 1] = item

    def reduce_cols(
        self,
        fn: Callable[[T], float],
        default: float,
    ) -> list[float]:
        # An item spanning multiple columns shares its measurement
        # across the columns it covers: fn(item) / colspan goes into
        # each. Then per-column max as in Grid.reduce_cols.
        out: list[float] = []
        for c in range(self._grid.shape[1]):
            contribs = [
                fn(item) / (c1 - c0 + 1)
                for item, (_, _, c0, c1) in zip(self._items, self._rects)
                if c0 <= c <= c1
            ]
            out.append(max(contribs) if contribs else default)
        return out

    def reduce_rows(
        self,
        fn: Callable[[T], float],
        default: float,
    ) -> list[float]:
        # Mirror of reduce_cols: fn(item) / rowspan into each row the
        # item covers, then per-row max.
        out: list[float] = []
        for r in range(self._grid.shape[0]):
            contribs = [
                fn(item) / (r1 - r0 + 1)
                for item, (r0, r1, _, _) in zip(self._items, self._rects)
                if r0 <= r <= r1
            ]
            out.append(max(contribs) if contribs else default)
        return out

    def items_on_edge(
        self,
        side: Side,
        idx: int,
    ) -> list[T]:
        # An item's top/bottom edge is its r0/r1; left/right is c0/c1.
        # Match the requested edge to idx exactly — not "the item is
        # present at row/col idx", which would include spanned cells.
        out: list[T] = []
        for item, (r0, r1, c0, c1) in zip(self._items, self._rects):
            edge = {"top": r0, "bottom": r1, "left": c0, "right": c1}[side]
            if edge == idx:
                out.append(item)
        return out

    def _rect_of(self, item: T) -> Rect:
        # Use the recorded span instead of treating its first cell as the
        # whole item.
        for it, rect in zip(self._items, self._rects):
            if it is item:
                return rect
        raise ValueError(f"{item!r} is not in the grid")

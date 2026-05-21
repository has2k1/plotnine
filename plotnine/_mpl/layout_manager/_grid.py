from collections.abc import Iterator
from dataclasses import InitVar, dataclass
from typing import (
    Callable,
    Generic,
    Literal,
    Sequence,
    TypeVar,
    overload,
)

import numpy as np

T = TypeVar("T")


@dataclass
class Grid(Generic[T]):
    nrow: InitVar[int]
    ncol: InitVar[int]
    items: InitVar[Sequence[T]]
    order: InitVar[Literal["row_major", "col_major"]] = "row_major"
    """
    Put items into the grid left->right, top->bottom starting at `start`.
    Unfilled cells remain None. Returns the number of items written.
    """

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
        side: Literal["top", "bottom", "left", "right"],
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

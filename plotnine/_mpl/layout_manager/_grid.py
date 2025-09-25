from collections.abc import Iterator
from dataclasses import InitVar, dataclass
from typing import (
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

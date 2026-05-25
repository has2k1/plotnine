from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Sequence, TypeVar

from plotnine._mpl.layout_manager._grid import DesignGrid

if TYPE_CHECKING:
    from matplotlib.gridspec import SubplotSpec

    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine._mpl.layout_manager._grid import Rect

T = TypeVar("T")

EMPTY_CHARS = frozenset({"#", ".", " "})


@dataclass
class DesignSpec:
    """
    Parsed `plot_layout(design=...)` string

    Attributes
    ----------
    nrow, ncol
        Grid shape.
    grid
        `nrow × ncol` matrix of labels. Empty cells carry `""`.
    """

    nrow: int
    ncol: int
    grid: list[list[str]]
    _rects: list[Rect] = field(repr=False)
    """
    Inclusive `(r0, r1, c0, c1)` rectangle per item, in plot order
    (= sorted order of the label characters). Internal — production
    consumers should go through `get_subplotspecs` and `make_grid`
    instead of reading this directly.
    """

    @property
    def n_regions(self) -> int:
        """
        Number of regions in the design (= items the composition needs)
        """
        return len(self._rects)

    def get_subplotspecs(self, gridspec: p9GridSpec) -> list[SubplotSpec]:
        """
        One SubplotSpec per item, sliced from `gridspec` along the
        item's rectangle
        """
        return [
            gridspec[r0 : r1 + 1, c0 : c1 + 1]
            for (r0, r1, c0, c1) in self._rects
        ]

    def make_grid(self, items: Sequence[T]) -> DesignGrid[T]:
        """
        Span-aware `DesignGrid` placing `items` at this design's rects
        """
        return DesignGrid(self.nrow, self.ncol, items, self._rects)


def parse_design(s: str) -> DesignSpec:
    """
    Parse a design string into a DesignSpec

    See `plot_layout(design=...)` for the format.
    """
    # Pipeline:
    # 1. Strip & split into rows; require equal row widths.
    # 2. Build the cell grid, normalising empty markers (#, ., space) to "".
    # 3. Group cell positions by label character.
    # 4. For each label in sorted order, take the bounding rectangle
    #    of its cells and verify every cell inside is the same label
    #    (loud rejection of L-shapes and overlapping regions).
    lines = [line.strip() for line in s.strip().split("\n")]
    lines = [line for line in lines if line]
    if not lines:
        raise ValueError("design string is empty")

    ncol = len(lines[0])
    for r, line in enumerate(lines):
        if len(line) != ncol:
            raise ValueError(
                f"design rows have unequal lengths: "
                f"row 0 has {ncol} columns but row {r} has {len(line)}"
            )
    nrow = len(lines)

    grid: list[list[str]] = [
        ["" if ch in EMPTY_CHARS else ch for ch in line] for line in lines
    ]

    cells_by_label: dict[str, list[tuple[int, int]]] = {}
    for r in range(nrow):
        for c in range(ncol):
            ch = grid[r][c]
            if not ch:
                continue
            cells_by_label.setdefault(ch, []).append((r, c))

    # Assign plots in the sorted order of label characters
    rects: list[Rect] = []
    for label in sorted(cells_by_label):
        cells = cells_by_label[label]
        rs = [r for r, _ in cells]
        cs = [c for _, c in cells]
        r0, r1 = min(rs), max(rs)
        c0, c1 = min(cs), max(cs)
        # Rectangularity: every cell inside the bounding box must
        # carry this label.
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                if grid[r][c] != label:
                    found = grid[r][c] or "#"
                    raise ValueError(
                        f"design region '{label}' is not rectangular: "
                        f"cell ({r}, {c}) is '{found}' but should "
                        f"be '{label}'"
                    )
        rects.append((r0, r1, c0, c1))

    return DesignSpec(nrow=nrow, ncol=ncol, grid=grid, _rects=rects)

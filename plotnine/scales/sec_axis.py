from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from .._utils import OPPOSITE_SIDE, identity
from ..exceptions import PlotnineError
from ..iapi import sec_axis_view
from ._runtime_typing import (  # noqa: TCH001
    ContinuousBreaksUser,
    ScaleLabelsUser,
)

if TYPE_CHECKING:
    from typing import Callable, Sequence

    from plotnine.iapi import scale_position_view
    from plotnine.scales.scale_continuous import scale_continuous
    from plotnine.typing import FloatArray, FloatArrayLike

__all__ = ("sec_axis", "dup_axis")

# Number of grid points used to numerically invert the transform
GRID_SIZE = 1000


@dataclass
class sec_axis:
    """
    Specification of a secondary axis

    A secondary axis is drawn on the side opposite the primary axis.
    It represents a strictly monotonic, one-to-one transformation of
    the primary values, with its own breaks, labels and title.
    """

    transform: Callable[[FloatArray], FloatArrayLike] = identity
    """
    Vectorized function that maps values of the primary axis (in data
    space) to values of the secondary axis. It must be strictly
    monotonic over the range of the primary axis.
    """

    name: str | None = None
    """
    Title of the secondary axis. If `None`, the primary axis title is
    used. An empty string gives no title.
    """

    breaks: ContinuousBreaksUser = True
    """
    Locations of the secondary ticks, in secondary values. `True`
    computes nice breaks, `None` places ticks at the primary breaks,
    `False` removes them. A sequence or callable is used as given.
    """

    labels: ScaleLabelsUser = True
    """
    Labels at the secondary breaks. `True` formats the breaks, `None`
    copies the primary labels (requires `breaks=None`), `False`
    removes them. A sequence, callable or dict is used as given.
    """

    def __post_init__(self):
        if self.labels is None and self.breaks is not None:
            raise PlotnineError(
                "A secondary axis can only copy the primary labels "
                "(labels=None) when it also copies the primary breaks "
                "(breaks=None)."
            )

    def view(
        self,
        scale: scale_continuous,
        primary: scale_position_view,
    ) -> sec_axis_view:
        """
        Resolved secondary axis for one panel of the primary scale

        Parameters
        ----------
        scale :
            Trained primary scale.
        primary :
            View of the primary scale for the panel.

        Returns
        -------
        :
            Breaks, labels, title and side of the secondary axis. The
            breaks are positions in the primary (transformed)
            coordinate space, ready to be placed on an mpl axis.
        """
        from mizani.transforms import identity_trans

        low, high = min(primary.range), max(primary.range)
        grid = np.linspace(low, high, GRID_SIZE)
        values = np.asarray(
            self.transform(np.asarray(scale.inverse(grid))), dtype=float
        )
        diffs = np.diff(values)
        if not (np.all(diffs > 0) or np.all(diffs < 0)):
            raise PlotnineError(
                "The transformation for a secondary axis must be monotonic."
            )
        if values[0] > values[-1]:
            values, grid = values[::-1], grid[::-1]
        vrange = (values[0], values[-1])

        if self.breaks is None:
            breaks = np.asarray(primary.breaks, dtype=float)
            sec_values = np.asarray(
                self.transform(np.asarray(scale.inverse(breaks))),
                dtype=float,
            )
        else:
            if self.breaks is True:
                sec_values = np.asarray(
                    identity_trans().breaks(vrange), dtype=float
                )
            elif self.breaks is False:
                sec_values = np.array([])
            elif callable(self.breaks):
                sec_values = np.asarray(self.breaks(vrange), dtype=float)
            else:
                sec_values = np.asarray(self.breaks, dtype=float)
            keep = (sec_values >= vrange[0]) & (sec_values <= vrange[1])
            sec_values = sec_values[keep]
            breaks = np.interp(sec_values, values, grid)

        labels: Sequence[str]
        if self.labels is None:
            labels = list(primary.labels)
        elif self.labels is True:
            labels = identity_trans().format(sec_values)
        elif self.labels is False:
            labels = []
        elif isinstance(self.labels, dict):
            labels = [str(self.labels.get(b, b)) for b in sec_values]
        elif callable(self.labels):
            labels = self.labels(list(sec_values))
        else:
            labels = list(self.labels)

        return sec_axis_view(
            breaks=list(breaks),
            labels=list(labels),
            name=self.name,
            position=OPPOSITE_SIDE[primary.position],
        )


def dup_axis(
    name: str | None = None,
    breaks: ContinuousBreaksUser = None,
    labels: ScaleLabelsUser = None,
) -> sec_axis:
    """
    Specification of a secondary axis that mirrors the primary axis

    Every argument defaults to `None` — copy the setting from the
    primary axis.

    Parameters
    ----------
    name :
        Title of the secondary axis, as in `sec_axis`.
    breaks :
        Locations of the secondary ticks, as in `sec_axis`.
    labels :
        Labels at the secondary breaks, as in `sec_axis`.

    Returns
    -------
    :
        A secondary axis specification with an identity transform.
    """
    return sec_axis(name=name, breaks=breaks, labels=labels)

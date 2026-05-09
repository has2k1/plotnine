from __future__ import annotations

from typing import TypeVar

from matplotlib.artist import Artist
from matplotlib.figure import Figure

TArtist = TypeVar("TArtist", bound=Artist)


class p9Figure(Figure):
    """
    Figure for plotnine plots

    It stamps figure-level artists (added through the public methods:
    `add_*`, `figimage` and `text`) with strictly increasing zorders,
    allowing insertion order to dictates paint order, since matplotlib
    stable-sorts by zorder before rendering.

    For now stamping is gated by `_stamping` as the refactoring goes on.
    """

    _next_zorder: int
    _stamping: bool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # figure.patch sits at zorder 1; start above it.
        self._next_zorder = 2
        self._stamping = False

    def _stamp(self, artist: TArtist) -> TArtist:
        if self._stamping:
            artist.set_zorder(self._next_zorder)
            self._next_zorder += 1
        return artist

    def add_artist(self, artist, *args, **kwargs):
        return self._stamp(super().add_artist(artist, *args, **kwargs))

    def add_subplot(self, *args, **kwargs):
        return self._stamp(super().add_subplot(*args, **kwargs))

    def add_axes(self, *args, **kwargs):
        return self._stamp(super().add_axes(*args, **kwargs))

    def figimage(self, *args, **kwargs):
        return self._stamp(super().figimage(*args, **kwargs))

    def text(self, *args, **kwargs):
        return self._stamp(super().text(*args, **kwargs))

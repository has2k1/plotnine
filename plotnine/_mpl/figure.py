from __future__ import annotations

from typing import TypeVar

from matplotlib.artist import Artist
from matplotlib.figure import Figure

TArtist = TypeVar("TArtist", bound=Artist)


class p9Figure(Figure):
    """
    Figure for plotnine plots

    Stamps figure-level artists (added through the public methods
    ``add_artist``, ``add_subplot``, ``add_axes``, ``figimage``,
    ``text``) with strictly increasing zorders, so insertion order
    dictates paint order — matplotlib stable-sorts by zorder before
    rendering.
    """

    _next_zorder: int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # figure.patch sits at zorder 1; start above it.
        self._next_zorder = 2

    def _stamp(self, artist: TArtist) -> TArtist:
        artist.set_zorder(self._next_zorder)
        self._next_zorder += 1
        return artist

    def add_artist(self, artist: TArtist, *args, **kwargs) -> TArtist:
        super().add_artist(artist, *args, **kwargs)
        return self._stamp(artist)

    def add_subplot(self, *args, **kwargs):
        return self._stamp(super().add_subplot(*args, **kwargs))

    def add_axes(self, *args, **kwargs):
        return self._stamp(super().add_axes(*args, **kwargs))

    def figimage(self, *args, **kwargs):
        return self._stamp(super().figimage(*args, **kwargs))

    def text(self, *args, **kwargs):
        return self._stamp(super().text(*args, **kwargs))

from __future__ import annotations

import typing
from copy import deepcopy

from matplotlib.animation import ArtistAnimation

from .exceptions import PlotnineError

if typing.TYPE_CHECKING:
    from typing import Iterable

    from matplotlib.artist import Artist
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from plotnine import ggplot
    from plotnine.scales.scale import scale

__all__ = ("PlotnineAnimation",)


class PlotnineAnimation(ArtistAnimation):
    """
    Animation using ggplot objects

    Parameters
    ----------
    plots :
        ggplot objects that make up the the frames of the animation
    interval : int
        Delay between frames in milliseconds. Defaults to 200.
    repeat_delay : int
        If the animation in repeated, adds a delay in milliseconds
        before repeating the animation. Defaults to `None`.
    repeat : bool
        Controls whether the animation should repeat when the sequence
        of frames is completed. Defaults to `True`.
    blit : bool
        Controls whether blitting is used to optimize drawing. Defaults
        to `False`.

    Notes
    -----
    1. The plots should have the same `facet` and
       the facet should not have fixed x and y scales.
    2. The scales of all the plots should have the same limits. It is
       a good idea to create a scale (with limits) for each aesthetic
       and add them to all the plots.
    """

    def __init__(
        self,
        plots: Iterable[ggplot],
        interval: int = 200,
        repeat_delay: int | None = None,
        repeat: bool = True,
        blit: bool = False,
    ):
        figure, artists = self._draw_plots(plots)
        ArtistAnimation.__init__(
            self,
            figure,
            artists,
            interval=interval,
            repeat_delay=repeat_delay,
            repeat=repeat,
            blit=blit,
        )

    def _draw_plots(
        self, plots: Iterable[ggplot]
    ) -> tuple[Figure, list[list[Artist]]]:
        """
        Plot and return the figure and artists

        Parameters
        ----------
        plots : iterable
            ggplot objects that make up the the frames of the animation

        Returns
        -------
        figure
            Matplotlib figure
        artists
            List of [](`Matplotlib.artist.Artist`)
        """
        import matplotlib.pyplot as plt

        # For keeping track of artists for each frame
        artist_offsets: dict[str, list[int]] = {
            "collections": [],
            "patches": [],
            "lines": [],
            "texts": [],
            "artists": [],
        }

        scale_limits = {}

        def initialise_artist_offsets(n: int):
            """
            Initialise artists_offsets arrays to zero

            Parameters
            ----------
            n : int
                Number of axes to initialise artists for.
                The artists for each axes are tracked separately.
            """
            for artist_type in artist_offsets:
                artist_offsets[artist_type] = [0] * n

        def get_frame_artists(axs: list[Axes]) -> list[Artist]:
            """
            Artists shown in a given frame

            Parameters
            ----------
            axs : list[Axes]
                Matplotlib axes that have had artists added
                to them.
            """
            # The axes accumulate artists for all frames
            # For each frame we pickup the newly added artists
            # We use offsets to mark the end of the previous frame
            # e.g ax.collections[start:]
            frame_artists = []
            for i, ax in enumerate(axs):
                for name in artist_offsets:
                    start = artist_offsets[name][i]
                    new_artists = getattr(ax, name)[start:]
                    frame_artists.extend(new_artists)
                    artist_offsets[name][i] += len(new_artists)
            return frame_artists

        def set_scale_limits(scales: list[scale]):
            """
            Set limits of all the scales in the animation

            Should be called before `check_scale_limits`.

            Parameters
            ----------
            scales : list[scales]
                List of scales the have been used in building a
                ggplot object.
            """
            for sc in scales:
                ae = sc.aesthetics[0]
                scale_limits[ae] = sc.final_limits

        def check_scale_limits(scales: list[scale], frame_no: int):
            """
            Check limits of the scales of a plot in the animation

            Raises a PlotnineError if any of the scales has limits
            that do not match those of the first plot/frame.

            Should be called after `set_scale_limits`.

            Parameters
            ----------
            scales : list[scales]
                List of scales the have been used in building a
                ggplot object.

            frame_no : int
                Frame number
            """
            if len(scale_limits) != len(scales):
                raise PlotnineError(
                    "All plots must have the same number of scales "
                    "as the first plot of the animation."
                )

            for sc in scales:
                ae = sc.aesthetics[0]
                if ae not in scale_limits:
                    raise PlotnineError(
                        f"The plot for frame {frame_no} does not "
                        f"have a scale for the {ae} aesthetic."
                    )
                if sc.final_limits != scale_limits[ae]:
                    raise PlotnineError(
                        f"The {ae} scale of plot for frame {frame_no} has "
                        "different limits from those of the first frame."
                    )

        figure: Figure | None = None
        axs: list[Axes] = []
        artists = []
        scales = None  # Will hold the scales of the first frame

        # The first ggplot creates the figure, axes and the initial
        # frame of the animation. The rest of the ggplots draw
        # onto the figure and axes created by the first ggplot and
        # they create the subsequent frames.
        for frame_no, p in enumerate(plots):
            if figure is None:
                figure = p.draw()
                axs = figure.get_axes()
                initialise_artist_offsets(len(axs))
                scales = p._build_objs.scales
                set_scale_limits(scales)
            else:
                plot = self._draw_animation_plot(p, figure, axs)
                check_scale_limits(plot.scales, frame_no)

            artists.append(get_frame_artists(axs))

        if figure is None:
            figure = plt.figure()

        assert figure is not None
        # Prevent Jupyter from plotting any static figure
        plt.close(figure)
        return figure, artists

    def _draw_animation_plot(
        self, plot: ggplot, figure: Figure, axs: list[Axes]
    ) -> ggplot:
        """
        Draw a plot/frame of the animation

        This methods draws plots from the 2nd onwards
        """
        from ._utils.context import plot_context

        plot = deepcopy(plot)
        plot.figure = figure
        plot.axs = axs
        with plot_context(plot):
            plot._build()
            plot.axs = plot.facet.setup(plot)
            plot._draw_layers()
        return plot

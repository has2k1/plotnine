from copy import copy

import matplotlib.pyplot as plt
from matplotlib.animation import ArtistAnimation

from .exceptions import PlotnineError


class PlotnineAnimation(ArtistAnimation):
    """
    Animation using ggplot objects

    Parameters
    ----------
    plots : iterable
        ggplot objects that make up the the frames of the animation
    interval : number, optional
       Delay between frames in milliseconds. Defaults to 200.
    repeat_delay : number, optional
        If the animation in repeated, adds a delay in milliseconds
        before repeating the animation. Defaults to `None`.
    repeat : bool, optional
        Controls whether the animation should repeat when the sequence
        of frames is completed. Defaults to `True`.
    blit : bool, optional
        Controls whether blitting is used to optimize drawing. Defaults
        to `False`.

    Note
    ----
    1. The plots should have the same `facet` and
       the facet should not have fixed x and y scales.
    2. The scales of all the plots should have the same limits. It is
       a good idea to create a scale (with limits) for each aesthetic
       and add them to all the plots.
    3. For plots with legends or any other features that are cutoff,
       use the :class:`~plotnine.themes.themeable.subplots_adjust`
       themeable to create space for it.
    """

    def __init__(self, plots, interval=200, repeat_delay=None,
                 repeat=True, blit=False):
        figure, artists = self._draw_plots(plots)
        ArtistAnimation.__init__(
            self,
            figure,
            artists,
            interval=interval,
            repeat_delay=repeat_delay,
            repeat=repeat,
            blit=blit
        )

    def _draw_plots(self, plots):
        """
        Plot and return the figure and artists

        Parameters
        ----------
        plots : iterable
            ggplot objects that make up the the frames of the animation

        Returns
        -------
        figure : matplotlib.figure.Figure
            Matplotlib figure
        artists : list
            List of :class:`Matplotlib.artist.artist`
        """
        # For keeping track of artists for each frame
        artist_offsets = {
            'collections': [],
            'patches': [],
            'lines': [],
            'texts': [],
            'artists': []
        }

        scale_limits = dict()

        def initialise_artist_offsets(n):
            """
            Initilise artists_offsets arrays to zero

            Parameters
            ----------
            n : int
                Number of axes to initialise artists for.
                The artists for each axes are tracked separately.
            """
            for artist_type in artist_offsets:
                artist_offsets[artist_type] = [0] * n

        def get_frame_artists(plot):
            """
            Parameters
            ----------
            plot : ggplot
                Drawn ggplot object from which to extract
                artists.
            """
            # The axes accumulate artists for all frames
            # For each frame we pickup the newly added artists
            # We use offsets to mark the end of the previous frame
            # e.g ax.collections[start:]
            frame_artists = []
            for i, ax in enumerate(plot.axs):
                for name in artist_offsets:
                    start = artist_offsets[name][i]
                    new_artists = getattr(ax, name)[start:]
                    frame_artists.extend(new_artists)
                    artist_offsets[name][i] += len(new_artists)
            return frame_artists

        def set_scale_limits(plot):
            """
            Set limits of all the scales in the animation

            Should be called before :func:`check_scale_limits`.

            Parameters
            ----------
            plot : ggplot
                First ggplot object that has been drawn
            """
            for sc in plot.scales:
                ae = sc.aesthetics[0]
                scale_limits[ae] = sc.limits

        def check_scale_limits(plot, frame_no):
            """
            Check limits of the scales of a plot in the animation

            Raises a PlotnineError if any of the scales has limits
            that do not match those of the first plot/frame.

            Should be called after :func:`set_scale_limits`.

            Parameters
            ----------
            plot : ggplot
                ggplot object that has been drawn

            frame_no : int
                Frame number
            """
            if len(scale_limits) != len(plot.scales):
                raise PlotnineError(
                    "All plots must have the same number of scales "
                    "as the first plot of the animation."
                )

            for sc in plot.scales:
                ae = sc.aesthetics[0]
                if ae not in scale_limits:
                    raise PlotnineError(
                        "The plot for frame {} does not have a scale "
                        "for the {} aesthetic.".format(frame_no, ae)
                    )
                if sc.limits != scale_limits[ae]:
                    raise PlotnineError(
                        "The {} scale of plot for frame {} has different "
                        "limits from those of the first frame."
                        "".format(ae, frame_no)
                    )

        figure = None
        axs = None
        artists = []

        # The first ggplot creates the figure, axes and the initial
        # frame of the animation. The rest of the ggplots draw
        # onto the figure and axes created by the first ggplot and
        # they create the subsequent frames.
        for frame_no, p in enumerate(plots):
            if figure is None:
                figure, plot = p.draw(return_ggplot=True)
                axs = plot.axs
                initialise_artist_offsets(len(axs))
                set_scale_limits(plot)
            else:
                p = copy(p)
                plot = p._draw_using_figure(figure, axs)
                try:
                    check_scale_limits(plot, frame_no)
                except PlotnineError as err:
                    plt.close(figure)
                    raise err
            artists.append(get_frame_artists(plot))

        if figure is None:
            figure = plt.figure()

        return figure, artists

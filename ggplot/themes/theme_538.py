from .theme import theme


class theme_538(theme):
    """
    Theme for 538.

    Copied from CamDavidsonPilon's gist:
        https://gist.github.com/CamDavidsonPilon/5238b6499b14604367ac

    """

    def __init__(self):
        theme.__init__(self, complete=True)
        d = {
            'axes.axisbelow': 'True',
            'axes.edgecolor': '#F0F0F0',
            'axes.facecolor': '#F0F0F0',
            'axes.grid': 'True',
            'axes.grid.which': 'major',
            'axes.labelcolor': '#3C3C3C',
            'axes.labelsize': 'large',
            'axes.linewidth': '0',
            'axes.titlesize': 'x-large',
            'examples.directory': '',
            'figure.facecolor': '#F0F0F0',
            'figure.subplot.hspace': '0.5',
            'figure.figsize': '11, 8',
            'font.size': '14.0',
            'grid.color': '#DADADA',
            'grid.linestyle': '-',
            'grid.linewidth': '2.0',
            'legend.fancybox': 'True',
            'lines.linewidth': '2.0',
            'lines.linewidth': '4',
            'lines.solid_capstyle': 'butt',
            'patch.edgecolor': '#f0f0f0',
            'patch.linewidth': '0.5',
            'savefig.edgecolor': '#f0f0f0',
            'savefig.facecolor': '#f0f0f0',
            'svg.embed_char_paths': 'path',
            'xtick.color': '#3C3C3C',
            'xtick.major.pad': '2',
            'xtick.major.size': '0',
            'xtick.minor.size': '0',
            'ytick.color': '#3C3C3C',
            'ytick.major.pad': '2',
            'ytick.major.size': '0',
            'ytick.minor.size': '0',
        }
        self._rcParams.update(d)

    def apply_more(self, ax):
        # Only show bottom left ticks
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

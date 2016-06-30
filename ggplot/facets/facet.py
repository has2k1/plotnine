from __future__ import absolute_import, division, print_function

from ..utils import suppress

# For default matplotlib backend
with suppress(ImportError):
    import matplotlib.pyplot as plt
    import matplotlib.text as mtext
    import matplotlib.patches as mpatch


class facet(object):
    ncol = None
    nrow = None
    figure = None
    as_table = True
    drop = True
    shrink = True
    free = {'x': True, 'y': True}

    def __init__(self, scales='fixed', shrink=True,
                 labeller='label_value', as_table=True,
                 drop=True):
        from .labelling import as_labeller
        self.shrink = shrink
        self.labeller = as_labeller(labeller)
        self.as_table = as_table
        self.drop = drop
        self.free = {'x': scales in ('free_x', 'free'),
                     'y': scales in ('free_y', 'free')}

    def set_breaks_and_labels(self, ranges, layout_info, ax):
        # Add axes and labels on all sides. The super
        # class should remove what is unnecessary

        # limits
        ax.set_xlim(ranges['x_range'])
        ax.set_ylim(ranges['y_range'])

        # breaks
        ax.set_xticks(ranges['x_major'])
        ax.set_yticks(ranges['y_major'])

        # minor breaks
        ax.set_xticks(ranges['x_minor'], minor=True)
        ax.set_yticks(ranges['y_minor'], minor=True)

        # labels
        ax.set_xticklabels(ranges['x_labels'])
        ax.set_yticklabels(ranges['y_labels'])

    def get_figure_and_axs(self, num_panels):
        figure, axs = plt.subplots(self.nrow, self.ncol,
                                   sharex=False, sharey=False)
        # Dictionary to collect matplotlib objects that will
        # be targeted for theming by the themeables
        figure._themeable = {'legend_title': [],
                             'legend_text': []}
        self.figure = figure
        self.adjust_space()

        try:
            axs = axs.flatten()
        except AttributeError:
            axs = [axs]

        # No panel, do not let MPL put axes
        for ax in axs[num_panels:]:
            ax.axis('off')

        axs = axs[:num_panels]
        return figure, axs

    def adjust_space(self):
        # TODO: spaces should depend on the horizontal
        # and vertical lengths of the axes since the
        # spacing values are in transAxes dimensions
        plt.subplots_adjust(wspace=.05, hspace=.05)

    def draw_strip_text(self, text_lines, location, theme, ax):
        """
        Create a background patch and put a label on it
        """
        num_lines = len(text_lines)
        themeable = self.figure._themeable

        for key in ('strip_text_x', 'strip_text_y',
                    'strip_background_x', 'strip_background_y'):
            if key not in themeable:
                themeable[key] = []

        # The facet labels are placed onto the figure using
        # transAxes dimensions. The line height and line
        # width are mapped to the same [0, 1] range
        # i.e (pts) * (inches / pts) * (1 / inches)
        # plus a padding factor of 1.6
        bbox = ax.get_window_extent().transformed(
            self.figure.dpi_scale_trans.inverted())
        w, h = bbox.width, bbox.height  # in inches

        fs = float(theme.rcParams.get('font.size', 11))

        # linewidth in transAxes
        pad = linespacing = 1.5
        lwy = (pad+fs) / (72.27*h)
        lwx = (pad+fs) / (72.27*w)

        # bbox height (along direction of text) of
        # labels in transAxes
        hy = pad * lwy * num_lines
        hx = pad * lwx * num_lines

        # text location in transAxes
        y = 1 + hy/2.0
        x = 1 + hx/2.0

        if location == 'right':
            _x, _y = x, 0.5
            xy = (1, 0)
            rotation = -90
            box_width = hx
            box_height = 1
            label = '\n'.join(reversed(text_lines))
        else:
            _x, _y = 0.5, y
            xy = (0, 1)
            rotation = 0
            box_width = 1
            box_height = hy
            label = '\n'.join(text_lines)

        rect = mpatch.FancyBboxPatch(xy,
                                     width=box_width,
                                     height=box_height,
                                     facecolor='lightgrey',
                                     edgecolor='None',
                                     linewidth=0,
                                     transform=ax.transAxes,
                                     zorder=1,
                                     boxstyle='square, pad=0',
                                     clip_on=False)

        text = mtext.Text(_x, _y, label,
                          transform=ax.transAxes,
                          rotation=rotation,
                          verticalalignment='center',
                          horizontalalignment='center',
                          linespacing=linespacing,
                          zorder=1.2,  # higher than rect
                          clip_on=False)

        ax.add_artist(rect)
        ax.add_artist(text)

        if location == 'right':
            themeable['strip_background_y'].append(rect)
            themeable['strip_text_y'].append(text)
        else:
            themeable['strip_background_x'].append(rect)
            themeable['strip_text_x'].append(text)

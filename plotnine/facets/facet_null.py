from __future__ import absolute_import, division, print_function

from .facet import facet, layout_null


class facet_null(facet):
    """
    A single Panel

    Parameters
    ----------
    shrink : bool
        Whether to shrink the scales to the output of the
        statistics instead of the raw data. Default is ``True``.
    """

    def __init__(self, shrink=True, figure=None):
        facet.__init__(self, shrink=shrink)
        self.nrow = 1
        self.ncol = 1

    def map(self, data, layout):
        data['PANEL'] = 1
        return data

    def compute_layout(self, data):
        return layout_null()

    def set_breaks_and_labels(self, ranges, layout_info, pidx):
        """
        Add breaks and labels to the axes

        Parameters
        ----------
        ranges : dict-like
            range information for the axes
        layout_info : dict-like
            facet layout information
        pidx : int
            Panel index
        """
        ax = self.axs[pidx]
        facet.set_breaks_and_labels(self, ranges, layout_info, pidx)
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

    def spaceout_and_resize_panels(self):
        """
        Adjust the space between the panels
        """
        # Only deal with the aspect ratio
        figure = self.figure
        theme = self.theme

        try:
            aspect_ratio = theme.themeables.property('aspect_ratio')
        except KeyError:
            aspect_ratio = self.coordinates.aspect(
                    self.layout.panel_params[0])

        if aspect_ratio is None:
            return

        left = figure.subplotpars.left
        right = figure.subplotpars.right
        top = figure.subplotpars.top
        bottom = figure.subplotpars.bottom
        W, H = figure.get_size_inches()

        w = (right-left)*W
        h = w*aspect_ratio
        H = h / (top-bottom)

        figure.set_figheight(H)

    def draw_label(self, layout_info, pidx):
        pass

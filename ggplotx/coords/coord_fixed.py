from __future__ import absolute_import, division, print_function

from .coord_cartesian import coord_cartesian


class coord_fixed(coord_cartesian):
    """
    Cartesian coordinates with fixed relationship between x and y scales

    Parameters
    ----------
    ratio : float
        Desired aspect_ratio (:math:`y/x`) of the panel(s).
        Default is 1.
    xlim : None | (float, float)
        Limits for x axis. If None, then they are
        automatically computed.
    ylim : None | (float, float)
        Limits for y axis. If None, then they are
        automatically computed.
    expand : bool
        If `True`, expand the coordinate axes by
        some factor. If `False`, use the limits
        from the data.

    Note
    ----
    To specify aspect ratio of the visual size for the axes use the
    :class:`~ggplotx.themes.themeable.aspect_ratio` themeable::

        ggplot(data, aes('x', 'y')) + theme(aspect_ratio=0.5)
    """

    def __init__(self, ratio=1, xlim=None, ylim=None, expand=True):
        coord_cartesian.__init__(self, xlim=xlim, ylim=ylim,
                                 expand=expand)
        self.ratio = ratio

    def aspect(self, panel_scales):
        x = panel_scales['x_range']
        y = panel_scales['y_range']
        return (y[1]-y[0]) / (x[1]-x[0]) * self.ratio


coord_equal = coord_fixed

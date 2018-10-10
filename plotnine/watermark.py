from copy import deepcopy

import matplotlib.image as mimage


class watermark:
    """
    Add watermark to plot

    Parameters
    ----------
    filename : str
        Image file
    xo : int, optional
        x position offset in pixels. Default is 0.
    yo : int, optional
        y position offset in pixels. Default is 0.
    alpha : float, optional
        Alpha blending value.
    kwargs : dict
        Additional parameters passed to
        :meth:`matplotlib.figure.figimage`.

    Notes
    -----
    You can add more than one watermark to a plot.
    """

    def __init__(self, filename, xo=0, yo=0, alpha=None, **kwargs):
        self.filename = filename
        kwargs.update(xo=xo, yo=yo, alpha=alpha)
        if 'zorder' not in kwargs:
            kwargs['zorder'] = 99.9
        self.kwargs = kwargs

    def __radd__(self, gg, inplace=False):
        gg = gg if inplace else deepcopy(gg)
        gg.watermarks.append(self)
        return gg

    def draw(self, figure):
        """
        Draw watermark

        Parameters
        ----------
        figure : Matplotlib.figure.Figure
            Matplolib figure on which to draw
        """
        X = mimage.imread(self.filename)
        figure.figimage(X, **self.kwargs)

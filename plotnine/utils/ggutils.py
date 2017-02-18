"""
Helper methods for plotnine.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
from warnings import warn

import matplotlib.pyplot as plt
import six

from .exceptions import PlotnineError


def ggsave(filename=None, plot=None, device=None, format=None,
           path=None, scale=1, width=None, height=None, units='in',
           dpi=None, limitsize=True, **kwargs):
    """
    Save a ggplot with sensible defaults

    ggsave is a convenient function for saving a plot.  It defaults to
    saving the last plot that you displayed, and for a default size uses
    the size of the current graphics device.  It also guesses the type of
    graphics device from the extension.  This means the only argument you
    need to supply is the filename.

    Parameters
    ----------
    filename : str or file
        File name or file to write the plot to.
    plot : ggplot
        Plot to save, defaults to last plot displayed.
    format : str
        Image format to use, automatically extract from
        file name extension.
    path : str
        Path to save plot to (if you just want to set path and
        not filename).
    scale : number
        Scaling factor
    width : number
        Width (defaults to the width of current plotting window).
    height : number
        Height (defaults to the height of current plotting window).
    units : str
        Units for width and height when either one is explicitly
        specified (in, cm, or mm).
    dpi : float
        DPI to use for raster graphics. If None, defaults to using
        the `dpi` of theme, if none is set then a `dpi` of 100.
    limitsize : bool
        If ``True`` (the default), ggsave will not save images
        larger than 50x50 inches, to prevent the common error
        of specifying dimensions in pixels.
    kwargs : dict
        Additional arguments to pass to matplotlib `savefig()`.

    Note
    ----
    ggsave will happily save matplotlib plots, if that was the last plot
    and none was specified.
    """
    fig_kwargs = {'bbox_inches': 'tight'}  # 'tight' is a good default
    fig_kwargs.update(kwargs)
    figure = [None]  # Python 3 a nonlocal

    # Input verification #

    # This is the case when we just use "ggsave(plot)"
    if hasattr(filename, 'draw'):
        plot, filename = filename, plot

    # dpi
    if hasattr(plot, 'draw'):
        from ..themes.theme import theme, theme_get
        plot.theme = plot.theme or theme_get()
        if dpi is None:
            try:
                dpi = plot.theme.themeables.property('dpi')
            except KeyError:
                dpi = 100
                plot.theme += theme(dpi=dpi)
        # Should not need this with MPL 2.0
        fig_kwargs['dpi'] = dpi
    else:
        raise PlotnineError("plot is not a ggplot object")

    # format
    if format and device:
        raise PlotnineError(
            "Both 'format' and 'device' given: use only one")
    elif device:
        # in the end the image format is in format
        format = device

    # filename
    print_filename = False
    if filename is None:
        if plot:
            ext = format if format else 'pdf'
            hash_token = abs(plot.__hash__())
            filename = 'ggsave-{}.{}'.format(hash_token, ext)
            print_filename = True
        else:
            # ggplot2 has a way to get to the last plot,
            # but we currently dont't
            raise PlotnineError("No plot given: please supply a plot")

    if not isinstance(filename, six.string_types):
        # so probably a file object
        if format is None:
            raise PlotnineError(
                "filename is not a string and no format given:",
                "please supply a format!")
    if path:
        filename = os.path.join(path, filename)

    # units
    if units not in {'in', 'cm', 'mm'}:
        raise PlotnineError("units not one of 'in', 'cm', or 'mm'")

    # scale
    try:
        scale = float(scale)
    except:
        msg = "Can't convert scale argument to a number: {}"
        raise PlotnineError(msg.format(scale))

    _width, _height = width, height  # Python 3 nonlocal

    # The function the does the work #
    def _ggsave():
        width, height = _width, _height  # Python 3 nonlocal

        # figure
        if plot is None:
            figure[0] = plt.gcf()
        else:
            figure[0] = plot.draw()

        filetypes = figure[0].canvas.get_supported_filetypes()
        if format and format not in filetypes:
            raise PlotnineError("Unknown format: {}".format(format))

        fig_kwargs['format'] = format

        to_inch = {'in': lambda x: x,
                   'cm': lambda x: x/2.54,
                   'mm': lambda x: x/(2.54*10)}

        from_inch = {'in': lambda x: x,
                     'cm': lambda x: x*2.54,
                     'mm': lambda x: x*2.54*10}

        w, h = figure[0].get_size_inches()
        print_size = False
        if width is None:
            width = w
            print_size = True
        else:
            width = to_inch[units](width)

        if height is None:
            height = h
            print_size = True
        else:
            height = to_inch[units](height)

        # ggplot2: if you specify a width *and* a scale,
        # you get the width*scale image!
        width = width * scale
        height = height * scale

        if print_size or print_filename:
            msg = ''
            if print_size:
                msg = "\nSaving {0} x {1} {2} image.".format(
                           from_inch[units](width),
                           from_inch[units](height),
                           units)
            if print_filename:
                msg += '\nFilename: {}'.format(filename)

            warn(msg)

        if limitsize and (width > 25 or height > 25):
            msg = ("Dimensions exceed 25 inches "
                   "(height and width are specified in inches/cm/mm, "
                   "not pixels). If you are sure you want these "
                   "dimensions, use 'limitsize=False'.")
            raise PlotnineError(msg)

        figure[0].set_size_inches(width, height)
        figure[0].savefig(filename, **fig_kwargs)
        figure[0].set_size_inches(w, h)

    # Call to main method wrapped in clean-up code #

    def close_figure():
        """
        Any figure created in this function is closed before exit
        """
        # close figure, if it was drawn by ggsave
        if plot is not None and figure[0] is not None:
            plt.close(figure[0])

    try:
        _ggsave()
    except Exception as err:
        close_figure()
        raise err
    else:
        close_figure()

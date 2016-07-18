"""
Helper methods for ggplotx.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import six

from .exceptions import gg_warn, GgplotError


class _gg_options(dict):

    def __setitem__(self, key, val):
        if key not in self:
            raise GgplotError("Unknown option '{}'".format(key))
        dict.__setitem__(self, key, val)

    def __deepcopy__(self, memo):
        return self


gg_options = _gg_options(
    # Development flag, e.g. set to True to prevent
    # the queuing up of figures when errors happen.
    close_all_figures=False,
    current_theme=None)


if not hasattr(mpl, 'rc_context'):
    from .utils import _rc_context
    mpl.rc_context = _rc_context


class gg_context(object):
    def __init__(self, fname=None, theme=None):
        self.fname = fname
        self.theme = theme

    def __enter__(self):
        # Outer matplotlib context
        try:
            self._rc_context = mpl.rc_context()
        except AttributeError:
            # Workaround for matplotlib 1.1.1 not having a rc_context
            self._rcparams = mpl.rcParams.copy()
            if self.fname:
                mpl.rcfile(self.fname)
        else:
            self._rc_context.__enter__()

        # Inside self._rc_context, modify rc params
        if self.theme:
            # Use a throw away rcParams, so subsequent plots
            # will not have any residual from this plot
            for key, val in six.iteritems(self.theme.rcParams):
                # there is a bug in matplotlib which does not allow
                # None directly
                # https://github.com/matplotlib/matplotlib/issues/2543
                try:
                    if key == 'text.dvipnghack' and val is None:
                        val = "none"
                    mpl.rcParams[key] = val
                except Exception as e:
                    msg = ("""Setting "mpl.rcParams['{}']={}" """
                           "raised an Exception: {}")
                    raise GgplotError(msg.format(key, val, e))
        mpl.interactive(False)

    def __exit__(self, type, value, tb):
        # restore rc params
        try:
            self._rc_context.__exit__(type, value, tb)
        except AttributeError:
            mpl.rcParams.update(self._rcparams)

        # other clean up
        self.reset()

    def reset(self):
        pass


# API-docs from ggplot2: GPL-2 licensed

def ggsave(filename=None, plot=None, device=None, format=None,
           path=None, scale=1, width=None, height=None, units="in",
           dpi=300, limitsize=True, **kwargs):
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
    dpi : number
        DPI to use for raster graphics.
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

    # This is the case when we just use "ggsave(plot)"
    if hasattr(filename, 'draw'):
        plot, filename = filename, plot

    if plot is None:
        figure = plt.gcf()
    else:
        if hasattr(plot, 'draw'):
            from ..themes.theme import theme, theme_get
            plot.theme = (plot.theme or theme_get()) + theme(dpi=dpi)
            figure = plot.draw()
        else:
            raise GgplotError("plot is not a ggplot object")

    if format and device:
        raise GgplotError(
            "Both 'format' and 'device' given: only use one")

    # in the end the image format is in format
    if device:
        format = device
    if format:
        if format not in figure.canvas.get_supported_filetypes():
            raise GgplotError("Unknown format: {}".format(format))
        fig_kwargs['format'] = format

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
            raise GgplotError("No plot given: please supply a plot")

    if not isinstance(filename, six.string_types):
        # so probably a file object
        if format is None:
            raise GgplotError(
                "filename is not a string and no format given:",
                "please supply a format!")

    if path:
        filename = os.path.join(path, filename)

    if units not in ['in', 'cm', 'mm']:
        raise GgplotError("units not one of 'in', 'cm', or 'mm'")

    to_inch = {'in': lambda x: x,
               'cm': lambda x: x/2.54,
               'mm': lambda x: x/(2.54*10)}

    from_inch = {'in': lambda x: x,
                 'cm': lambda x: x*2.54,
                 'mm': lambda x: x*2.54*10}

    w, h = figure.get_size_inches()
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

    try:
        scale = float(scale)
    except:
        msg = "Can't convert scale argument to a number: {}"
        raise GgplotError(msg.format(scale))

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

        gg_warn(msg)

    if limitsize and (width > 25 or height > 25):
        msg = ("Dimensions exceed 25 inches "
               "(height and width are specified in inches/cm/mm, "
               "not pixels). If you are sure you want these "
               "dimensions, use 'limitsize=False'.")
        raise GgplotError(msg)

    figure.set_size_inches(width, height)
    figure.savefig(filename, **fig_kwargs)
    figure.set_size_inches(w, h)

    # close figure, if it was drawn by ggsave
    if plot is not None:
        plt.close(figure)

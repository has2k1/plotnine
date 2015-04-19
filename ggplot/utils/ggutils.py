"""Helper methods for ggplot.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json
import os
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import six

from .exceptions import gg_warning, GgplotError, gg_reset


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
            rcParams = self.theme.get_rcParams()
            for key in six.iterkeys(rcParams):
                val = rcParams[key]
                # there is a bug in matplotlib which does not allow
                # None directly
                # https://github.com/matplotlib/matplotlib/issues/2543
                try:
                    if key == 'text.dvipnghack' and val is None:
                        val = "none"
                    mpl.rcParams[key] = val
                except Exception as e:
                    msg = """\
                        Setting "mpl.rcParams['{}']={}" \
                        raised an Exception: {}"""
                    gg_warning(msg.format(key, val, e))
        mpl.interactive(False)

    def __exit__(self, type, value, tb):
        # restore rc params
        try:
            self._rc_context.__exit__(type, value, tb)
        except AttributeError:
            mpl.rcParams.update(self._rcparams)

        # other clean up
        gg_reset()  # TODO: get rid of this
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
        file name or file to write the plot to
    plot : ggplot
        plot to save, defaults to last plot displayed
    format : str
        image format to use, automatically extract from
        file name extension
    path : str
        path to save plot to (if you just want to set path and
        not filename)
    scale : number
        scaling factor
    width : number
        width (defaults to the width of current plotting window)
    height : number
        height (defaults to the height of current plotting window)
    units : str
        units for width and height when either one is explicitly
        specified (in, cm, or mm)
    dpi : number
        dpi to use for raster graphics
    limitsize : bool
        when `True` (the default), ggsave will not save images
        larger than 50x50 inches, to prevent the common error
        of specifying dimensions in pixels.
    kwargs : dict
        additional arguments to pass to matplotlib `savefig()`

    Returns
    -------
    None

    Examples
    --------
    >>> from ggplot import *
    >>> gg = ggplot(aes(x='wt',y='mpg',label='name'),data=mtcars) + geom_text()
    >>> ggsave("filename.png", gg)

    Notes
    -----
    Incompatibilities to ggplot2:

    - `format` can be use as a alternative to `device`
    - ggsave will happily save matplotlib plots, if that was the last plot
    """
    fig_kwargs = {'bbox_inches': 'tight'}  # 'tight' is a good default
    fig_kwargs.update(kwargs)

    # This is the case when we just use "ggsave(plot)"
    if hasattr(filename, 'render'):
        plot, filename = filename, plot

    if plot is None:
        figure = plt.gcf()
    else:
        if hasattr(plot, 'render'):
            plot.theme._rcParams['figure.dpi'] = dpi
            figure = plot.render()
        else:
            raise GgplotError("plot is not a ggplot object")

    if format and device:
        raise GgplotError(
            "Both 'format' and 'device' given: only use one")
    # in the end the imageformat is in format
    if device:
        format = device
    if format:
        if format not in figure.canvas.get_supported_filetypes():
            raise GgplotError("Unknown format: {}".format(format))
        fig_kwargs['format'] = format

    if filename is None:
        if plot:
            # ggplot2 defaults to pdf
            filename = '{}.{}'.format(plot.__hash__(),
                                      (format if format else 'pdf'))
        else:
            # ggplot2 has a way to get to the last plot,
            # but we currently dont't
            raise GgplotError(
                "No plot given: please supply a plot")

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
    issue_size = False
    if width is None:
        width = w
        issue_size = True
    else:
        width = to_inch[units](width)
    if height is None:
        height = h
        issue_size = True
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

    if issue_size:
        msg = "Saving {0} x {1} {2} image.\n"
        gg_warning(msg.format(from_inch[units](width),
                              from_inch[units](height),
                              units))

    if limitsize and (width > 25 or height > 25):
        raise GgplotError(
            "Dimensions exceed 25 inches",
            "(height and width are specified in inches/cm/mm,",
            "not pixels). If you are sure you want these",
            "dimensions, use 'limitsize=False'.")

    try:
        figure.set_size_inches(width, height)
        figure.savefig(filename, **fig_kwargs)
    finally:
        # restore the sizes
        figure.set_size_inches(w, h)

    # close figure, if it was drawn by ggsave
    if plot is not None:
        plt.close(figure)

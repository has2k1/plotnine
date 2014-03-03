from ggplot import *
from ggplot import xlab as xlabel
from ggplot import ylab as ylabel
import pandas as pd


def qplot(x, y=None, color=None, size=None, fill=None, data=None,
        geom="auto", stat=[], position=[], xlim=None, ylim=None, log="",
        main=None, xlab=None, ylab="", asp=None):
    """
    Parameters
    ----------
    x: string, pandas series, list, or numpy array
        x values
    y: string, pandas series, list, or numpy array
        y values
    color: string
        color values
    size: string
        size values
    fill: string
        fill values
    data: data frame
        data frame to use for the plot
    geom: string (auto, point, bar, hist, line)
        string that specifies which type of plot to make
    stat: list
        specifies which statistics to use
    position: list
        gives position adjustment to use
    xlim: tuple
        limits on x axis; i.e. (0, 10)
    ylim: tuple, None
        limits on y axis; i.e. (0, 10)
    log: string
        which variables to log transform ("x", "y", or "xy")
    main: string
        title for the plot
    xlab: string
        title for the x axis
    ylab: string
        title for the y axis
    asp: string
        the y/x aspect ratio
    
    Returns
    -------
    p: ggplot
        returns a plot

    Examples
    --------
    >>> print qplot('mpg', 'drat', data=mtcars, main="plain")
    >>> print qplot('mpg', 'drat', color='cyl', data=mtcars, main="cont. color")
    >>> print qplot('mpg', 'drat', color='name', data=mtcars, main="disc. color")
    >>> print qplot('mpg', 'drat', size='cyl', data=mtcars, main="size")
    >>> print qplot('mpg', 'drat', data=mtcars, log='x', main="log x")
    >>> print qplot('mpg', 'drat', data=mtcars, log='y', main="log y")
    >>> print qplot('mpg', 'drat', data=mtcars, log='xy', main="log xy")
    >>> print qplot('mpg', 'drat', data=mtcars, geom="point", main="point")
    >>> print qplot('mpg', 'drat', data=mtcars, geom="line", main="line")
    >>> print qplot('mpg', data=mtcars, geom="hist", main="hist")
    >>> print qplot('mpg', data=mtcars, geom="histogram", main="histogram")
    >>> print qplot('cyl', 'mpg', data=mtcars, geom="bar", main="bar")
    >>> print qplot('mpg', 'drat', data=mtcars, xlab= "x lab", main="xlab")
    >>> print qplot('mpg', 'drat', data=mtcars, ylab = "y lab", main="ylab")
    """

    if x is not None and not isinstance(x, str):
        data = pd.DataFrame({
            "x": x
        })
        x = 'x'
    if y is not None and not isinstance(y, str):
        data['y'] = y
        y = 'y'


    aes_elements = {"x": x}
    if y:
        aes_elements["y"] = y
    if color:
        aes_elements["color"] = color
    if size:
        aes_elements["size"] = size
    if fill:
        aes_elements["fill"] = fill
    _aes = aes(**aes_elements)

    geom_map = {
        "bar": geom_bar,
        "hist": geom_histogram,
        "histogram": geom_histogram,
        "line": geom_line,
        "point": geom_point
    }
    # taking our best guess
    if geom=="auto":
        if y is None:
            geom = geom_histogram
        elif data[x].dtype==np.object:
            geom = geom_bar
        else:
            geom = geom_point
    else:
        geom = geom_map.get(geom, geom_point)

    p = ggplot(_aes, data=data) + geom()
    if "x" in log:
        p += scale_x_log()
    if "y" in log:
        p += scale_y_log()
    if xlab:
        p += xlabel(xlab)
    if ylab:
        p += ylabel(ylab)
    if main:
        p += ggtitle(main)
    return p


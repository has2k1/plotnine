from UserDict import UserDict

class aes(UserDict):
    """
    Creates a dictionary that is used to evaluate
    things you're plotting. Most typically, this will
    be a column in a pandas DataFrame.

    Parameters
    -----------
    x: x-axis value
        Can be used for continuous (point, line) charts and for
        discrete (bar, hist) charts.
    y: y-axis value
        Can be usedf or continuous charts only
    color (colour): color of a layer
        Can be continuous or discrete. If continuous, this will be
        given a color gradient between 2 colors.
    shape: shape of a point
        Can be used only with geom_point
    size: size of a point or line
        Used to give a relative size for a continuous value
    alpha: transparency level of a point
        Number between 0 and 1. Only supported for hard coded values.
    xintercept
    ymin: min value for a vertical line or a range of points
        See geom_area, geom_ribbon, geom_vline
    ymax: max value for a vertical line or a range of points
        See geom_area, geom_ribbon, geom_vline
    xmin: min value for a horizonal line
        Specific to geom_hline
    xmax: max value for a horizonal line
        Specific to geom_hline
    slope: slope of an abline
        Specific to geom_abline
    intercept: intercept of an abline
        Specific to geom_abline

    Examples
    -----------
    aes(x='x', y='y')
    """

    DEFAULT_ARGS = ['x', 'y', 'color']
    
    def __init__(self, *args, **kwargs):
        if args:
            self.data = dict(zip(self.DEFAULT_ARGS, args))
        else:
            self.data = kwargs
        if 'colour' in self.data:
            self.data['color'] = self.data['colour']
            del self.data['colour']


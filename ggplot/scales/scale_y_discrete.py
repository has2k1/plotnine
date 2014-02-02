from .scale import scale
from copy import deepcopy

class scale_y_discrete(scale):
    """
    Scale y axis as discrete values

    Parameters
    ----------
    breaks: list
        maps to ybreaks
    labels: list, dict
        maps to ytick_labels

    Examples
    --------
    >>> print ggplot(mtcars, aes('mpg', 'qsec')) + \
    ...     geom_point() + \
    ...     scale_y_discrete(breaks=[10,20,30],  \
    ...     labels=["horrible", "ok", "awesome"])

    """
    VALID_SCALES = ['name', 'limits', 'labels', 'breaks', 'trans']
    def __radd__(self, gg):
        gg = deepcopy(gg)
        if self.name:
            gg.ylab = self.name
        if self.limits:
            gg.ylimits = self.limits
        if self.breaks:
            gg.ybreaks = self.breaks
        if self.labels:
            gg.ytick_labels = self.labels
        return gg

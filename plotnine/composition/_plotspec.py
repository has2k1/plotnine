from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.gridspec import SubplotSpec

    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine.ggplot import ggplot


@dataclass
class plotspec:
    """
    Plot Specification
    """

    plot: ggplot
    """
    Plot
    """

    figure: Figure
    """
    Figure in which the draw the plot
    """

    composition_gridspec: p9GridSpec
    """
    The gridspec of the innermost composition group that contains the plot
    """

    subplotspec: SubplotSpec
    """
    The subplotspec that contains the plot

    This is the subplot within the composition gridspec and it will
    contain the plot's gridspec.
    """

    plot_gridspec: p9GridSpec
    """
    The gridspec in which the plot is drawn
    """

    def __post_init__(self):
        self.plot.figure = self.figure
        self.plot._gridspec = self.plot_gridspec

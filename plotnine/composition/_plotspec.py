from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure

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

    gridspec: p9GridSpec
    """
    The gridspec in which the plot is drawn
    """

    def __post_init__(self):
        self.plot.figure = self.figure
        self.plot._gridspec = self.gridspec

from __future__ import annotations

from ._plot_spacer import plot_spacer


class guide_area(plot_spacer):
    """
    A grid cell that hosts collected guides

    Used in a composition that collects guides with
    `plot_layout(guides="collect")` to route the merged legend into a
    cell of the grid instead of placing it on the side of the
    composition.

    Renders empty (like [](`~plotnine.composition.plot_spacer`)) when
    no collection is in effect, no guides exist to collect, or another
    `guide_area` was selected first.

    Parameters
    ----------
    fill :
        Background color. The default is a transparent area.
    alpha :
        Opacity of the background fill, between 0 (transparent) and 1
        (opaque). The default leaves the area transparent.

    See Also
    --------
    plotnine.composition.plot_spacer : Blank cell with the same styling.
    plotnine.composition.plot_layout : Set `guides="collect"` to enable
        collection.
    """

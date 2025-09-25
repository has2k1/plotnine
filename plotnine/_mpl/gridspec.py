from __future__ import annotations

from dataclasses import asdict
from functools import cached_property
from typing import TYPE_CHECKING, cast

try:
    from matplotlib.gridspec import GridSpecBase, SubplotParams
except ImportError:
    # MPL 3.8
    from matplotlib.figure import SubplotParams
    from matplotlib.gridspec import GridSpecBase

from matplotlib.gridspec import SubplotSpec
from matplotlib.transforms import Bbox, BboxTransformTo, TransformedBbox

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
    from matplotlib.transforms import Transform

    from plotnine._mpl.layout_manager._spaces import GridSpecParams
    from plotnine.composition._plot_layout import plot_layout


class p9GridSpec(GridSpecBase):
    """
    Gridspec for plotnine plots

    This gridspec does not read any subplot parameter values from matplotlib's
    rcparams. And there is no space along the edges and between the subplots.

    This gridspec can also be initialised while contained/nested in a given
    subplot.

    Parameters
    ----------
    nest_into :
        If given, this gridspec will be contained in the subplot.
    """

    _subplot_params: SubplotParams
    """
    The subplot spacing parameters of this gridspec

    These values are relative to where (figure or subplot) that the
    gridspec is contained. Use .get_subplot_params to get the absolute
    values (those in figure coordinates).
    """
    _nested_gridspecs: list[p9GridSpec]
    """
    All gridspecs that are nested into any of the subplots of this one
    """
    _patch: Rectangle

    def __init__(
        self,
        nrows,
        ncols,
        figure: Figure,
        *,
        width_ratios=None,
        height_ratios=None,
        byrow: bool = True,
        nest_into: SubplotSpec | None = None,
    ):
        self.figure = figure
        self._nested_gridspecs = []
        self.byrow = byrow

        super().__init__(
            nrows,
            ncols,
            width_ratios=width_ratios,
            height_ratios=height_ratios,
        )

        if nest_into:
            self._parent_subplot_spec = nest_into
            # MPL GridSpecBase expects only the subclasses that will be nested
            # to have the .get_topmost_subplotspec method.
            self.get_topmost_subplotspec = self._get_topmost_subplotspec

            # Register this gridspec as nested
            gs = cast("p9GridSpec", nest_into.get_gridspec())
            gs._nested_gridspecs.append(self)

        self.update(
            left=0,
            bottom=0,
            top=1,
            right=1,
            wspace=0,
            hspace=0,
        )

    @staticmethod
    def from_layout(
        layout: plot_layout,
        figure: Figure,
        *,
        nest_into: SubplotSpec | None = None,
    ) -> p9GridSpec:
        """
        Create gridspec from a plot_layout instance
        """
        return p9GridSpec(
            layout.nrow,
            layout.ncol,
            figure,
            byrow=True if layout.byrow is None else layout.byrow,
            nest_into=nest_into,
        )

    def __iter__(self):
        from itertools import product

        if self.byrow:
            for r, c in product(range(self.nrows), range(self.ncols)):
                yield SubplotSpec(self, r * self.ncols + c)
        else:
            for c, r in product(range(self.ncols), range(self.nrows)):
                yield SubplotSpec(self, r * self.ncols + c)

    @property
    def patch(self) -> Rectangle:
        """
        Background patch for the whole gridspec
        """
        return self._patch

    @patch.setter
    def patch(self, value: Rectangle):
        """
        Set value and update position
        """
        self._patch = value
        self._update_patch_position()

    @property
    def nested(self):
        """
        Return True if this gridspec is nested
        """
        return hasattr(self, "_parent_subplot_spec")

    def update(
        self,
        left=None,
        bottom=None,
        right=None,
        top=None,
        wspace=None,
        hspace=None,
    ):
        """
        Update the gridpec's suplot parameters and all that depend on them
        """
        if not hasattr(self, "_subplot_params"):
            self._subplot_params = SubplotParams()

        self._subplot_params.update(
            left=left,
            bottom=bottom,
            top=top,
            right=right,
            wspace=wspace,
            hspace=hspace,
        )

    def _update_patch_position(self):
        """
        Update the position and size of the patch

        The patch position should be updated whenever the subplot
        parameters change.
        """
        if not hasattr(self, "_patch"):
            return

        ss_bbox = self[0].get_position(None)  # pyright: ignore[reportArgumentType]
        self.patch.set_xy((ss_bbox.x0, ss_bbox.y0))
        self.patch.set_width(ss_bbox.width)
        self.patch.set_height(ss_bbox.height)

    def _update_axes_position(self):
        """
        Update the position of the axes in this gridspec
        """
        for ax in self.figure.axes:
            if ss := ax.get_subplotspec():
                ax._set_position(ss.get_position(self))  # pyright: ignore[reportAttributeAccessIssue, reportArgumentType]

    def _update_artists(self):
        """
        Update the artist positions that depend on this gridspec
        """
        self._update_patch_position()
        self._update_axes_position()
        for gs in self._nested_gridspecs:
            gs._update_artists()

    def update_params_and_artists(self, gsparams: GridSpecParams):
        """
        Update gridpspec params and the artists
        """
        self.update(**asdict(gsparams))
        self._update_artists()

    def get_subplot_params(self, figure=None) -> SubplotParams:
        """
        Return the subplot parameters (in figure coordinates) for the gridspec
        """
        params = self._subplot_params

        if not self.nested:
            return params

        # When the gridspec is nested the subplot params of this gridspec
        # are relative to the position of parent subplot. We want values that
        # are relative to the figure, so we add these param values as offsets
        # to the position of the parent subplot.
        parent_bbox = self._parent_subplot_spec.get_position(figure)  # pyright: ignore
        _left, _bottom, _right, _top = parent_bbox.extents

        left = _left + params.left
        bottom = _bottom + params.bottom
        right = _right - (1 - params.right)
        top = _top - (1 - params.top)

        return SubplotParams(
            left=left,
            bottom=bottom,
            right=right,
            top=top,
            wspace=params.wspace,
            hspace=params.hspace,
        )

    def _get_topmost_subplotspec(self) -> SubplotSpec:
        """
        Return the topmost `.SubplotSpec` instance associated with the subplot.

        This method starts with an underscore so that mpl's GridSpecBase does
        not think that any/all instances of this class are nested. It is then
        only dynamically assigned (without the underscore) to an instance of
        this class when it is nested into a subplot.
        """
        return self._parent_subplot_spec.get_topmost_subplotspec()

    @cached_property
    def parent_gridspec(self) -> p9GridSpec | None:
        if self.nested and (ss := self._parent_subplot_spec):
            return ss.get_gridspec()  # pyright: ignore[reportReturnType]

    @property
    def bbox_relative(self):
        """
        Bounding box for the gridspec relative to the figure

        This bbox is in figure coordinates.
        """
        params = self.get_subplot_params()
        return Bbox.from_extents(
            params.left, params.bottom, params.right, params.top
        )

    @property
    def bbox(self):
        """
        Bounding box of the gridspec

        This bbox is in display coordinates.
        """
        return TransformedBbox(self.bbox_relative, self.figure.transSubfigure)

    @property
    def width(self) -> float:
        """
        Width of bbox in figure space
        """
        return self.bbox_relative.width

    @property
    def height(self) -> float:
        """
        Height of bbox in figure space
        """
        return self.bbox_relative.height

    def to_transform(self) -> Transform:
        """
        Return transform of this gridspec

        Where:
            - (0, 0) is the bottom left of the gridspec
            - (1, 1) is the top right of the gridspec

        The output of this transform is in the display units of the figure.
        """
        return BboxTransformTo(self.bbox)

    def set_height_ratios(self, height_ratios):
        super().set_height_ratios(height_ratios)
        self._update_artists()

    def set_width_ratios(self, width_ratios):
        super().set_width_ratios(width_ratios)
        self._update_artists()

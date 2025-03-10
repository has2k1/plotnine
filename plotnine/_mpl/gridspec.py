from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib.gridspec import GridSpecBase, SubplotParams

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.gridspec import SubplotSpec
    from matplotlib.patches import Rectangle


class p9GridSpec(GridSpecBase):
    """
    Gridspec for plotnine plots

    This gridspec does not read any subplot parameter values from matplotlib's
    rcparams and the default a grid that fills up all the available space;
    there is no space along the edges and between the subplots.

    This gridspec can also be initialised while contained/nested in a given
    subplot.

    Parameters
    ----------
    nest_into :
        If given, this gridspec will be contained in the subplot.
    """

    _figure: Figure | None
    _subplot_params: SubplotParams
    """
    The subplot spacing parameters of this gridspec

    These values are relative to where (figure or subplot) that the
    gridspec is contained. Use .get_subplot_params to get the absolute
    values (those in figure coordinates).
    """
    _patch: Rectangle

    def __init__(
        self,
        nrows,
        ncols,
        figure=None,
        *,
        width_ratios=None,
        height_ratios=None,
        nest_into: SubplotSpec | None = None,
    ):
        super().__init__(
            nrows,
            ncols,
            width_ratios=width_ratios,
            height_ratios=height_ratios,
        )
        self._figure = figure
        if nest_into:
            self._parent_subplot_spec = nest_into
            # MPL GridSpecBase expects only the subclasses that will be nested
            # to have the .get_topmost_subplotspec method.
            self.get_topmost_subplotspec = self._get_topmost_subplotspec

        self.update(
            left=0,
            bottom=0,
            top=1,
            right=1,
            wspace=0,
            hspace=0,
        )

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
        top=None,
        right=None,
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
        self._update_patch_position()
        self._update_axes_position()

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
        try:
            figure = self.figure
        except ValueError:
            return

        # Adapted from matplotlib.figure.Figure.subplots_adjust
        for ax in figure.axes:
            if ss := ax.get_subplotspec():
                ax._set_position(ss.get_position(self))  # pyright: ignore[reportAttributeAccessIssue, reportArgumentType]

    def get_subplot_params(self, figure=None) -> SubplotParams:
        """
        Return the subplot parameters (in figure coordinates) for the gridspec
        """
        params = self._subplot_params

        if not self.nested:
            return params

        # When the gridspec is nested, the parameters are relative the
        # parent subplot. From the position/parameters of parent gridspec,
        # we calculate those of the nested one as offsets.
        parent_bbox = self._parent_subplot_spec.get_position(figure)  # pyright: ignore
        _left, _bottom, _right, _top = parent_bbox.extents
        left = _left + params.left
        right = _right - (1 - params.right)
        bottom = _bottom + params.bottom
        top = _top - (1 - params.top)
        return SubplotParams(
            left=left,
            right=right,
            bottom=bottom,
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

    @property
    def figure(self) -> Figure:
        """
        Return the figure that contains this GridSpec
        """
        if self._figure:
            return self._figure
        elif self.nested:
            gs = self._parent_subplot_spec.get_gridspec()
            if isinstance(gs, p9GridSpec):
                return gs.figure  # pyright: ignore[reportReturnType]
            ss = self.get_topmost_subplotspec()
            return ss._gridspec.figure  # pyright: ignore[reportAttributeAccessIssue]

        raise ValueError(
            "Could not find a figure associated with this GridSpec."
        )

    @figure.setter
    def figure(self, value: Figure):
        self._figure = value

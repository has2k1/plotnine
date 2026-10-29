from __future__ import annotations

import typing
from copy import copy, deepcopy
from functools import cached_property
from typing import Any, Literal, overload

from ..exceptions import PlotnineError
from ..options import get_option, set_option
from .targets import ThemeTargets
from .themeable import Themeables, themeable

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from typing import Protocol, Self, TypeAlias

    from matplotlib import RcParams
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from plotnine import ggplot
    from plotnine._mpl.layout_manager._plot_layout_items import (
        TagLocation,
        TagPosition,
    )
    from plotnine.composition import Compose
    from plotnine.guides.guide import guide
    from plotnine.typing import (
        HorizontalJustification,
        Justification,
        LegendPosition,
        Orientation,
        Side,
        VerticalJustification,
    )

    from .elements import (
        element_blank,
        element_line,
        element_rect,
        element_text,
        margin,
    )

    _Text: TypeAlias = element_text | element_blank
    _Line: TypeAlias = element_line | element_blank
    _Rect: TypeAlias = element_rect | element_blank
    _PanelOrPlot: TypeAlias = Literal["panel", "plot"]

    # callable type representing `Themeables.getp`
    class _GetPCallable(Protocol):
        def __call__(
            self, /, key: str | tuple[str, str], default: Any = None
        ) -> Any: ...


# All complete themes are initiated with these rcparams. They
# can be overridden.
DEFAULT_RCPARAMS = {
    "axes.axisbelow": "True",
    "font.sans-serif": [
        "Helvetica",
        "DejaVu Sans",  # MPL ships with this one
        "Avant Garde",
        "Computer Modern Sans serif",
        "Arial",
    ],
    "font.serif": [
        "Times",
        "Palatino",
        "New Century Schoolbook",
        "Bookman",
        "Computer Modern Roman",
        "Times New Roman",
    ],
    "lines.antialiased": "True",
    "patch.antialiased": "True",
    "timezone": "UTC",
}


class theme:
    """
    Base class for themes

    In general, only complete themes should subclass this class.

    Parameters
    ----------
    complete : bool
        Themes that are complete will override any existing themes.
        themes that are not complete (ie. partial) will add to or
        override specific elements of the current theme. e.g:

        ```python
        theme_gray() + theme_xkcd()
        ```

        will be completely determined by [](`~plotnine.themes.theme_xkcd`),
        but:

        ```python
        theme_gray() + theme(axis_text_x=element_text(angle=45))
        ```

        will only modify the x-axis text.
    kwargs: Any
        kwargs are `themeables`. The themeables are elements that are
        subclasses of `themeable`. Many themeables are defined using
        theme elements i.e

        - [](`~plotnine.themes.element_line`)
        - [](`~plotnine.themes.element_rect`)
        - [](`~plotnine.themes.element_text`)

        These simply bind together all the aspects of a themeable
        that can be themed. See [](`~plotnine.themes.themeable.themeable`).
        Extension packages may provide additional themeables by defining
        and importing subclasses of `themeable`, then passing values for
        them as keyword arguments to `theme`.

    Notes
    -----
    When subclassing, make sure to call `theme.__init__`{.py}.
    After which you can customise `self._rcParams`{.py} within
    the `__init__` method of the new theme. The `rcParams`
    should not be modified after that.
    """

    complete: bool

    # The ggplot, Compose, or guide this theme is bound to.
    # Set in ._setup; figure and axs are derived from it.
    owner: ggplot | Compose | guide

    # Dictionary to collect matplotlib objects that will
    # be targeted for theming by the themeables
    # It is initialised in the ._setup method.
    targets: ThemeTargets
    _is_retina = False

    themeables: Themeables

    def __init__(
        self,
        complete: bool = False,
        # Generated with `tools/_generate_theme_params.py`
        axis_title_x_bottom: _Text | None = None,
        axis_title_x_top: _Text | None = None,
        axis_title_x: _Text | None = None,
        axis_title_y_left: _Text | None = None,
        axis_title_y_right: _Text | None = None,
        axis_title_y: _Text | None = None,
        axis_title: _Text | None = None,
        legend_title: _Text | None = None,
        legend_text_legend: _Text | None = None,
        legend_text_colorbar: _Text | None = None,
        legend_text: _Text | None = None,
        plot_title: _Text | None = None,
        plot_subtitle: _Text | None = None,
        plot_caption: _Text | None = None,
        plot_footer: _Text | None = None,
        plot_tag: _Text | None = None,
        plot_title_position: _PanelOrPlot | None = None,
        plot_caption_position: _PanelOrPlot | None = None,
        plot_footer_position: _PanelOrPlot | None = None,
        plot_tag_location: TagLocation | None = None,
        plot_tag_position: TagPosition | None = None,
        strip_text_x_top: _Text | None = None,
        strip_text_x_bottom: _Text | None = None,
        strip_text_x: _Text | None = None,
        strip_text_y_left: _Text | None = None,
        strip_text_y_right: _Text | None = None,
        strip_text_y: _Text | None = None,
        strip_text: _Text | None = None,
        title: _Text | None = None,
        axis_text_x_bottom: _Text | None = None,
        axis_text_x_top: _Text | None = None,
        axis_text_theta_outside: _Text | None = None,
        axis_text_theta_inside: _Text | None = None,
        axis_text_theta: _Text | None = None,
        axis_text_x: _Text | None = None,
        axis_text_y_left: _Text | None = None,
        axis_text_y_right: _Text | None = None,
        axis_text_r_start: _Text | None = None,
        axis_text_r_end: _Text | None = None,
        axis_text_r: _Text | None = None,
        axis_text_y: _Text | None = None,
        axis_text: _Text | None = None,
        text: _Text | None = None,
        axis_line_x_bottom: _Line | None = None,
        axis_line_x_top: _Line | None = None,
        axis_line_theta_inside: _Line | None = None,
        axis_line_theta_outside: _Line | None = None,
        axis_line_theta: _Line | None = None,
        axis_line_x: _Line | None = None,
        axis_line_y_left: _Line | None = None,
        axis_line_y_right: _Line | None = None,
        axis_line_r_start: _Line | None = None,
        axis_line_r_end: _Line | None = None,
        axis_line_r: _Line | None = None,
        axis_line_y: _Line | None = None,
        axis_line: _Line | None = None,
        axis_ticks_minor_x_bottom: _Line | None = None,
        axis_ticks_minor_x_top: _Line | None = None,
        axis_ticks_minor_theta_outside: _Line | None = None,
        axis_ticks_minor_theta_inside: _Line | None = None,
        axis_ticks_minor_theta: _Line | None = None,
        axis_ticks_minor_x: _Line | None = None,
        axis_ticks_minor_y_left: _Line | None = None,
        axis_ticks_minor_y_right: _Line | None = None,
        axis_ticks_minor_r_start: _Line | None = None,
        axis_ticks_minor_r_end: _Line | None = None,
        axis_ticks_minor_r: _Line | None = None,
        axis_ticks_minor_y: _Line | None = None,
        axis_ticks_major_x_bottom: _Line | None = None,
        axis_ticks_major_x_top: _Line | None = None,
        axis_ticks_major_theta_outside: _Line | None = None,
        axis_ticks_major_theta_inside: _Line | None = None,
        axis_ticks_major_theta: _Line | None = None,
        axis_ticks_major_x: _Line | None = None,
        axis_ticks_major_y_left: _Line | None = None,
        axis_ticks_major_y_right: _Line | None = None,
        axis_ticks_major_r_start: _Line | None = None,
        axis_ticks_major_r_end: _Line | None = None,
        axis_ticks_major_r: _Line | None = None,
        axis_ticks_major_y: _Line | None = None,
        axis_ticks_major: _Line | None = None,
        axis_ticks_minor: _Line | None = None,
        axis_ticks_x: _Line | None = None,
        axis_ticks_y: _Line | None = None,
        axis_ticks: _Line | None = None,
        legend_ticks: _Line | None = None,
        legend_axis_line: _Line | None = None,
        panel_grid_major_x: _Line | None = None,
        panel_grid_major_y: _Line | None = None,
        panel_grid_minor_x: _Line | None = None,
        panel_grid_minor_y: _Line | None = None,
        panel_grid_major: _Line | None = None,
        panel_grid_minor: _Line | None = None,
        panel_grid: _Line | None = None,
        plot_footer_line: _Line | None = None,
        line: _Line | None = None,
        legend_key: _Rect | None = None,
        legend_frame: _Rect | None = None,
        legend_background: _Rect | None = None,
        legend_box_background: _Rect | None = None,
        panel_background: _Rect | None = None,
        panel_border: _Rect | None = None,
        plot_background: _Rect | None = None,
        plot_footer_background: _Rect | None = None,
        strip_background_x: _Rect | None = None,
        strip_background_y: _Rect | None = None,
        strip_background: _Rect | None = None,
        rect: _Rect | None = None,
        axis_ticks_length_major_x: complex | None = None,
        axis_ticks_length_major_y: complex | None = None,
        axis_ticks_length_major_theta: complex | None = None,
        axis_ticks_length_major_r: complex | None = None,
        axis_ticks_length_major: float | None = None,
        axis_ticks_length_minor_x: complex | None = None,
        axis_ticks_length_minor_y: complex | None = None,
        axis_ticks_length_minor_theta: complex | None = None,
        axis_ticks_length_minor_r: complex | None = None,
        axis_ticks_length_minor: complex | None = None,
        axis_ticks_length: complex | None = None,
        panel_spacing_x: float | None = None,
        panel_spacing_y: float | None = None,
        panel_spacing: float | None = None,
        plot_margin_left: float | None = None,
        plot_margin_right: float | None = None,
        plot_margin_top: float | None = None,
        plot_margin_bottom: float | None = None,
        plot_margin: float | None = None,
        panel_ontop: bool | None = None,
        aspect_ratio: float | None = None,
        dpi: float | None = None,
        figure_format: str | None = None,
        figure_size: tuple[float, float] | None = None,
        legend_box: Orientation | None = None,
        legend_box_margin: int | None = None,
        legend_box_just: Justification | Literal["baseline"] | None = None,
        legend_justification_right: (
            VerticalJustification | float | None
        ) = None,
        legend_justification_left: VerticalJustification | float | None = None,
        legend_justification_top: (
            HorizontalJustification | float | None
        ) = None,
        legend_justification_bottom: (
            HorizontalJustification | float | None
        ) = None,
        legend_justification_inside: (
            Justification | float | tuple[float, float] | None
        ) = None,
        legend_justification: (
            Justification | float | tuple[float, float] | None
        ) = None,
        legend_direction: Orientation | None = None,
        legend_key_width: float | None = None,
        legend_key_height: float | None = None,
        legend_key_size: float | None = None,
        legend_ticks_length: float | None = None,
        legend_margin: float | None = None,
        legend_box_spacing: float | None = None,
        legend_spacing: float | None = None,
        legend_position_inside: tuple[float, float] | None = None,
        legend_position: LegendPosition | Literal["none"] | None = None,
        legend_title_position: Side | None = None,
        legend_text_position: (
            Side
            | Literal["top-bottom", "bottom-top", "left-right", "right-left"]
            | Sequence[Side]
            | None
        ) = None,
        legend_key_spacing_x: int | None = None,
        legend_key_spacing_y: int | None = None,
        legend_key_spacing: int | None = None,
        strip_align_x: float | None = None,
        strip_align_y: float | None = None,
        strip_align: float | None = None,
        strip_switch_pad_x: float | None = None,
        strip_switch_pad_y: float | None = None,
        strip_switch_pad: float | None = None,
        strip_placement: Literal["inside", "outside"] | None = None,
        svg_usefonts: bool | None = None,
        **kwargs: Any,
    ) -> None:
        import matplotlib as mpl

        self.themeables = Themeables()
        self.complete = complete

        self._rcParams = mpl.RcParams(DEFAULT_RCPARAMS if complete else {})

        # Themeables
        official_themeables = themeable.registry()
        locals_args = dict(locals())
        it = (
            (name, element)
            for name, element in locals_args.items()
            if element is not None and name in official_themeables
        )
        new = themeable.from_class_name

        for name, element in it:
            self.themeables[name] = new(name, element)

        # Unofficial themeables for extensions
        # or those that have been deprecated
        for name, element in kwargs.items():
            self.themeables[name] = new(name, element)

    def __eq__(self, other: object) -> bool:
        """
        Test if themes are equal

        Mostly for testing purposes
        """
        return other is self or (
            isinstance(other, type(self))
            and other.themeables == self.themeables
            and other.rcParams == self.rcParams
        )

    @cached_property
    def T(self) -> Themeables:
        """
        Convenient access to the themeables
        """
        return self.themeables

    @cached_property
    def getp(self) -> _GetPCallable:
        """
        Convenient access into the properties of the themeables
        """
        return self.themeables.getp

    def get_margin(self, name: str) -> margin:
        """
        Return the margin property of a element_text themeables
        """
        return self.themeables.getp((name, "margin"))

    @cached_property
    def get_ha(self) -> Callable[[str], float]:
        return self.themeables.get_ha

    @cached_property
    def get_va(self) -> Callable[[str], float]:
        return self.themeables.get_va

    def apply(self) -> None:
        """
        Apply this theme, then apply additional modifications in order.

        This method will be called once after plot has completed.
        Subclasses that override this method should make sure that the
        base class method is called.
        """
        for th in self.T.values():
            th.apply(self)

    def _setup(self, owner: ggplot | Compose | guide):
        """
        Bind this theme to its owner

        `theme.figure` and `theme.axs` resolve to the owner's current state
        at access time, so this method can run before the owner's axes are
        created — they will be present by the time `theme.apply()` reads
        `theme.axs`.

        `targets` is initialised here. Re-calling `_setup` rebinds
        `self.owner` and re-creates `targets`.

        Parameters
        ----------
        owner :
            The plot, composition or guide this theme is attached to.
        """
        self.owner = owner

        title, subtitle = self._owner_title_subtitle()
        if title or subtitle:
            self._smart_title_and_subtitle_ha(title, subtitle)

        self.targets = ThemeTargets()
        self.T.setup(self)

    @property
    def figure(self) -> Figure:
        """
        Matplotlib figure the theme renders onto

        Resolves to the owner's figure. All three owner types
        (ggplot, Compose, guide) expose `figure` directly.
        """
        return self.owner.figure

    @property
    def axs(self) -> list[Axes]:
        """
        Axes the theme iterates over at apply time

        Empty for `Compose` and `guide` owners — only ggplot has
        per-panel axes. Reads the owner's current `axs` lazily,
        so this property reflects post-`facet.setup` state even
        if `_setup` ran earlier.
        """
        from ..ggplot import ggplot

        if isinstance(self.owner, ggplot):
            return self.owner.axs
        return []

    def _owner_title_subtitle(self) -> tuple[str | None, str | None]:
        """
        Title and subtitle text from the owner

        ggplot stores these on `labels`; Compose stores them on
        `annotation`; guide has neither.
        """
        from ..composition._compose import Compose
        from ..ggplot import ggplot

        if isinstance(self.owner, ggplot):
            return self.owner.labels.title, self.owner.labels.subtitle
        if isinstance(self.owner, Compose):
            return self.owner.annotation.title, self.owner.annotation.subtitle
        return None, None

    @property
    def rcParams(self) -> RcParams:
        """
        Return rcParams dict for this theme.

        Notes
        -----
        Subclasses should not need to override this method as long as
        self._rcParams is constructed properly.

        rcParams are used during plotting. Sometimes the same theme can be
        achieved by setting rcParams before plotting or a apply
        after plotting. The choice of how to implement it is is a matter of
        convenience in that case.

        There are certain things can only be themed after plotting. There
        may not be an rcParam to control the theme or the act of plotting
        may cause an entity to come into existence before it can be themed.

        """
        try:
            rcParams = deepcopy(self._rcParams)
        except NotImplementedError:
            # deepcopy raises an error for objects that are derived from or
            # composed of matplotlib.transform.TransformNode.
            # Not desirable, but probably requires upstream fix.
            # In particular, XKCD uses matplotlib.patheffects.withStrok
            rcParams = copy(self._rcParams)

        for th in self.T.values():
            rcParams.update(th.rcParams)
        return rcParams

    def add_theme(self, other: theme) -> theme:
        """
        Add themes together

        Subclasses should not override this method.

        This will be called when adding two instances of class 'theme'
        together.
        A complete theme will annihilate any previous themes. Partial themes
        can be added together and can be added to a complete theme.
        """
        if other.complete:
            return other

        self.themeables.update(deepcopy(other.themeables))
        return self

    def __add__(self, other: theme) -> theme:
        """
        Add other theme to this theme
        """
        if not isinstance(other, theme):
            msg = f"Adding theme failed. {other} is not a theme"
            raise PlotnineError(msg)
        self = deepcopy(self)
        return self.add_theme(other)

    @overload
    def __radd__(self, other: theme) -> theme: ...

    @overload
    def __radd__(self, other: ggplot) -> ggplot: ...

    def __radd__(self, other: theme | ggplot) -> theme | ggplot:
        """
        Add theme to ggplot object or to another theme

        This will be called in one of two ways:

        ```python
        ggplot() + theme()
        theme1() + theme2()
        ```

        In both cases, `self` is the [](`~plotnine.themes.theme`)
        on the right hand side.

        Subclasses should not override this method.
        """
        # ggplot() + theme, get theme
        # if hasattr(other, 'theme'):
        if not isinstance(other, theme):
            if self.complete:
                other.theme = self
            else:
                # If no theme has been added yet,
                # we modify the default theme
                other.theme = other.theme or theme_get()
                other.theme = other.theme.add_theme(self)
            return other
        # theme1 + theme2
        else:
            if self.complete:
                # e.g. other + theme_gray()
                return self
            else:
                # e.g. other + theme(...)
                return other.add_theme(self)

    def __iadd__(self, other: theme) -> Self:
        """
        Add theme to theme
        """
        self.add_theme(other)
        return self

    def __deepcopy__(self, memo: dict) -> theme:
        """
        Deep copy without copying the figure
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        shallow = {"plot", "figure", "axs"}
        skip = {"targets"}
        for key, item in old.items():
            if key in skip:
                continue
            elif key in shallow:
                new[key] = item
                memo[id(new[key])] = new[key]
            else:
                new[key] = deepcopy(item, memo)

        return result

    def to_retina(self) -> theme:
        """
        Return a retina-sized version of this theme

        The result is a theme that has double the dpi.
        """
        if self._is_retina:
            return deepcopy(self)

        dpi = self.getp("dpi")
        self = self + theme(dpi=dpi * 2)
        self._is_retina = True
        return self

    def _inherit_figure_props(self, other: theme) -> None:
        """
        Inherit figure properties from another theme

        Plots and guides that share a figure use its owner's size, DPI, and
        output format.
        """
        self.themeables.pop("figure_format", None)
        self += theme(
            figure_size=other.getp("figure_size"),
            dpi=other.getp("dpi"),
            figure_format=other.getp("figure_format"),
        )

    def _smart_title_and_subtitle_ha(
        self, title: str | None, subtitle: str | None
    ):
        """
        Smartly add the horizontal alignment for the title and subtitle
        """
        from .elements import element_text

        has_title = bool(title) and not self.T.is_blank("plot_title")
        has_subtitle = bool(subtitle) and not self.T.is_blank("plot_subtitle")

        title_ha = self.getp(("plot_title", "ha"))
        subtitle_ha = self.getp(("plot_subtitle", "ha"))

        default_title_ha, default_subtitle_ha = "center", "left"
        kwargs = {}

        if has_title and title_ha is None:
            if has_subtitle and not subtitle_ha:
                title_ha = default_subtitle_ha
            else:
                title_ha = default_title_ha
            kwargs["plot_title"] = element_text(ha=title_ha)

        if has_subtitle and subtitle_ha is None:
            subtitle_ha = default_subtitle_ha
            kwargs["plot_subtitle"] = element_text(ha=subtitle_ha)

        if kwargs:
            self += theme(**kwargs)

    @property
    def _figure_size_px(self) -> tuple[int, int]:
        """
        Return the size of the output in pixels
        """
        dpi = self.getp("dpi")
        width, height = self.getp("figure_size")
        return (int(width * dpi), int(height * dpi))


def theme_get() -> theme:
    """
    Return the default theme

    The default theme is the one set (using [](`~plotnine.themes.theme_set`))
    by the user. If none has been set, then [](`~plotnine.themes.theme_gray`)
    is the default.
    """
    from .theme_gray import theme_gray

    _theme = get_option("current_theme")
    if isinstance(_theme, type):
        _theme = _theme()
    return _theme or theme_gray()


def theme_set(new: theme | type[theme]) -> theme:
    """
    Change the current(default) theme

    Parameters
    ----------
    new : theme
        New default theme

    Returns
    -------
    out : theme
        Previous theme
    """
    if not isinstance(new, theme) and not issubclass(new, theme):
        raise PlotnineError("Expecting object to be a theme")

    out: theme = get_option("current_theme")
    set_option("current_theme", new)
    return out


def theme_update(**kwargs: themeable) -> None:
    """
    Modify elements of the current theme

    Parameters
    ----------
    kwargs : dict
        Theme elements
    """
    assert "complete" not in kwargs
    theme_set(theme_get() + theme(**kwargs))  # pyright: ignore

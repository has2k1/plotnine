from __future__ import annotations

import typing
from copy import copy, deepcopy
from functools import cached_property
from typing import overload

from ..exceptions import PlotnineError
from ..options import get_option, set_option
from .targets import ThemeTargets
from .themeable import Themeables, themeable

if typing.TYPE_CHECKING:
    from typing import Type

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from typing_extensions import Self

    from plotnine import ggplot

    from .elements import margin


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

    Notes
    -----
    When subclassing, make sure to call `theme.__init__`{.py}.
    After which you can customise `self._rcParams`{.py} within
    the `__init__` method of the new theme. The `rcParams`
    should not be modified after that.
    """

    complete: bool

    # This is set when the figure is created,
    # it is useful at legend drawing time and
    # when applying the theme.
    plot: ggplot
    figure: Figure
    axs: list[Axes]

    # Dictionary to collect matplotlib objects that will
    # be targeted for theming by the themeables
    # It is initialised in the setup method.
    targets: ThemeTargets

    def __init__(
        self,
        complete=False,
        # Generate themeables keyword parameters with
        #
        #     from plotnine.themes.themeable import themeable
        #     for name in themeable.registry():
        #         print(f'{name}=None,')
        axis_title_x=None,
        axis_title_y=None,
        axis_title=None,
        legend_title=None,
        legend_text_legend=None,
        legend_text_colorbar=None,
        legend_text=None,
        plot_title=None,
        plot_subtitle=None,
        plot_caption=None,
        plot_tag=None,
        plot_title_position=None,
        plot_caption_position=None,
        plot_tag_location=None,
        plot_tag_position=None,
        strip_text_x=None,
        strip_text_y=None,
        strip_text=None,
        title=None,
        axis_text_x=None,
        axis_text_y=None,
        axis_text=None,
        text=None,
        axis_line_x=None,
        axis_line_y=None,
        axis_line=None,
        axis_ticks_minor_x=None,
        axis_ticks_minor_y=None,
        axis_ticks_major_x=None,
        axis_ticks_major_y=None,
        axis_ticks_major=None,
        axis_ticks_minor=None,
        axis_ticks_x=None,
        axis_ticks_y=None,
        axis_ticks=None,
        legend_ticks=None,
        panel_grid_major_x=None,
        panel_grid_major_y=None,
        panel_grid_minor_x=None,
        panel_grid_minor_y=None,
        panel_grid_major=None,
        panel_grid_minor=None,
        panel_grid=None,
        line=None,
        legend_key=None,
        legend_frame=None,
        legend_background=None,
        legend_box_background=None,
        panel_background=None,
        panel_border=None,
        plot_background=None,
        strip_background_x=None,
        strip_background_y=None,
        strip_background=None,
        rect=None,
        axis_ticks_length_major_x=None,
        axis_ticks_length_major_y=None,
        axis_ticks_length_major=None,
        axis_ticks_length_minor_x=None,
        axis_ticks_length_minor_y=None,
        axis_ticks_length_minor=None,
        axis_ticks_length=None,
        panel_spacing_x=None,
        panel_spacing_y=None,
        panel_spacing=None,
        plot_margin_left=None,
        plot_margin_right=None,
        plot_margin_top=None,
        plot_margin_bottom=None,
        plot_margin=None,
        panel_ontop=None,
        aspect_ratio=None,
        dpi=None,
        figure_size=None,
        legend_box=None,
        legend_box_margin=None,
        legend_box_just=None,
        legend_justification_right=None,
        legend_justification_left=None,
        legend_justification_top=None,
        legend_justification_bottom=None,
        legend_justification_inside=None,
        legend_justification=None,
        legend_direction=None,
        legend_key_width=None,
        legend_key_height=None,
        legend_key_size=None,
        legend_ticks_length=None,
        legend_margin=None,
        legend_box_spacing=None,
        legend_spacing=None,
        legend_position_inside=None,
        legend_position=None,
        legend_title_position=None,
        legend_text_position=None,
        legend_key_spacing_x=None,
        legend_key_spacing_y=None,
        legend_key_spacing=None,
        strip_align_x=None,
        strip_align_y=None,
        strip_align=None,
        svg_usefonts=None,
        **kwargs,
    ):
        self.themeables = Themeables()
        self.complete = complete

        if complete:
            self._rcParams = deepcopy(DEFAULT_RCPARAMS)
        else:
            self._rcParams = {}

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
    def T(self):
        """
        Convenient access to the themeables
        """
        return self.themeables

    @cached_property
    def getp(self):
        """
        Convenient access into the properties of the themeables
        """
        return self.themeables.getp

    def get_margin(self, name: str) -> margin:
        """
        Return the margin propery of a element_text themeables
        """
        return self.themeables.getp((name, "margin"))

    @cached_property
    def get_ha(self):
        return self.themeables.get_ha

    @cached_property
    def get_va(self):
        return self.themeables.get_va

    def apply(self):
        """
        Apply this theme, then apply additional modifications in order.

        This method will be called once after plot has completed.
        Subclasses that override this method should make sure that the
        base class method is called.
        """
        for th in self.T.values():
            th.apply(self)

    def setup(self, plot: ggplot):
        """
        Setup theme for applying

        This method will be called when the figure and axes have been created
        but before any plotting or other artists have been added to the
        figure. This method gives the theme and the elements references to
        the figure and/or axes.

        It also initialises where the artists to be themed will be stored.
        """
        self.plot = plot
        self.figure = plot.figure
        self.axs = plot.axs
        self.targets = ThemeTargets()
        self._add_default_themeable_properties()
        self.T.setup(self)

    def _add_default_themeable_properties(self):
        """
        Add default themeable properties that depend depend on the plot

        Some properties may be left unset (None) and their final values are
        best worked out dynamically after the plot has been built, but
        before the themeables are applied.

        This is where the theme is modified to add those values.
        """
        self._smart_title_and_subtitle_ha()

    @property
    def rcParams(self):
        """
        Return rcParams dict for this theme.

        Notes
        -----
        Subclasses should not need to override this method method as long as
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
        dpi = self.getp("dpi")
        return self + theme(dpi=dpi * 2)

    def _smart_title_and_subtitle_ha(self):
        """
        Smartly add the horizontal alignment for the title and subtitle
        """
        from .elements import element_text

        has_title = bool(
            self.plot.labels.get("title", "")
        ) and not self.T.is_blank("plot_title")
        has_subtitle = bool(
            self.plot.labels.get("subtitle", "")
        ) and not self.T.is_blank("plot_subtitle")

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


def theme_set(new: theme | Type[theme]) -> theme:
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


def theme_update(**kwargs: themeable):
    """
    Modify elements of the current theme

    Parameters
    ----------
    kwargs : dict
        Theme elements
    """
    assert "complete" not in kwargs
    theme_set(theme_get() + theme(**kwargs))  # pyright: ignore

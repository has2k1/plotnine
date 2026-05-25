from __future__ import annotations

import abc
from copy import copy, deepcopy
from functools import cached_property
from io import BytesIO
from typing import TYPE_CHECKING, cast, overload

from plotnine.themes.theme import theme, theme_get

from .._utils.context import plot_composition_context
from .._utils.ipython import (
    get_ipython,
    get_mimebundle,
    is_inline_backend,
)
from .._utils.quarto import is_knitr_engine, is_quarto_environment
from ..composition._plot_annotation import plot_annotation
from ..composition._plot_layout import plot_layout
from ..composition._types import ComposeAddable
from ..guides.guides import guides
from ..options import get_option

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Iterator

    from matplotlib.figure import Figure
    from typing_extensions import Self

    from plotnine._mpl.figure import p9Figure
    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine._mpl.layout_manager._composition_side_space import (
        CompositionSideSpaces,
    )
    from plotnine.composition._design import DesignSpec
    from plotnine.composition._guide_area import guide_area
    from plotnine.ggplot import PlotAddable, ggplot
    from plotnine.typing import FigureFormat, MimeBundle


class Compose:
    """
    Base class for those that create plot compositions

    As a user, you will never directly work with this class, except
    through the operators that it makes possible.
    The operators are of two kinds:

    ### 1. Composing Operators

    The combine plots or compositions into a single composition.
    Both operands are either a plot or a composition.

    `/`

    :   Arrange operands side by side.
        Powered by the subclass [](`~plotnine.composition.Beside`).

    `|`

    :   Arrange operands vertically.
        Powered by the subclass [](`~plotnine.composition.Stack`).

    `-`

    :   Arrange operands side by side _and_ at the same nesting level.
        Also powered by the subclass [](`~plotnine.composition.Beside`).

    `+`

    :   Arrange operands in a 2D grid.
        Powered by the subclass [](`~plotnine.composition.Wrap`).

    ### 2. Plot Modifying Operators

    The modify all or some of the plots in a composition.
    The left operand is a composition and the right operand is a
    _plotaddable_; any object that can be added to a `ggplot` object
    e.g. _geoms_, _stats_, _themes_, _facets_, ... .

    `&`

    :   Add right hand side to all plots in the composition.

    `*`

    :   Add right hand side to all plots in the top-most nesting
        level of the composition.

    `+`

    :    Add right hand side to the last plot in the composition.

    Parameters
    ----------
    items :
        The objects to be arranged (composed)


    See Also
    --------
    plotnine.composition.Beside : To arrange plots side by side
    plotnine.composition.Stack : To arrange plots vertically
    plotnine.composition.Wrap : To arrange in a grid
    plotnine.composition.plot_spacer : To add a blank space between plots
    """

    # These are created in the ._create_figure
    figure: p9Figure
    _gridspec: p9GridSpec
    """
    Gridspec (1x1) that contains the annotations and the composition items

    plot_layout's theme parameter affects this gridspec.
    """

    _design_spec: DesignSpec | None = None
    """
    Parsed `plot_layout(design=...)`. `None` when no design is set.
    """

    _sub_gridspec: p9GridSpec
    """
    Gridspec (nxn) that contains the composed [ggplot | Compose] items

     -------------------
    |  title            |<----- ._gridspec
    |  subtitle         |
    |                   |
    |   -------------   |
    |  |      |      |<-+------ ._sub_gridspec
    |  |      |      |  |
    |   -------------   |
    |                   |
    |           caption |
    |-------------------|
    |       footer      |
     -------------------
    """
    _sidespaces: CompositionSideSpaces

    def __init__(self, items: list[ggplot | Compose]):
        # The way we handle the plots has consequences that would
        # prevent having a duplicate plot in the composition.
        # Using copies prevents this.
        self.items = [
            op if isinstance(op, Compose) else deepcopy(op) for op in items
        ]

        self._layout = plot_layout()
        """
        Every composition gets initiated with an empty plot_layout whose
        attributes are either dynamically generated before the composition
        is drawn, or they are overwritten by a layout added by the user.
        """

        self._annotation = plot_annotation()
        """
        The annotations around the composition
        """

        # Composition-level guides populated if "collect"ing
        self.guides = guides()
        self.guides._owner = self

    def __repr__(self):
        """
        repr

        Notes
        -----
        Subclasses that are dataclasses should be declared with
        `@dataclass(repr=False)`.
        """
        # knitr relies on __repr__ to automatically print the last object
        # in a cell.
        if is_knitr_engine():
            self.show()
            return ""
        return super().__repr__()

    @property
    def layout(self) -> plot_layout:
        """
        The plot_layout of this composition
        """
        self.items
        return self._layout

    @layout.setter
    def layout(self, value: plot_layout):
        """
        Add (or merge) a plot_layout to this composition
        """
        self._layout = copy(self.layout)
        self._layout.update(value)

    @property
    def annotation(self) -> plot_annotation:
        """
        The plot_annotation of this composition
        """
        return self._annotation

    @annotation.setter
    def annotation(self, value: plot_annotation):
        """
        Add (or merge) a plot_annotation to this composition
        """
        self._annotation = copy(self.annotation)
        self._annotation.update(value)

    @property
    def nrow(self) -> int:
        return cast("int", self.layout.nrow)

    @property
    def ncol(self) -> int:
        return cast("int", self.layout.ncol)

    @property
    def theme(self) -> theme:
        """
        Theme for this composition

        This is the default theme plus combined with theme from the
        annotation.
        """
        if not getattr(self, "_theme", None):
            self._theme = theme_get() + self.annotation.theme
        return self._theme

    @theme.setter
    def theme(self, value: theme):
        self._theme = value

    @abc.abstractmethod
    def __or__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a column
        """

    @abc.abstractmethod
    def __truediv__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a row
        """

    def __add__(
        self,
        rhs: ggplot | Compose | PlotAddable | ComposeAddable,
    ) -> Compose:
        """
        Add rhs to the composition

        Parameters
        ----------
        rhs:
            What to add to the composition
        """
        from plotnine import ggplot

        self = deepcopy(self)

        if isinstance(rhs, ComposeAddable):
            return rhs.__radd__(self)
        elif not isinstance(rhs, (ggplot, Compose)):
            self.last_plot = self.last_plot + rhs
            return self

        t1, t2 = type(self).__name__, type(rhs).__name__
        msg = f"unsupported operand type(s) for +: '{t1}' and '{t2}'"
        raise TypeError(msg)

    def __sub__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add the rhs onto the composition

        Parameters
        ----------
        rhs:
            What to place besides the composition
        """
        from plotnine import ggplot

        from . import Beside

        if not isinstance(rhs, (ggplot, Compose)):
            t1, t2 = type(self).__name__, type(rhs).__name__
            msg = f"unsupported operand type(s) for -: '{t1}' and '{t2}'"
            raise TypeError(msg)

        return Beside([self, rhs])

    def __and__(self, rhs: PlotAddable) -> Self:
        """
        Add rhs to all plots in the composition

        Recurses into ggplot insets too: a plot with insets receives
        `item & rhs` (which broadcasts to its own host and insets).

        Parameters
        ----------
        rhs:
            What to add.
        """
        from plotnine import ggplot, theme

        self = deepcopy(self)

        if isinstance(rhs, theme):
            self.annotation.theme = self.annotation.theme + rhs

        for i, item in enumerate(self):
            if isinstance(item, Compose) or (
                isinstance(item, ggplot) and item._insets
            ):
                self[i] = item & rhs
            else:
                item += copy(rhs)

        return self

    def __mul__(self, rhs: PlotAddable) -> Self:
        """
        Add rhs to the outermost nesting level of the composition

        Parameters
        ----------
        rhs:
            What to add.
        """
        from plotnine import ggplot

        self = deepcopy(self)

        for item in self:
            if isinstance(item, ggplot):
                item += copy(rhs)

        return self

    def __len__(self) -> int:
        """
        Number of operands
        """
        return len(self.items)

    def __iter__(self) -> Iterator[ggplot | Compose]:
        """
        Return an iterable of all the items
        """
        return iter(self.items)

    @overload
    def __getitem__(self, index: int) -> ggplot | Compose: ...

    @overload
    def __getitem__(self, index: slice) -> list[ggplot | Compose]: ...

    def __getitem__(
        self,
        index: int | slice,
    ) -> ggplot | Compose | list[ggplot | Compose]:
        return self.items[index]

    def __setitem__(self, key, value):
        self.items[key] = value

    def _repr_mimebundle_(self, include=None, exclude=None) -> MimeBundle:
        """
        Return dynamic MIME bundle for composition display
        """
        ip = get_ipython()
        format: FigureFormat = (
            get_option("figure_format")
            or (ip and ip.config.InlineBackend.get("figure_format"))
            or "retina"
        )

        if format == "retina":
            self = deepcopy(self)
            self._to_retina()

        buf = BytesIO()
        self.save(buf, "png" if format == "retina" else format)
        figure_size_px = self.theme._figure_size_px
        return get_mimebundle(buf.getvalue(), format, figure_size_px)

    def iter_sub_compositions(self):
        for item in self:
            if isinstance(item, Compose):
                yield item

    def iter_plots(self):
        from plotnine import ggplot

        for item in self:
            if isinstance(item, ggplot):
                yield item

    def iter_plots_all(self):
        """
        Recursively generate all plots under this composition
        """
        for plot in self.iter_plots():
            yield plot

        for cmp in self.iter_sub_compositions():
            yield from cmp.iter_plots_all()

    def _resolve_guide_owners(self, owner: Compose | None = None):
        """
        Decide which `Compose` (if any) owns each leaf's guides

        Walks the composition tree and overrides `leaf.guides._owner`
        to the nearest `"collect"` ancestor (with `"keep"`
        interrupting propagation). Leaves not under a collector keep
        their default `_owner = leaf` from `ggplot.__init__`.

        Parameters
        ----------
        owner :
            The `Compose` inherited as guide owner from a higher
            ancestor, or `None` if no `"collect"` ancestor is active.
        """
        from plotnine import ggplot

        own = self.layout.guides
        if own == "keep":
            new_owner = None
        elif own == "collect":
            new_owner = self
        else:  # None — propagate inherited owner unchanged
            new_owner = owner

        for item in self:
            if isinstance(item, ggplot):
                # If the guides are inside a plot, they are not "collected"
                # / assigned to any composition.
                # And, always assign the ggplot as the owner to guard against
                # prior (and now stale) ownership when the same plot is
                # reused in different compositions
                if new_owner is not None and not _renders_legend_inside(
                    item.theme
                ):
                    item.guides._owner = new_owner
                else:
                    item.guides._owner = item
            else:
                item._resolve_guide_owners(owner=new_owner)

    def _walk_guide_owners(self):
        """
        Yield every composition in this tree that collects guides

        A composition is a guide owner when its
        `layout.guides == "collect"`. Includes `self` if it qualifies.
        """
        if self.layout.guides == "collect":
            yield self
        for sub in self.iter_sub_compositions():
            yield from sub._walk_guide_owners()

    @cached_property
    def _guide_area(self) -> guide_area | None:
        """
        The cell that hosts this composition's collected legend

        Only a `guide_area` placed directly at this composition's
        level is eligible; one nested inside a sub-composition
        belongs to that sub-grid, so an outer collector cannot
        reach it.

        Returns
        -------
        out :
            The first matching `guide_area` among the composition's
            direct items, or `None` when no eligible cell exists —
            in which case collected guides fall back to side
            placement.
        """
        from ._guide_area import guide_area

        for item in self.iter_plots():
            if isinstance(item, guide_area):
                return item
        return None

    @property
    def last_plot(self) -> ggplot:
        """
        Last plot added to the composition
        """
        from plotnine import ggplot

        last_operand = self.items[-1]
        if isinstance(last_operand, ggplot):
            return last_operand
        else:
            return last_operand.last_plot

    @last_plot.setter
    def last_plot(self, plot: ggplot):
        """
        Replace the last plot in the composition
        """
        from plotnine import ggplot

        last_operand = self.items[-1]
        if isinstance(last_operand, ggplot):
            self.items[-1] = plot
        else:
            last_operand.last_plot = plot

    def __deepcopy__(self, memo):
        """
        Deep copy without copying the figure
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        shallow = {"figure", "gridsspec", "__copy"}
        for key, item in old.items():
            if key in shallow:
                new[key] = item
                memo[id(new[key])] = new[key]
            else:
                new[key] = deepcopy(item, memo)

        old["__copy"] = result

        return result

    def _to_retina(self):
        from plotnine import ggplot

        self.theme = self.theme.to_retina()

        for item in self:
            if isinstance(item, ggplot):
                item.theme = item.theme.to_retina()
            else:
                item._to_retina()

    def _setup(self) -> Figure:
        """
        Setup this instance for the building process
        """
        self._create_figure()
        return self.figure

    def _create_figure(self):
        """
        Create figure & gridspecs for all sub compositions
        """
        if not hasattr(self, "figure"):
            import matplotlib.pyplot as plt

            from plotnine._mpl.figure import p9Figure
            from plotnine._mpl.layout_manager import PlotnineLayoutEngine

            self.figure = cast("p9Figure", plt.figure(FigureClass=p9Figure))
            self.figure.set_layout_engine(PlotnineLayoutEngine(self))

        if not hasattr(self, "_gridspec"):
            from plotnine._mpl.gridspec import p9GridSpec

            self._generate_gridspecs(
                self.figure,
                p9GridSpec(1, 1, self.figure, nest_into=None),
            )

    def _generate_gridspecs(self, figure: p9Figure, container_gs: p9GridSpec):
        from plotnine import ggplot
        from plotnine._mpl.gridspec import p9GridSpec

        self.figure = figure
        self._gridspec = container_gs
        self.layout._setup(self)
        self._sub_gridspec = p9GridSpec.from_layout(
            self.layout, figure=figure, nest_into=container_gs[0]
        )

        # Iterating over the gridspec yields the SubplotSpecs for each
        # "subplot" in the grid. The SubplotSpec is the handle for the
        # area in the grid; it allows us to put a plot or a nested
        # composion in that area.
        # With plot_layout(design=...), each item gets a SubplotSpec
        # sliced from its rectangle (potentially spanning multiple cells)
        # instead of one cell per item.
        if (spec := getattr(self, "_design_spec", None)) is not None:
            pairs = list(zip(self, spec.get_subplotspecs(self._sub_gridspec)))
        else:
            pairs = list(zip(self, self._sub_gridspec))

        for item, subplot_spec in pairs:
            # This container gs will contain a plot or a composition,
            # i.e. it will be assigned to one of:
            #    1. ggplot._gridspec
            #    2. compose._gridspec
            _container_gs = p9GridSpec(1, 1, figure, nest_into=subplot_spec)
            if isinstance(item, ggplot):
                item.figure = figure
                item._gridspec = _container_gs
            else:
                item._generate_gridspecs(figure, _container_gs)

    def show(self):
        """
        Display plot in the cells output

        This function is called for its side-effects.
        """
        # Prevent against any modifications to the users
        # ggplot object. Do the copy here as we may/may not
        # assign a default theme
        self = deepcopy(self)

        if is_inline_backend() or is_quarto_environment():
            from IPython.display import display

            data, metadata = self._repr_mimebundle_()
            display(data, metadata=metadata, raw=True)
        else:
            self.draw(show=True)

    def draw(self, *, show: bool = False) -> Figure:
        """
        Render the arranged plots

        Parameters
        ----------
        show :
            Whether to show the plot.

        Returns
        -------
        :
            Matplotlib figure
        """

        def _draw_items(cmp):
            # Propagate figure-owner-only theme props (figure_size,
            # dpi, ...) onto direct children so child layout uses
            # the composition's values. Then walk plots and
            # sub-compositions.
            for item in cmp:
                item.theme._inherit_figure_props(cmp.theme)
            cmp._draw_plots()
            for sub_cmp in cmp.iter_sub_compositions():
                sub_cmp._setup()
                # Initialise the sub-cmp's theme targets so a
                # downstream `cmp.guides.draw()` (or annotation pass)
                # can write into `sub_cmp.theme.targets`.
                sub_cmp.theme._setup(sub_cmp)
                _draw_items(sub_cmp)

        # Drawing (order matters)
        with plot_composition_context(self, show):
            figure = self._setup()
            self.theme._setup(self)
            self._draw_composition_background()
            self._resolve_guide_owners()
            _draw_items(self)
            # Render guides at every collecting Compose — each binds
            # itself as the owner just before drawing.
            for cmp in self._walk_guide_owners():
                cmp.guides._bind_owner(cmp)
                cmp.guides.draw()
            self._draw_annotation()
            self.theme.apply()

        return figure

    def _draw_plots(self):
        """
        Draw all plots in the composition
        """
        from plotnine import ggplot

        for item in self:
            if isinstance(item, ggplot):
                item.draw()

    def _draw_composition_background(self):
        """
        Draw the background rectangle of the composition
        """
        from matplotlib.lines import Line2D
        from matplotlib.patches import Rectangle

        rect = Rectangle((0, 0), 0, 0, facecolor="none")
        self.figure.add_artist(rect)
        self._gridspec.patch = rect
        self.theme.targets.plot_background = rect

        if self.annotation.footer:
            rect = Rectangle((0, 0), 0, 0, facecolor="none", linewidth=0)
            self.figure.add_artist(rect)
            self.theme.targets.plot_footer_background = rect

            line = Line2D([0, 0], [0, 0], color="none", linewidth=0)
            self.figure.add_artist(line)
            self.theme.targets.plot_footer_line = line

    def _draw_annotation(self):
        """
        Draw the items in the annotation

        Note that, this method puts the artists on the figure, and
        the layout manager moves them to their final positions.
        """
        if self.annotation.empty():
            return

        from matplotlib.text import Text

        targets = self.theme.targets

        if title := self.annotation.title:
            targets.plot_title = self.figure.add_artist(Text(text=title))

        if subtitle := self.annotation.subtitle:
            targets.plot_subtitle = self.figure.add_artist(Text(text=subtitle))

        if caption := self.annotation.caption:
            targets.plot_caption = self.figure.add_artist(Text(text=caption))

        if footer := self.annotation.footer:
            targets.plot_footer = self.figure.add_artist(Text(text=footer))

    def save(
        self,
        filename: str | Path | BytesIO,
        format: str | None = None,
        dpi: int | None = None,
        **kwargs,
    ):
        """
        Save a composition as an image file

        Parameters
        ----------
        filename :
            File name to write the plot to. If not specified, a name
        format :
            Image format to use, automatically extract from
            file name extension.
        dpi :
            DPI to use for raster graphics. If None, defaults to using
            the `dpi` of theme to the first plot.
        **kwargs :
            These are ignored. Here to "softly" match the API of
            `ggplot.save()`.
        """
        from plotnine import theme

        # To set the dpi, we only need to change the dpi of
        # the last plot and theme gets added to the last plot
        plot = (self + theme(dpi=dpi)) if dpi else self
        figure = plot.draw()
        figure.savefig(filename, format=format)


def _renders_legend_inside(t: theme) -> bool:
    """
    Whether the theme places the legend inside the panel area

    True for the string `"inside"` and for a tuple `(x, y)` value
    of `legend_position`, which is also interpreted as an inside
    position.
    """
    pos = t.getp("legend_position")
    return pos == "inside" or isinstance(pos, tuple)

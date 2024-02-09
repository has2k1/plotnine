from __future__ import annotations

import typing
from contextlib import suppress
from warnings import warn

import numpy as np
import pandas as pd

from ._utils import array_kind
from ._utils.registry import Registry
from .exceptions import PlotnineError, PlotnineWarning
from .facets import facet_grid, facet_null, facet_wrap
from .facets.facet_grid import parse_grid_facets_old
from .facets.facet_wrap import parse_wrap_facets_old
from .ggplot import ggplot
from .labels import labs
from .mapping.aes import ALL_AESTHETICS, SCALED_AESTHETICS, aes
from .scales import lims, scale_x_log10, scale_y_log10
from .themes import theme

if typing.TYPE_CHECKING:
    from typing import Any, Iterable, Literal, Optional

    from plotnine.typing import DataLike, TupleFloat2

__all__ = ("qplot",)


def qplot(
    x: Optional[str | Iterable[Any] | range] = None,
    y: Optional[str | Iterable[Any] | range] = None,
    data: Optional[DataLike] = None,
    facets: str = "",
    margins: bool | list[str] = False,
    geom: str | list[str] | tuple[str] = "auto",
    xlim: Optional[TupleFloat2] = None,
    ylim: Optional[TupleFloat2] = None,
    log: Optional[Literal["x", "y", "xy"]] = None,
    main: Optional[str] = None,
    xlab: Optional[str] = None,
    ylab: Optional[str] = None,
    asp: Optional[float] = None,
    **kwargs: Any,
) -> ggplot:
    """
    Quick plot

    Parameters
    ----------
    x :
        x aesthetic
    y :
        y aesthetic
    data :
        Data frame to use (optional). If not specified,
        will create one, extracting arrays from the
        current environment.
    geom :
        *geom(s)* to do the drawing. If `auto`, defaults
        to 'point' if `x` and `y` are specified or
        'histogram' if only `x` is specified.
    facets :
        Facets
    margins :
        variable names to compute margins for. True will compute
        all possible margins. Depends on the facetting.
    xlim :
        x-axis limits
    ylim :
        y-axis limits
    log :
        Which (if any) variables to log transform.
    main :
        Plot title
    xlab :
        x-axis label
    ylab :
        y-axis label
    asp :
        The y/x aspect ratio.
    **kwargs :
        Arguments passed on to the geom.

    Returns
    -------
    :
        ggplot object
    """
    from .mapping._env import Environment

    # Extract all recognizable aesthetic mappings from the parameters
    # String values e.g  "I('red')", "I(4)" are not treated as mappings
    environment = Environment.capture(1)
    aesthetics = {} if x is None else {"x": x}
    if y is not None:
        aesthetics["y"] = y

    def is_mapping(value: Any) -> bool:
        """
        Return True if value is not enclosed in I() function
        """
        with suppress(AttributeError):
            return not (value.startswith("I(") and value.endswith(")"))
        return True

    def I(value: Any) -> Any:
        return value

    I_env = Environment([{"I": I}])

    for ae in kwargs.keys() & ALL_AESTHETICS:
        value = kwargs[ae]
        if is_mapping(value):
            aesthetics[ae] = value
        else:
            kwargs[ae] = I_env.eval(value)

    # List of geoms
    if isinstance(geom, str):
        geom = [geom]
    elif isinstance(geom, tuple):
        geom = list(geom)

    if data is None:
        data = pd.DataFrame()

    # Work out plot data, and modify aesthetics, if necessary
    def replace_auto(lst: list[str], str2: str) -> list[str]:
        """
        Replace all occurences of 'auto' in with str2
        """
        for i, value in enumerate(lst):
            if value == "auto":
                lst[i] = str2
        return lst

    if "auto" in geom:
        if "sample" in aesthetics:
            replace_auto(geom, "qq")
        elif y is None:
            # If x is discrete we choose geom_bar &
            # geom_histogram otherwise. But we need to
            # evaluate the mapping to find out the dtype
            env = environment.with_outer_namespace({"factor": pd.Categorical})

            if isinstance(aesthetics["x"], str):
                try:
                    x = env.eval(
                        aesthetics["x"],
                        inner_namespace=data,  # type: ignore
                    )
                except Exception as e:
                    msg = f"Could not evaluate aesthetic 'x={aesthetics['x']}'"
                    raise PlotnineError(msg) from e
            elif not hasattr(aesthetics["x"], "dtype"):
                x = np.asarray(aesthetics["x"])

            if array_kind.discrete(x):
                replace_auto(geom, "bar")
            else:
                replace_auto(geom, "histogram")

        else:
            if x is None:
                if isinstance(aesthetics["y"], typing.Sized):
                    aesthetics["x"] = range(len(aesthetics["y"]))
                    xlab = "range(len(y))"
                    ylab = "y"
                else:
                    # We could solve the issue in layer.compute_asthetics
                    # but it is not worth the extra complexity
                    raise PlotnineError("Cannot infer how long x should be.")
            replace_auto(geom, "point")

    p: ggplot = ggplot(data, aes(**aesthetics))
    p.environment = environment

    def get_facet_type(facets: str) -> Literal["grid", "wrap", "null"]:
        with suppress(PlotnineError):
            parse_grid_facets_old(facets)
            return "grid"

        with suppress(PlotnineError):
            parse_wrap_facets_old(facets)
            return "wrap"

        warn(
            "Could not determine the type of faceting, "
            "therefore no faceting.",
            PlotnineWarning,
        )
        return "null"

    if facets:
        facet_type = get_facet_type(facets)
        if facet_type == "grid":
            p += facet_grid(facets, margins=margins)
        elif facet_type == "wrap":
            p += facet_wrap(facets)
        else:
            p += facet_null()

    # Add geoms
    for g in geom:
        geom_name = f"geom_{g}"
        geom_klass = Registry[geom_name]
        stat_name = f"stat_{geom_klass.DEFAULT_PARAMS['stat']}"
        stat_klass = Registry[stat_name]
        # find params
        recognized = kwargs.keys() & (
            geom_klass.DEFAULT_PARAMS.keys()
            | geom_klass.aesthetics()
            | stat_klass.DEFAULT_PARAMS.keys()
            | stat_klass.aesthetics()
        )
        recognized = recognized - aesthetics.keys()
        params = {ae: kwargs[ae] for ae in recognized}
        p += geom_klass(**params)

    # pd.Series objects have name attributes. In a dataframe, the
    # series have the name of the column.
    labels = {}
    for ae in SCALED_AESTHETICS & kwargs.keys():
        with suppress(AttributeError):
            labels[ae] = kwargs[ae].name

    with suppress(AttributeError):
        labels["x"] = xlab if xlab is not None else x.name  # type: ignore

    with suppress(AttributeError):
        labels["y"] = ylab if ylab is not None else y.name  # type: ignore

    if main is not None:
        labels["title"] = main

    if log:
        if "x" in log:
            p += scale_x_log10()

        if "y" in log:
            p += scale_y_log10()

    if labels:
        p += labs(**labels)

    if asp:
        p += theme(aspect_ratio=asp)

    if xlim:
        p += lims(x=xlim)

    if ylim:
        p += lims(y=ylim)

    return p

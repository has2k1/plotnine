from __future__ import annotations

import typing

from .._utils import SIZE_FACTOR, to_rgba
from ..coords import coord_flip
from ..doctools import document
from ..exceptions import PlotnineError
from .geom import geom
from .geom_path import geom_path
from .geom_polygon import geom_polygon

if typing.TYPE_CHECKING:
    from typing import Any

    import pandas as pd
    from matplotlib.axes import Axes

    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view
    from plotnine.typing import ColorsLike


@document
class geom_ribbon(geom):
    """
    Ribbon plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    outline_type : Literal["upper", "lower", "both", "full"], default="both"
        How to stroke to outline of the region / area.
        If `upper`, draw only upper bounding line.
        If `lower`, draw only lower bounding line.
        If `both`, draw both upper & lower bounding lines.
        If `full`, draw closed polygon around the area.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Aesthetics Descriptions**

    `where`

    :   Define where to exclude horizontal regions from being filled.
        Regions between any two `False` values are skipped.
        For sensible demarcation the value used in the *where* predicate
        expression should match the `ymin` value or expression. i.e.

        ```python
         aes(ymin=0, ymax="col1", where="col1 > 0")  # good
         aes(ymin=0, ymax="col1", where="col1 > 10")  # bad

         aes(ymin=col2, ymax="col1", where="col1 > col2")  # good
         aes(ymin=col2, ymax="col1", where="col1 > col3")  # bad
        ```
    """
    DEFAULT_AES = {
        "alpha": 1,
        "color": "none",
        "fill": "#333333",
        "linetype": "solid",
        "size": 0.5,
        "where": True,
    }
    REQUIRED_AES = {"x", "ymax", "ymin"}
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "outline_type": "both",
        "na_rm": False,
    }
    draw_legend = staticmethod(geom_polygon.draw_legend)

    def handle_na(self, data: pd.DataFrame) -> pd.DataFrame:
        return data

    def setup_data(self, data: pd.DataFrame) -> pd.DataFrame:
        # The outlines need x and y coordinates
        if self.params["outline_type"] in ("upper", "lower", "both"):
            if "xmax" in data and "x" not in data:
                data["x"] = data["xmax"]
            if "ymax" in data and "y" not in data:
                data["y"] = data["ymax"]
        return data

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        **params: Any,
    ):
        _x = "y" if isinstance(coord, coord_flip) else "x"
        data = coord.transform(data, panel_params, munch=True)
        data = data.sort_values(by=["group", _x], kind="mergesort")
        units = ["alpha", "color", "fill", "linetype", "size"]

        if len(data[units].drop_duplicates()) > 1:
            msg = "Aesthetics cannot vary within a ribbon."
            raise PlotnineError(msg)

        for _, udata in data.groupby(units, dropna=False):
            udata.reset_index(inplace=True, drop=True)
            geom_ribbon.draw_unit(udata, panel_params, coord, ax, **params)

    @staticmethod
    def draw_unit(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        **params: Any,
    ):
        size = data["size"].iloc[0] * SIZE_FACTOR
        fill = to_rgba(data["fill"], data["alpha"])

        if data["color"].isna().all():
            color: ColorsLike = "none"
        else:
            color = data["color"]

        if fill is None:
            fill = "none"

        if isinstance(coord, coord_flip):
            fill_between = ax.fill_betweenx
            _x, _min, _max = data["y"], data["xmin"], data["xmax"]
        else:
            fill_between = ax.fill_between
            _x, _min, _max = data["x"], data["ymin"], data["ymax"]

        # We only change this defaults for fill_between when necessary
        where = data.get("where", None)
        interpolate = not (where is None or where.all())

        if params["outline_type"] != "full":
            size = 0
            color = "none"

        fill_between(
            _x,
            _min,
            _max,
            where=where,  # type: ignore
            interpolate=interpolate,
            facecolor=fill,
            edgecolor=color,
            linewidth=size,
            linestyle=data["linetype"].iloc[0],
            zorder=params["zorder"],
            rasterized=params["raster"],
        )

        # Alpha does not affect the outlines
        data["alpha"] = 1
        geom_ribbon._draw_outline(data, panel_params, coord, ax, **params)

    @staticmethod
    def _draw_outline(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        **params: Any,
    ):
        outline_type = params["outline_type"]

        if outline_type == "full":
            return

        x, y = "x", "y"
        if isinstance(coord, coord_flip):
            x, y = y, x
            data[x], data[y] = data[y], data[x]

        if outline_type in ("lower", "both"):
            geom_path.draw_group(
                data.eval(f"y = {y}min"), panel_params, coord, ax, **params
            )

        if outline_type in ("upper", "both"):
            geom_path.draw_group(
                data.eval(f"y = {y}max"), panel_params, coord, ax, **params
            )

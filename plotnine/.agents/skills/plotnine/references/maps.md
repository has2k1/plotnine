# Maps

Geographic plotting with `geom_map()`. Plotnine consumes
GeoPandas GeoDataFrames directly; Shapely
geometries are read via the GeoDataFrame's `geometry` column.

## Data Model

A GeoDataFrame is a pandas DataFrame with a `geometry` column of
Shapely shapes (points, lines, polygons). Data for plotting typically
comes from:

- **Shapefiles / GeoJSON** — `geopandas.read_file("...")`.
- **geodatasets** — curated
  sample datasets: `geopandas.read_file(geodatasets.get_path("name"))`.
- **Joined attribute tables** — merge a GeoDataFrame with a regular
  DataFrame on a shared key to attach values to regions.

## Basic Map

`geom_map()` plots each geometry in the active GeoDataFrame. Pair it
with `coord_fixed()` to preserve aspect ratio (essential — without it,
shapes stretch with the plot panel).

```python
from plotnine import *
import geopandas as gpd
import geodatasets

nybb = gpd.read_file(geodatasets.get_path("nybb"))

(
    ggplot(nybb)
    + geom_map(fill="#CCCCCC", color="white")
    + coord_fixed()
    + labs(title="New York City Boroughs")
)
```

## Choropleth

Map a numeric column to `fill` inside `aes()`. The fill scale controls
the color mapping.

```python
from plotnine import *
import geopandas as gpd
import geodatasets

nybb = gpd.read_file(geodatasets.get_path("nybb"))

(
    ggplot(nybb, aes(fill="Shape_Area"))
    + geom_map(color="white")
    + scale_fill_cmap(cmap_name="viridis")
    + coord_fixed()
    + labs(title="NYC Boroughs by Area", fill="Shape Area")
)
```

For a diverging scale centered on a reference value, use
`scale_fill_gradient2()`:

```python
scale_fill_gradient2(low="#2166AC", mid="#F7F7F7", high="#B2182B", midpoint=0)
```

## Styling

`theme_void()` strips axes, ticks, and panel — usually what you want
for a map.

```python
from plotnine import *
import geopandas as gpd
import geodatasets

nybb = gpd.read_file(geodatasets.get_path("nybb"))

(
    ggplot(nybb, aes(fill="Shape_Area"))
    + geom_map(color="white", size=0.3)
    + scale_fill_cmap(cmap_name="YlOrRd")
    + coord_fixed()
    + theme_void()
    + labs(title="NYC Boroughs", fill="Area")
)
```

To remove borders set `color="none"`; to fill with the default but
without borders, keep `fill` and drop `color`.

## Handling Missing Data

Rows with NA in the fill column receive the scale's `na_value`.

```python
scale_fill_cmap(cmap_name="viridis", na_value="#DDDDDD")
```

The same pattern works for `scale_fill_continuous`,
`scale_fill_gradient`, and `scale_fill_gradient2`.

## Layering Multiple Maps

Stack `geom_map()` calls with different `data=` arguments to overlay
layers (e.g., administrative boundaries on top of a choropleth).

```python
from plotnine import *
import geopandas as gpd
import geodatasets

nybb = gpd.read_file(geodatasets.get_path("nybb"))
# In a real workflow, `points` would be a second GeoDataFrame.
# For illustration we reuse the borough centroids:
centroids = nybb.copy()
centroids["geometry"] = centroids.geometry.centroid

(
    ggplot()
    + geom_map(nybb, aes(fill="Shape_Area"), color="white")
    + geom_map(centroids, color="black", size=2)
    + scale_fill_cmap(cmap_name="viridis")
    + coord_fixed()
    + theme_void()
    + labs(title="Boroughs with Centroid Markers", fill="Area")
)
```

Layering respects draw order: later layers paint on top.

## Common Pitfalls

- **Omitting `coord_fixed()`**: without it, the map distorts as the
  plot panel changes aspect ratio. Always pair `geom_map()` with
  `coord_fixed()` unless you explicitly want the distortion.

- **CRS mismatches across layers**: when overlaying two GeoDataFrames,
  reproject them to a common CRS first (`.to_crs(epsg=...)`). Mixed
  coordinate reference systems silently misalign features.

- **`color="none"` vs `color=None`**: use the string `"none"` (or
  `"None"`) to suppress borders. `None` (Python literal) is not
  accepted.

- **Very large GeoDataFrames**: `geom_map()` draws every vertex.
  Simplify geometries (`gdf.geometry = gdf.geometry.simplify(tol)`)
  for millions-of-points datasets before plotting.

## See Also

- [geoms.md](geoms.md) — other geoms (points, lines, polygons)
- [aesthetics-and-scales.md](aesthetics-and-scales.md) — continuous
  fill scales, legend customization
- [color-and-accessibility.md](color-and-accessibility.md) —
  colorblind-safe palettes for choropleths
- [coords-and-axes.md](coords-and-axes.md) — coordinate systems

# Aesthetics and Scales

Aesthetics map data variables to visual properties. Scales control how those
mappings translate to visual output — colors, sizes, axis positions, etc.

## Reading Order

| Task                                | Read in order                                      |
|-------------------------------------|----------------------------------------------------|
| Map a variable to a visual property | Mapping vs Setting → Aesthetic Channels            |
| Pick a scale                        | Scale Families → `api/scale_<...>.md`              |
| Customize a scale (breaks, labels)  | Scale Families → `api/scale_<axis>_<type>.md`      |
| Customize a legend or guide         | Legends and Guides                                 |
| Use a stat-computed variable        | Computed Aesthetics                                |

Per-scale parameter reference and single-scale examples live at
`api/scale_<name>.md`. This file covers the cross-cutting concepts.

## Mapping vs Setting

### Mapping a variable (inside `aes()`)

Maps a column to a visual property. plotnine creates a legend automatically.

```python
from plotnine import *
from plotnine.data import penguins

(
    ggplot(penguins.dropna(), aes(x="bill_length_mm", y="bill_depth_mm", color="species"))
    + geom_point()
    + labs(x="Bill Length (mm)", y="Bill Depth (mm)", title="Penguin Bill Dimensions", color="Species")
)
```

### Setting a fixed value (outside `aes()`)

Applies a constant visual property to all points. No legend is created.

```python
from plotnine import *
from plotnine.data import penguins

(
    ggplot(penguins.dropna(), aes(x="bill_length_mm", y="bill_depth_mm"))
    + geom_point(color="steelblue", alpha=0.6)
    + labs(x="Bill Length (mm)", y="Bill Depth (mm)", title="Penguin Bill Dimensions")
)
```

## Aesthetic Channels

| Aesthetic  | Description                      | Typical geoms                                        |
|------------|----------------------------------|------------------------------------------------------|
| `x`, `y`   | Position                         | All                                                  |
| `color`    | Outline / line color             | `geom_point`, `geom_line`, `geom_bar`                |
| `fill`     | Interior fill color              | `geom_bar`, `geom_boxplot`, `geom_area`, `geom_tile` |
| `size`     | Point/line size                  | `geom_point`, `geom_line`                            |
| `shape`    | Point shape                      | `geom_point` (discrete only)                         |
| `alpha`    | Transparency (0–1)               | All                                                  |
| `linetype` | Line style (solid, dashed, etc.) | `geom_line`, `geom_smooth`                           |
| `group`    | Grouping (no legend)             | `geom_line`, `geom_boxplot`                          |

## Scale Families

Every aesthetic has a corresponding `scale_*` function family:

| Aesthetic | Discrete                                                      | Continuous                                                           |
|-----------|---------------------------------------------------------------|----------------------------------------------------------------------|
| `color`   | `scale_color_brewer`, `scale_color_manual`, `scale_color_hue` | `scale_color_cmap`, `scale_color_gradient`, `scale_color_continuous` |
| `fill`    | `scale_fill_brewer`, `scale_fill_manual`, `scale_fill_hue`    | `scale_fill_cmap`, `scale_fill_gradient`, `scale_fill_continuous`    |
| `x`       | `scale_x_discrete`                                            | `scale_x_continuous`, `scale_x_log10`, `scale_x_datetime`            |
| `y`       | `scale_y_discrete`                                            | `scale_y_continuous`, `scale_y_log10`, `scale_y_datetime`            |
| `size`    | `scale_size_discrete`                                         | `scale_size_continuous`, `scale_size_area`                           |
| `shape`   | `scale_shape_discrete`, `scale_shape_manual`                  | —                                                                    |
| `alpha`   | `scale_alpha_discrete`                                        | `scale_alpha_continuous`                                             |

Per-scale parameter surface, defaults, and single-scale examples live
at `api/<scale-name>.md` (e.g. `api/scale_color_brewer.md`).

## Computed Aesthetics

### after_stat

Use `after_stat()` to map computed statistics instead of raw data columns.
The computed variable name depends on the stat (e.g., `stat_bin` computes
`count`, `density`, `ncount`, `ndensity`).

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds, aes(x="carat"))
    + geom_histogram(aes(y=after_stat("density")), binwidth=0.1)
    + geom_density(color="red")
    + labs(x="Carat", y="Density", title="Histogram with Density Overlay")
)
```

### stage

`stage()` allows different mappings at different pipeline stages: data mapping,
after stat computation, and after scale application.

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class"))
    + geom_bar(aes(fill=stage(start="class", after_stat="count")))
    + scale_fill_cmap(cmap_name="Blues")
    + labs(x="Vehicle Class", y="Count", fill="Count", title="Bars Colored by Count")
)
```

## Legends and Guides

Every mapped aesthetic produces a guide (a legend or a colorbar)
automatically. Customize via `guides()`, `guide_legend()`,
`guide_colorbar()`, scale arguments, or `theme()`.

### Picking the guide type

Continuous color/fill scales default to a colorbar; discrete scales
default to a legend. Override with `guides()`:

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds.sample(2000, random_state=42), aes(x="carat", y="price", color="depth"))
    + geom_point(alpha=0.5, size=1)
    + scale_color_cmap(cmap_name="viridis")
    + guides(color=guide_legend(ncol=1))
    + labs(x="Carat", y="Price (USD)", title="Legend forced for continuous color")
)
```

Use `guide_colorbar()` to customize a colorbar (height, width, tick
density) and `guide_legend()` for discrete legends (columns, reverse
order, key size).

### Merging legends

When multiple aesthetics map to the **same variable** and use the
**same scale name**, plotnine merges them into a single legend. Force
merging by aligning the `name=` argument across scales:

```python
from plotnine import *
from plotnine.data import penguins

(
    ggplot(penguins.dropna(), aes(x="bill_length_mm", y="bill_depth_mm", color="species", shape="species"))
    + geom_point(size=2)
    + scale_color_brewer(type="qual", palette="Set2", name="Species")
    + scale_shape_discrete(name="Species")
    + labs(x="Bill Length (mm)", y="Bill Depth (mm)", title="Merged legend (color + shape)")
)
```

### Customizing breaks and labels

`breaks=`, `labels=`, and `name=` on any `scale_*` function control
what the guide displays:

- **`breaks`** — list of values where ticks / legend entries appear.
- **`labels`** — list or callable mapping breaks to display strings.
- **`name`** — guide title (shortcut for `labs(<aesthetic>=...)`).

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds.sample(2000, random_state=42), aes(x="carat", y="price", color="cut"))
    + geom_point(alpha=0.5, size=1)
    + scale_color_brewer(
        type="qual",
        palette="Set2",
        name="Cut Quality",
        breaks=["Fair", "Good", "Very Good", "Premium", "Ideal"],
        labels=["Fair", "Good", "V. Good", "Prem.", "Ideal"],
    )
    + labs(x="Carat", y="Price (USD)", title="Custom break labels")
)
```

### Positioning

Legend position is a theme element, not a guide argument:

```python
+ theme(legend_position="bottom")         # "left", "right", "top", "bottom", "none"
+ theme(legend_position=(0.85, 0.20))     # (x, y) inside panel, 0–1
```

See [themes-and-styling.md](themes-and-styling.md) for the full
`theme()` surface (legend title/text elements, key size, background).

### Hiding a guide

```python
+ guides(color="none")                    # suppress one aesthetic's guide
+ theme(legend_position="none")           # suppress all guides
```

## Common Pitfalls

- **Quotes around variable names in `aes()`**: plotnine requires strings:
  `aes(x="displ")`, not `aes(x=displ)`.

- **`scale_color` vs `scale_fill` mismatch**: `geom_bar` uses `fill`, not
  `color`. Using `scale_color_brewer` won't affect bar interiors — use
  `scale_fill_brewer`. See [color-and-accessibility.md](color-and-accessibility.md)
  for palette details.

- **`scale_x_continuous` on discrete data**: Applying a continuous scale to a
  discrete column raises an error. Use `scale_x_discrete` for categorical
  columns, or convert the column first.

- **Invalid `after_stat` variable**: The available computed variables depend on
  the stat. For `geom_histogram` (uses `stat_bin`): `count`, `density`,
  `ncount`, `ndensity`. Check the stat documentation for available variables.

## See Also

- `api/scale_<name>.md` — parameter reference and single-scale examples
  for each scale function
- [aesthetic-specification.md](aesthetic-specification.md) — literal
  value formats for colors, linetypes, shapes, fonts
- [color-and-accessibility.md](color-and-accessibility.md) —
  palette choice and colorblind-safe scales
- [themes-and-styling.md](themes-and-styling.md) — styling legend
  and guide elements
- [geoms.md](geoms.md) — which aesthetics each geom accepts

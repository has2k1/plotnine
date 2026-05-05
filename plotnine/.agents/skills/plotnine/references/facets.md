# Facets

Facets split data into panels by one or more variables, creating small multiples
that share the same axes and scales. plotnine provides `facet_wrap` for a single
variable and `facet_grid` for two-variable grids.

## facet_wrap

Wraps panels into a rectangular layout. Use when faceting by a single variable
with many levels.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `facets` | — | Variable name(s) to facet by (string or list) |
| `nrow` | `None` | Number of rows |
| `ncol` | `None` | Number of columns |
| `scales` | `"fixed"` | `"fixed"`, `"free"`, `"free_x"`, `"free_y"` |
| `labeller` | `"label_value"` | Labelling function for strip text |
| `dir` | `"h"` | `"h"` (horizontal) or `"v"` (vertical) fill direction |
| `drop` | `True` | Drop unused factor levels |
| `as_table` | `True` | Lay out panels like a table (top-left start) |
| `shrink` | `True` | Shrink scales to fit stat output |

### Single variable wrap

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + facet_wrap("class")
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Fuel Efficiency by Vehicle Class")
)
```

### Controlling rows and columns

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + facet_wrap("class", nrow=2)
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Classes in Two Rows")
)
```

### Vertical fill direction

Setting `dir="v"` fills panels column-by-column instead of row-by-row.

```python
from plotnine import *
from plotnine.data import penguins

(
    ggplot(penguins.dropna(), aes(x="bill_length_mm", y="bill_depth_mm"))
    + geom_point(alpha=0.5, size=1)
    + facet_wrap("species", dir="v")
    + labs(x="Bill Length (mm)", y="Bill Depth (mm)", title="Penguin Bills by Species")
)
```

## facet_grid

Creates a matrix of panels defined by row and column variables.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `rows` | `None` | Row variable(s) |
| `cols` | `None` | Column variable(s) |
| `margins` | `False` | Add margin panels (`True`, or list of variable names) |
| `scales` | `"fixed"` | `"fixed"`, `"free"`, `"free_x"`, `"free_y"` |
| `space` | `"fixed"` | `"fixed"`, `"free"`, `"free_x"`, `"free_y"` |
| `labeller` | `"label_value"` | Labelling function for strip text |
| `drop` | `True` | Drop unused factor levels |
| `as_table` | `True` | Lay out panels like a table |
| `shrink` | `True` | Shrink scales to fit stat output |

### Two-variable grid

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + facet_grid(rows="drv", cols="cyl")
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Drive Type vs Cylinders")
)
```

### Row-only facet grid

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + facet_grid(rows="drv")
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Faceted by Drive Type")
)
```

## Free vs Fixed Scales

By default, all panels share the same axis ranges (`scales="fixed"`). Use
`scales="free"`, `"free_x"`, or `"free_y"` to let panels have independent
ranges.

### Free y-axis scales

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + facet_wrap("class", scales="free_y")
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Free Y Scales by Class")
)
```

### Free scales in facet_grid with free space

When using `facet_grid`, the `space` parameter makes panel sizes proportional
to their data range. This is useful for comparing distributions across panels
with different ranges.

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds.sample(2000, random_state=42), aes(x="carat", y="price"))
    + geom_point(alpha=0.3, size=0.5)
    + facet_grid(rows="cut", scales="free_y", space="free_y")
    + labs(x="Carat", y="Price (USD)", title="Diamond Price by Cut (Proportional Space)")
)
```

## Labellers

Labellers control the text displayed in facet strip labels.

| Function | Description | Example output |
|----------|-------------|----------------|
| `label_value` | Value only (default) | `"4"` |
| `label_both` | Variable and value | `"cyl: 4"` |
| `label_context` | Variable only when ambiguous | context-dependent |
| `labeller()` | Per-variable control | varies |
| `as_labeller()` | Custom mapping or function | varies |

### label_both

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + facet_wrap("cyl", labeller="label_both")
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Labelled with Variable Name")
)
```

### Custom labeller per variable

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.5)
    + facet_grid(rows="drv", cols="cyl", labeller=labeller(drv="label_both", cyl="label_value"))
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Custom Labeller per Variable")
)
```

## Strip Customization

Facet strip labels can be styled via `theme()`. See
[themes-and-styling.md](themes-and-styling.md) for full theme reference.

### Styled strip labels

```python
from plotnine import *
from plotnine.data import penguins

(
    ggplot(penguins.dropna(), aes(x="bill_length_mm", y="body_mass_g"))
    + geom_point(alpha=0.5, size=1)
    + facet_wrap("species")
    + theme(
        strip_background=element_rect(fill="#2c3e50"),
        strip_text=element_text(color="white", weight="bold", size=10),
    )
    + labs(x="Bill Length (mm)", y="Body Mass (g)", title="Custom Strip Styling")
)
```

## Common Pitfalls

- **Forgetting `scales="free"`**: When panels have vastly different ranges,
  overlapping data becomes invisible. Use `scales="free"` or `"free_y"` /
  `"free_x"` so each panel fits its own range.

- **Passing non-string to `facet_wrap`**: The `facets` parameter expects a
  string or list of strings, not a bare column reference. Use
  `facet_wrap("class")`, not `facet_wrap(class)`.

- **Confusing `nrow`/`ncol` (wrap) with `rows`/`cols` (grid)**:
  `facet_wrap` uses `nrow` and `ncol` to control the layout dimensions.
  `facet_grid` uses `rows` and `cols` to specify which variables define the
  grid axes.

- **Too many panels**: Faceting by a high-cardinality variable produces too many
  small panels. Filter or bin the variable before faceting.

## See Also

- [geoms.md](geoms.md) — the geoms being faceted
- [coords-and-axes.md](coords-and-axes.md) — `scales="free"` interaction
  with coordinate systems
- [themes-and-styling.md](themes-and-styling.md) — styling strip labels
  (`strip_text`, `strip_background`)

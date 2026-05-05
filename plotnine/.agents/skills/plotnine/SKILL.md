---
name: plotnine
description: >
  Generate, refine and export data visualizations using plotnine. Use this skill
  when the user asks to create plots or charts with plotnine. Also use when
  customizing themes, applying colorblind-safe palettes, reshaping data for
  plotting with plotnine, or saving figures to PNG/PDF/SVG/JPEG.
---

# plotnine

> This skill targets plotnine 0.15+ with pandas 2.x.

## Behavioral Rules

1. **Runnability** — all generated code is executable as-is. Include imports,
   data loading, and the full ggplot expression. No pseudocode, no `...`
   elisions, no undefined variables.

2. **Idiomatic plotnine** — use `+` layering, `aes()`, `theme_*`, `labs()`,
   `scale_*`. **Never fall back to matplotlib.** If plotnine cannot achieve the
   result, propose the closest plotnine-idiomatic alternative and explain the
   limitation.

3. **Data completeness** — generated code must include all data needed to run:
   inline `pd.DataFrame()` construction, `plotnine.data` datasets, or clearly
   referenced from the user's existing context. Never reference undefined
   DataFrames.

4. **Minimal transformations** — prefer simple pandas ops (`groupby`, `agg`,
   `melt`) or polars equivalents. Prefer plotnine `stat_*`/`position_*` over
   manual aggregation when possible.

5. **Accessibility** — always provide descriptive axis labels via `labs()` and
   clear legend titles. When the user requests accessible colors, recommend
   colorblind-safe palettes (Set2, viridis, Okabe-Ito). Provide alt-text
   guidance when asked.

6. **Reproducibility** — use `random_state=42` for any plotnine method that
   accepts it (e.g., `DataFrame.sample()`). Seed synthetic data with
   `numpy.random.default_rng(42)`.

## When to Use What

Task: Create a basic plot (scatter, bar, line, histogram, boxplot)
Use: "Plotnine Essentials" below, then [references/geoms.md](references/geoms.md)

Task: Map variables to visual properties or customize scales
Use: [references/aesthetics-and-scales.md](references/aesthetics-and-scales.md)

Task: Customize appearance (fonts, backgrounds, gridlines, themes)
Use: [references/themes-and-styling.md](references/themes-and-styling.md)

Task: Choose accessible colors or palettes
Use: [references/color-and-accessibility.md](references/color-and-accessibility.md)

Task: Reshape or prepare data for a specific chart
Use: [references/data-preparation.md](references/data-preparation.md)

Task: Revise an existing plot (iterative refinement)
Use: [references/iterative-refinement.md](references/iterative-refinement.md)

Task: Create small multiples / faceted plots
Use: [references/facets.md](references/facets.md)

Task: Add titles, subtitles, annotations, labels
Use: [references/labels-and-annotations.md](references/labels-and-annotations.md)

Task: Add trend lines, smoothers, statistical summaries
Use: [references/statistical-layers.md](references/statistical-layers.md)

Task: Adjust axes, coordinates, transforms
Use: [references/coords-and-axes.md](references/coords-and-axes.md)

Task: Save / export a figure
Use: [references/saving-and-export.md](references/saving-and-export.md)

Task: Combine multiple plots side-by-side or stacked
Use: [references/composition.md](references/composition.md)

Task: Plot geographic / map data
Use: [references/maps.md](references/maps.md)

Task: Specify literal aesthetic values (colors, linetypes, shapes, fonts)
Use: [references/aesthetic-specification.md](references/aesthetic-specification.md)

Task: Look up a specific symbol's parameters, types, or defaults
Use: `references/api/<symbol>.md` (e.g. [references/api/geom_point.md](references/api/geom_point.md)).
     British-spelling aliases (`scale_colour_*`) and 2d-suffix aliases
     (`geom_bin2d`, `stat_bin2d`) redirect to the canonical spelling.

## Decision Trees

Natural-language routing for when a user's question doesn't map cleanly
onto the task table above. Every leaf points to a reference file.

### I need to show …

```
Show what?
├─ one variable's distribution         → references/geoms.md (histogram, density, boxplot)
├─ relationship between two variables  → references/geoms.md (point, smooth)
│                                        + references/statistical-layers.md for trend lines
├─ a categorical breakdown             → references/geoms.md (bar, col)
├─ change over time                    → references/geoms.md (line, area)
├─ geographic / spatial data           → references/maps.md
├─ group comparison                    → references/geoms.md (violin, boxplot)
│                                        + references/facets.md for small multiples
└─ counts / proportions / heatmap      → references/geoms.md (bar, tile)
```

### I need to customize …

```
Customize what?
├─ colors / palettes                   → references/color-and-accessibility.md
├─ fonts / backgrounds / gridlines     → references/themes-and-styling.md
├─ legends and guides                  → references/aesthetics-and-scales.md §Legends and Guides
├─ scales (breaks, labels, limits)     → references/aesthetics-and-scales.md
├─ axes / coordinates / transforms     → references/coords-and-axes.md
├─ titles / subtitles / annotations    → references/labels-and-annotations.md
└─ literal aesthetic values            → references/aesthetic-specification.md
   (e.g. a specific hex, dash pattern, font weight)
```

### I need to lay out multiple plots or panels …

```
Layout how?
├─ one plot split by a variable                    → references/facets.md
│  (facet_wrap / facet_grid)
└─ several independent plots side-by-side or stacked → references/composition.md
   (| and / operators)
```

### I need to prepare my data …

```
Data shape problem?
├─ reshape wide → long (or vice versa)  → references/data-preparation.md
├─ order categorical axes               → references/data-preparation.md
├─ aggregate before plotting            → references/data-preparation.md
│                                         or references/statistical-layers.md (stat_summary)
└─ drop / handle NAs                    → references/data-preparation.md
```

### I'm revising an existing plot

```
→ references/iterative-refinement.md
```

### I need to save / export

```
→ references/saving-and-export.md
```

## Plotnine Essentials

### Standard import

```python
from plotnine import *
from plotnine.data import mpg
import pandas as pd          # only when pandas ops are used
import numpy as np           # only when generating synthetic data
```

Alternative import for users who prefer no wildcard:

```python
import plotnine as p9
from plotnine.data import mpg

(
    p9.ggplot(mpg, p9.aes(x="displ", y="hwy"))
    + p9.geom_point()
    + p9.labs(x="Engine Displacement (L)", y="Highway MPG", title="Fuel Efficiency")
)
```

Alternative import for users who prefer explicit imports:

```python
from plotnine import ggplot, aes, geom_point, labs
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point()
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Fuel Efficiency")
)
```

### Minimal working plot

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point()
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Fuel Efficiency by Engine Size")
)
```

### Saving a plot

```python
from plotnine import *
from plotnine.data import penguins

p = (
    ggplot(penguins.dropna(), aes(x="species", fill="species"))
    + geom_bar()
    + labs(x="Species", y="Count", title="Penguin Species Counts", fill="Species")
)

p.save("penguins.png", width=6, height=4, dpi=300)
```

Supported formats: PNG, PDF, SVG, and any format supported by matplotlib's
`savefig`.

## Difficulty Guidance

| Difficulty | Examples | Strategy |
|-----------|---------|----------|
| Easy | Scatter, bar of counts, histogram, boxplot, line chart | Single canonical pattern from Essentials above |
| Medium | Grouped bar, faceted scatter, violin + jitter, custom theme, color palette | Combine 2-3 layers; consult reference files |
| Hard | Multi-dataset layers, heatmap with annotations, composition, lollipop chart | Propose closest plotnine approach; explain limitations if any |

### Hard case guidance

If plotnine genuinely cannot produce the requested visualization (e.g., true
dual y-axes, interactive tooltips), explain the limitation and propose the
closest achievable result using only plotnine. Never fall back to matplotlib.

## Resources

### Reference Files

- [references/geoms.md](references/geoms.md) — Geom catalog with canonical patterns and examples
- [references/aesthetics-and-scales.md](references/aesthetics-and-scales.md) — Aesthetic mappings, scale functions, computed aesthetics
- [references/themes-and-styling.md](references/themes-and-styling.md) — Built-in themes, theme() customization, reusable themes
- [references/color-and-accessibility.md](references/color-and-accessibility.md) — Palettes, colorblind safety, alt-text guidance
- [references/data-preparation.md](references/data-preparation.md) — Tidy data, reshaping, aggregation, categorical ordering
- [references/iterative-refinement.md](references/iterative-refinement.md) — Edit protocol, diff format, revision patterns
- [references/facets.md](references/facets.md) — facet_wrap, facet_grid, labellers, strip styling
- [references/labels-and-annotations.md](references/labels-and-annotations.md) — labs(), annotate(), geom_text, geom_label, reference lines
- [references/statistical-layers.md](references/statistical-layers.md) — geom_smooth, stat_summary, stat_ecdf, position adjustments
- [references/coords-and-axes.md](references/coords-and-axes.md) — coord_cartesian, coord_flip, coord_fixed, coord_trans
- [references/saving-and-export.md](references/saving-and-export.md) — ggplot.save(), formats, sizes, in-memory saving
- [references/composition.md](references/composition.md) — Plot composition with |, /, +, &, *, plot_layout, plot_annotation
- [references/maps.md](references/maps.md) — geom_map, GeoPandas, choropleths, coord_fixed, theme_void
- [references/aesthetic-specification.md](references/aesthetic-specification.md) — Literal color/linetype/shape/size/text value formats
- `references/api/<symbol>.md` — Parameter reference for every public geom, stat, scale, and coord

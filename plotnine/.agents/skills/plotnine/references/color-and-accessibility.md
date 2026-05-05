# Color and Accessibility

Guidance for choosing color palettes that are readable, distinguishable, and
accessible to colorblind viewers.

## Default Behavior

plotnine applies `scale_color_hue()` for discrete variables (evenly spaced hues)
and `scale_color_continuous()` for continuous variables. These defaults are
reasonable for exploration but may not be ideal for publication or accessibility.

Only override the default when the user asks for a specific palette or requests
accessible/colorblind-safe colors.

## Colorblind-Safe Palettes

### Brewer Set2 (qualitative, up to 8 categories)

Best for categorical data with 3-8 groups.

```python
from plotnine import *
from plotnine.data import penguins

(
    ggplot(penguins.dropna(), aes(x="bill_length_mm", y="bill_depth_mm", color="species"))
    + geom_point()
    + scale_color_brewer(type="qual", palette="Set2")
    + labs(x="Bill Length (mm)", y="Bill Depth (mm)", title="Penguins (Colorblind-Safe)", color="Species")
)
```

### Viridis family (continuous or ordered)

Perceptually uniform and colorblind-safe. Works for continuous and ordinal data.
Variants: `"viridis"`, `"magma"`, `"plasma"`, `"inferno"`, `"cividis"`.

```python
from plotnine import *
from plotnine.data import midwest

(
    ggplot(midwest, aes(x="percollege", y="percbelowpoverty", color="popdensity"))
    + geom_point(alpha=0.5, size=1.5)
    + scale_color_cmap(cmap_name="viridis")
    + labs(x="% College Educated", y="% Below Poverty", title="Midwest Counties", color="Pop. Density")
)
```

For discrete data with many ordered levels, use `scale_color_cmap_d`:

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds.sample(2000, random_state=42), aes(x="carat", y="price", color="cut"))
    + geom_point(alpha=0.5, size=1)
    + scale_color_cmap_d(cmap_name="viridis")
    + labs(x="Carat", y="Price (USD)", title="Diamonds by Cut (Viridis Discrete)", color="Cut")
)
```

### Okabe-Ito palette (manual, up to 8 categories)

A widely recommended colorblind-safe palette by Okabe and Ito (2008).

```python
from plotnine import *
from plotnine.data import penguins

OKABE_ITO = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"]

(
    ggplot(penguins.dropna(), aes(x="bill_length_mm", y="bill_depth_mm", color="species"))
    + geom_point()
    + scale_color_manual(values=OKABE_ITO[:3])
    + labs(x="Bill Length (mm)", y="Bill Depth (mm)", title="Penguins (Okabe-Ito)", color="Species")
)
```

## Choosing Between Palettes

| Data type | Categories | Recommended palette |
|-----------|-----------|-------------------|
| Categorical (unordered) | 2-3 | `scale_color_brewer(type="qual", palette="Set2")` or Okabe-Ito |
| Categorical (unordered) | 4-8 | `scale_color_brewer(type="qual", palette="Set2")` or Okabe-Ito |
| Categorical (unordered) | >8 | Reduce categories or use facets instead |
| Ordinal (ordered) | any | `scale_color_cmap_d(cmap_name="viridis")` |
| Continuous (sequential) | — | `scale_color_cmap(cmap_name="viridis")` |
| Continuous (diverging) | — | `scale_color_gradient2(low="blue", mid="white", high="red")` |

## Double Encoding: Color + Shape

When presenting to mixed audiences or printing in grayscale, map the same
variable to both color and shape. This ensures the groups remain distinguishable
even without color.

```python
from plotnine import *
from plotnine.data import penguins

(
    ggplot(penguins.dropna(), aes(x="bill_length_mm", y="bill_depth_mm", color="species", shape="species"))
    + geom_point(size=2)
    + scale_color_brewer(type="qual", palette="Set2")
    + labs(x="Bill Length (mm)", y="Bill Depth (mm)", title="Double Encoding: Color + Shape", color="Species", shape="Species")
)
```

## Contrast and Readability

### Fill with dark borders

When using `fill` on bars or boxes, add a thin dark border for contrast.

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class", fill="factor(cyl)"))
    + geom_bar(color="black", size=0.3)
    + scale_fill_brewer(type="qual", palette="Set2")
    + labs(x="Vehicle Class", y="Count", title="Bars with Borders", fill="Cylinders")
)
```

### Light text on dark themes

When using `theme_dark()`, ensure labels and titles have sufficient contrast.

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds.sample(1000, random_state=42), aes(x="carat", y="price", color="cut"))
    + geom_point(alpha=0.6, size=1)
    + theme_dark()
    + theme(
        plot_title=element_text(color="white"),
        axis_title=element_text(color="white"),
    )
    + labs(x="Carat", y="Price (USD)", title="Dark Theme with Light Text", color="Cut")
)
```

## Alt-Text Guidance

When generating plots for documents or web pages, provide alt-text that
describes the chart type, the data shown, and the key pattern. Use this
template:

> **"[Chart type] showing [data]. [Key pattern]. Data: [source]."**

Examples:

- "Scatter plot showing bill length vs bill depth for three penguin species.
  Gentoo penguins have longer but shallower bills. Data: Palmer Penguins."
- "Bar chart showing count of cars by vehicle class. SUVs are the most common
  class. Data: EPA fuel economy (mpg)."

## Fill Palettes

Fill aesthetics use the `scale_fill_*` family, which mirrors `scale_color_*`.

```python
from plotnine import *
from plotnine.data import penguins

(
    ggplot(penguins.dropna(), aes(x="species", fill="species"))
    + geom_bar()
    + scale_fill_brewer(type="qual", palette="Set2")
    + labs(x="Species", y="Count", title="Penguin Counts by Species", fill="Species")
)
```

For continuous fill (e.g., heatmaps):

```python
from plotnine import *
from plotnine.data import faithfuld

(
    ggplot(faithfuld, aes(x="eruptions", y="waiting", fill="density"))
    + geom_tile()
    + scale_fill_cmap(cmap_name="viridis")
    + labs(x="Eruption Duration (min)", y="Waiting Time (min)", title="Old Faithful Heatmap", fill="Density")
)
```

## Common Pitfalls

- **`scale_color_*` for fill aesthetic**: Using `scale_color_brewer` when the
  geom uses `fill` (bars, boxes, areas) has no effect. Use `scale_fill_brewer`.

- **Too many categories (>8)**: Most qualitative palettes degrade above 8
  categories. Consider grouping rare categories into "Other" or using facets.

- **Rainbow/jet colormaps**: Avoid `"rainbow"` and `"jet"` — they are not
  perceptually uniform and are problematic for colorblind viewers. Use
  `"viridis"` or other perceptually uniform alternatives.

- **`scale_color_cmap` vs `scale_color_cmap_d`**: Use `scale_color_cmap` for
  continuous data and `scale_color_cmap_d` for discrete data. Using the wrong
  one raises an error.

- **Forgetting `values=` in `scale_color_manual`**: The `values` parameter
  is required. Pass a list of hex strings or named colors matching the number
  of levels.

## See Also

- [aesthetics-and-scales.md](aesthetics-and-scales.md) — applying
  palettes through `scale_color_*` / `scale_fill_*`
- [themes-and-styling.md](themes-and-styling.md) — picking background
  colors that work with foreground palettes

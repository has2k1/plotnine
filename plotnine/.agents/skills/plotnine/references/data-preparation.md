# Data Preparation

plotnine expects tidy data: one row per observation, one column per variable.
This file covers common pandas (and polars) transformations to prepare data for
plotting.

## Tidy Data for plotnine

A tidy DataFrame maps directly to `aes()`: each column becomes a potential
aesthetic, each row becomes a potential geometric mark.

| Tidy | Not tidy |
|------|----------|
| Columns: `year`, `variable`, `value` | Columns: `year`, `gdp`, `population`, `inflation` |
| One measurement per row | Multiple measurements per row (wide format) |

## Wide to Long

### pandas `pd.melt()`

Wide data has multiple measurement columns. Melt reshapes them into a single
`variable`/`value` pair.

```python
from plotnine import *
import pandas as pd

df_wide = pd.DataFrame({
    "month": ["Jan", "Feb", "Mar"],
    "product_a": [100, 120, 90],
    "product_b": [80, 95, 110],
})

df_long = pd.melt(df_wide, id_vars="month", var_name="product", value_name="sales")

(
    ggplot(df_long, aes(x="month", y="sales", fill="product"))
    + geom_col(position="dodge")
    + labs(x="Month", y="Sales", title="Monthly Sales by Product", fill="Product")
)
```

### polars `df.unpivot()`

The polars equivalent of `pd.melt()`. Note: polars DataFrames must be converted
before passing to plotnine (plotnine requires pandas).

```python
from plotnine import *
import polars as pl

df_wide = pl.DataFrame({
    "month": ["Jan", "Feb", "Mar"],
    "product_a": [100, 120, 90],
    "product_b": [80, 95, 110],
})

df_long = (
    df_wide
    .unpivot(index="month", variable_name="product", value_name="sales")
    .to_pandas()
)

(
    ggplot(df_long, aes(x="month", y="sales", fill="product"))
    + geom_col(position="dodge")
    + labs(x="Month", y="Sales", title="Monthly Sales by Product (Polars)", fill="Product")
)
```

## Aggregation

### groupby().agg()

Pre-aggregate when you need summary values that plotnine stats don't compute
directly.

```python
from plotnine import *
from plotnine.data import msleep
import pandas as pd

sleep_by_vore = (
    msleep
    .dropna(subset=["vore"])
    .groupby("vore", as_index=False)
    .agg(mean_sleep=("sleep_total", "mean"))
)

(
    ggplot(sleep_by_vore, aes(x="vore", y="mean_sleep"))
    + geom_col()
    + labs(x="Diet Type", y="Mean Total Sleep (hrs)", title="Average Sleep by Diet")
)
```

When possible, prefer `stat_summary()` over manual aggregation — it keeps the
full data available for other geom layers. See the stats vs pre-aggregation
section below.

## Computed Columns

Derived columns for new aesthetics should be computed before plotting.

```python
from plotnine import *
from plotnine.data import mpg
import pandas as pd

mpg2 = mpg.assign(efficiency_ratio=mpg["hwy"] / mpg["cty"])

(
    ggplot(mpg2, aes(x="displ", y="efficiency_ratio"))
    + geom_point(alpha=0.5)
    + labs(x="Engine Displacement (L)", y="Highway / City MPG Ratio", title="Efficiency Ratio by Engine Size")
)
```

## Categorical Ordering

### pandas `pd.Categorical`

By default, plotnine plots categorical columns in alphabetical order. To
control order, convert to an ordered categorical.

```python
from plotnine import *
from plotnine.data import mpg
import pandas as pd

class_order = (
    mpg.groupby("class")["hwy"]
    .median()
    .sort_values()
    .index
    .tolist()
)

mpg2 = mpg.assign(
    class_ordered=pd.Categorical(mpg["class"], categories=class_order, ordered=True)
)

(
    ggplot(mpg2, aes(x="class_ordered", y="hwy"))
    + geom_boxplot()
    + labs(x="Vehicle Class (by median MPG)", y="Highway MPG", title="Boxplots Ordered by Median")
)
```

### polars limitation

plotnine converts polars to pandas internally using `.to_pandas()`.
polars supports `Enum` types with fixed orderings and these correspond to ordered categories
in pandas. The regular polars categorical shares categories with all other polars categoricals and
does not map well to pandas unordered pandas categorical.

## Date/Time Preparation

Ensure date columns are parsed as datetime before plotting. Pair with
`scale_x_datetime()` for tick control.

```python
from plotnine import *
from plotnine.data import economics_long
import pandas as pd

subset = economics_long[economics_long["variable"] == "unemploy"].copy()

(
    ggplot(subset, aes(x="date", y="value"))
    + geom_line()
    + scale_x_datetime(date_breaks="10 years", date_labels="%Y")
    + labs(x="Year", y="Unemployed (thousands)", title="Unemployment Over Time")
)
```

For columns that are strings, convert first:

```python
import pandas as pd
from plotnine import *

df = pd.DataFrame({"date_str": ["2020-01-01", "2020-06-01", "2021-01-01"], "y": [10, 20, 15]})
df["date"] = pd.to_datetime(df["date_str"])

(
    ggplot(df, aes(x="date", y="y"))
    + geom_line()
    + labs(x="Date", y="Value", title="Values Over Time")
)
```

## Stats vs Pre-Aggregation

plotnine's built-in stats can often replace manual aggregation. Prefer stats
when the full data should remain available for layering.

| Task | Use stat | Use pandas/polars |
|------|---------|-------------------|
| Count per category | `geom_bar()` (uses `stat_count`) | — |
| Mean per group | `stat_summary(fun_y=np.mean)` | `groupby().agg()` when you need the aggregated frame elsewhere |
| Histogram bins | `geom_histogram()` (uses `stat_bin`) | — |
| Density estimate | `geom_density()` (uses `stat_density`) | — |
| Trend line | `geom_smooth()` (uses `stat_smooth`) | — |
| ECDF | `stat_ecdf()` | — |
| Custom summary | — | `groupby().agg()` with custom functions |
| Multi-dataset layers | — | Separate DataFrames passed to each geom |

### stat_summary example

```python
from plotnine import *
from plotnine.data import mpg
import numpy as np

(
    ggplot(mpg, aes(x="class", y="hwy"))
    + geom_jitter(width=0.2, alpha=0.3)
    + stat_summary(fun_y=np.mean, geom="point", color="red", size=3)
    + labs(x="Vehicle Class", y="Highway MPG", title="Individual Points with Mean Overlay")
)
```

## Common Pitfalls

- **Wide data to plotnine**: Passing wide DataFrames and trying to map multiple
  columns to the same axis does not work. Use `pd.melt()` or
  `polars.unpivot()` to reshape to long format first.

- **Forgetting `dropna()`**: Datasets like `penguins` contain NA values.
  plotnine drops rows with NA in mapped aesthetics and issues a warning, but NAs in
  grouping columns can produce unexpected categories. Filter with `.dropna()`
  before plotting. See [aesthetics-and-scales.md](aesthetics-and-scales.md) for
  mapping details.

- **Unsorted string categories**: String columns plot in alphabetical order by
  default. Use `pd.Categorical` with explicit `categories` to control order.

- **Unnecessary manual aggregation**: Don't compute group means with pandas
  just to plot them — use `stat_summary()` or `geom_bar()` instead. Manual
  aggregation is only needed when the stat layer doesn't provide the right
  computation or you need the aggregated frame for other purposes.

- **`ordered=True` on `pd.Categorical` doesn't set plot order**: plotnine
  uses the `categories=` argument to determine x-axis / legend order,
  regardless of whether the Categorical is marked `ordered=True`.
  `ordered=True` affects pandas comparison operators (`<`, `>`), not
  plot ordering. Set order via `pd.Categorical(col, categories=[...])`.

- **`geom_line` crosses groups without `group=`**: If your x-axis has
  repeat values across multiple series and no aesthetic distinguishes
  them, `geom_line` draws a single zigzagging line through all points.
  Set `aes(group="series_col")`, or map `color=` / `linetype=` to the
  series column — those set `group` implicitly.

- **Datetime columns need `datetime64`, not strings**: Plotting a
  column of date strings treats them as discrete categories in
  alphabetical order. Convert first with `pd.to_datetime(df["date"])`.
  If you mix timezone-aware and naive datetimes in the same column,
  normalize to one form before plotting.

## See Also

- [geoms.md](geoms.md) — which geoms expect long vs wide input
- [statistical-layers.md](statistical-layers.md) — prefer `stat_summary`
  to manual pandas aggregation when possible

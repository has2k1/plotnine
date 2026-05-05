# Statistical Layers

Statistical layers (`stat_*`) compute summaries, models, and
transformations of the data, paired with a default geom. Per-stat
parameter surface and single-stat examples live at
`api/stat_<name>.md`.

This file covers **position adjustments**, which control how
overlapping geoms align — a topic that cuts across stats and geoms
and doesn't map to a single symbol.

## Reading Order

| Task                                    | Read in order                                                  |
|-----------------------------------------|----------------------------------------------------------------|
| Pick a stat                             | `api/stat_<name>.md`                                           |
| Add a smoother / fit                    | `api/geom_smooth.md` → `api/stat_smooth.md` for fit parameters |
| Summarize y at each x                   | `api/stat_summary.md`                                          |
| Arrange overlapping bars / points       | Position Adjustments below                                     |

## Position Adjustments

Position adjustments control how overlapping geoms are arranged.

| Position                         | Description                                | Common with                                    |
|----------------------------------|--------------------------------------------|------------------------------------------------|
| `position_dodge(width)`          | Side-by-side within groups                 | `geom_bar`, `geom_col`, `geom_boxplot`         |
| `position_dodge2(width)`         | Side-by-side, works with variable widths   | `geom_boxplot`                                 |
| `position_stack()`               | Stack on top of each other                 | `geom_bar`, `geom_area`                        |
| `position_fill()`                | Stack normalized to 100%                   | `geom_bar`, `geom_area`                        |
| `position_jitter(width, height)` | Random offset                              | `geom_point`                                   |
| `position_jitterdodge()`         | Jitter within dodged groups                | `geom_point` with grouped bars                 |

### Dodged bars with explicit width

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class", fill="factor(drv)"))
    + geom_bar(position=position_dodge(width=0.8), width=0.7)
    + labs(x="Vehicle Class", y="Count", fill="Drive", title="Dodged Bar Chart")
)
```

### Stacked bars

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds, aes(x="cut", fill="clarity"))
    + geom_bar(position="stack")
    + labs(x="Cut", y="Count", fill="Clarity", title="Stacked Bar Chart")
)
```

### Proportional (fill) bars

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds, aes(x="cut", fill="clarity"))
    + geom_bar(position="fill")
    + labs(x="Cut", y="Proportion", fill="Clarity", title="Proportional Bar Chart")
)
```

### Jittered points with dodge

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class", y="hwy", color="factor(drv)"))
    + geom_jitter(position=position_jitterdodge(jitter_width=0.15, dodge_width=0.8), alpha=0.6)
    + labs(x="Vehicle Class", y="Highway MPG", color="Drive", title="Jittered Points by Class and Drive")
)
```

## Common Pitfalls

- **`method="lm"` requires statsmodels**: `geom_smooth(method="lm")` uses
  statsmodels internally. If statsmodels is not installed, plotnine raises an
  error. Install it with `uv add statsmodels`.

- **`position_fill` normalizes to 1, not stacking**: `position_fill` rescales
  bar heights so each x position sums to 1.0. The y-axis shows proportions,
  not counts. Use `position_stack` for raw counts.

- **`fun_data` vs `fun_y`**: `fun_data` returns a DataFrame with y, ymin,
  ymax columns (used for range geoms like pointrange, errorbar). `fun_y` only
  returns the central value. Using `fun_y` with a pointrange geom produces no
  range bars.

- **Default `fun_data="mean_cl_boot"` is slow**: Bootstrap CI computes many
  resamples. For large datasets, use `fun_data="mean_se"` for faster results,
  or provide `fun_y`/`fun_ymin`/`fun_ymax` with numpy functions.

- **Forgetting `width` in `position_dodge`**: Without an explicit width, dodged
  elements may not align properly with bar widths. Match `position_dodge(width=)`
  to `geom_bar(width=)`.

## See Also

- `api/stat_<name>.md` — parameter reference and single-stat examples
- [geoms.md](geoms.md) — the geoms these stats produce
- [aesthetics-and-scales.md](aesthetics-and-scales.md) — `after_stat()`
  mappings for stat-computed variables
- [data-preparation.md](data-preparation.md) — when to precompute vs
  use a stat layer

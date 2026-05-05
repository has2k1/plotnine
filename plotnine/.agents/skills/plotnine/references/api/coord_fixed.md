# coord_fixed

Cartesian coordinates with fixed relationship between x and y scales

## Signature

`coord_fixed(ratio=1, xlim=None, ylim=None, expand=True)`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `ratio` | float | `1` | Desired aspect_ratio (:math:y/x) of the panel(s). |
| `xlim` | tuple[float, float] | `None` | Limits for x axis. If None, then they are automatically computed. |
| `ylim` | tuple[float, float] | `None` | Limits for y axis. If None, then they are automatically computed. |
| `expand` | bool | `True` | If True, expand the coordinate axes by some factor. If False, use the limits from the data. |

## Examples

Forces a fixed aspect ratio between x and y axes. `coord_equal` is
an alias. Essential for geographic plots (see
[maps.md](../maps.md)) and for any 1:1 comparison.

### Equal aspect ratio with 1:1 line

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="cty", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_abline(slope=1, intercept=0, linetype="dashed", color="grey")
    + coord_fixed(ratio=1)
    + labs(x="City MPG", y="Highway MPG", title="City vs Highway (Equal Scale)")
)
```

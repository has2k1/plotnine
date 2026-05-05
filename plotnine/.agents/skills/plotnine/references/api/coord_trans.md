# coord_trans

Transformed cartesian coordinate system

## Signature

`coord_trans(x="identity", y="identity", xlim=None, ylim=None, expand=True)`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `x` | str \| trans | `"identity"` | Name of transform or trans class to transform the x axis |
| `y` | str \| trans | `"identity"` | Name of transform or trans class to transform the y axis |
| `xlim` | tuple[float, float] | `None` | Limits for x axis. If None, then they are automatically computed. |
| `ylim` | tuple[float, float] | `None` | Limits for y axis. If None, then they are automatically computed. |
| `expand` | bool | `True` | If True, expand the coordinate axes by some factor. If False, use the limits from the data. |

## Examples

Applies a coordinate-space transformation without changing the
underlying scale. The data stays on the original scale (so axis
ticks reflect original units); only the visual spacing is
transformed. Contrast with `scale_*_log10`, which transforms the
scale itself.

### Log-transformed coordinates

```python
from plotnine import *
from plotnine.data import diamonds

(
    ggplot(diamonds.sample(2000, random_state=42), aes(x="carat", y="price"))
    + geom_point(alpha=0.3, size=0.5)
    + coord_trans(x="log10", y="log10")
    + labs(x="Carat", y="Price (USD)", title="Log-Log Coordinate Transform")
)
```

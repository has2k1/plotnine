# geom_smooth

A smoothed conditional mean

## Signature

`geom_smooth( mapping=None, data=None, *, stat="smooth", position="identity", na_rm=False, inherit_aes=True, show_legend=None, raster=False, legend_fill_ratio=0.5, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping. |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `stat` | str \| stat | `"smooth"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"identity"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `inherit_aes` | bool | `True` | If False, overrides the default aesthetics. |
| `show_legend` | bool \| dict | `None` | Whether this layer should be included in the legends. None the default, includes any aesthetics that are mapped. If a bool, False never includes and True always includes. A dict can be used to exclude specific aesthetis of the layer from showing in the legend. e.g show_legend={'color': False}, any other aesthetic are included by default. |
| `raster` | bool | `False` | If True, draw onto this layer a raster (bitmap) object even ifthe final image is in vector format. |
| `legend_fill_ratio` | float | `0.5` | How much (vertically) of the legend box should be filled by the color that indicates the confidence intervals. Should be in the range [0, 1]. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the stat. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y |  |
| alpha | 0.4 |
| color | 'black' |
| fill | '#999999' |
| group |  |
| linetype | 'solid' |
| size | 1 |
| ymax | None |
| ymin | None |

## Examples

When `method="auto"` (the default), plotnine uses loess for fewer
than 1000 observations and GLM above that. Loess smoothing requires
the `scikit-misc` package. See [stat_smooth.md](stat_smooth.md) for
the full set of fit-related parameters.

### Linear fit

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="lm")
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Linear Fit")
)
```

### Loess smoother with custom span

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="loess", span=0.5, color="darkred")
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Loess Smoother (span=0.5)")
)
```

### Grouped smoothers

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy", color="factor(drv)"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="lm", se=False)
    + labs(x="Engine Displacement (L)", y="Highway MPG", color="Drive", title="Linear Fit by Drive Type")
)
```

### Full-range prediction

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="displ", y="hwy"))
    + geom_point(alpha=0.4)
    + geom_smooth(method="lm", fullrange=True)
    + labs(x="Engine Displacement (L)", y="Highway MPG", title="Full-Range Linear Fit")
)
```

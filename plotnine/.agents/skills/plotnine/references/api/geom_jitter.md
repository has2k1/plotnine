# geom_jitter

Scatter plot with points jittered to reduce overplotting

## Signature

`geom_jitter( mapping=None, data=None, *, stat="identity", position="jitter", na_rm=False, inherit_aes=True, show_legend=None, raster=False, width=None, height=None, random_state=None, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping. |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `stat` | str \| stat | `"identity"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"jitter"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `inherit_aes` | bool | `True` | If False, overrides the default aesthetics. |
| `show_legend` | bool \| dict | `None` | Whether this layer should be included in the legends. None the default, includes any aesthetics that are mapped. If a bool, False never includes and True always includes. A dict can be used to exclude specific aesthetis of the layer from showing in the legend. e.g show_legend={'color': False}, any other aesthetic are included by default. |
| `raster` | bool | `False` | If True, draw onto this layer a raster (bitmap) object even ifthe final image is in vector format. |
| `width` | float | `None` | Proportion to jitter in horizontal direction. The default value is that from position_jitter |
| `height` | float | `None` | Proportion to jitter in vertical direction. The default value is that from position_jitter. |
| `random_state` | int \| RandomState | `None` | Seed or Random number generator to use. If None, then numpy global generator numpy.random is used. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the stat. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y |  |
| alpha | 1 |
| color | 'black' |
| fill | None |
| group |  |
| shape | 'o' |
| size | 1.5 |
| stroke | 0.5 |

## Examples

### Jittered points

`geom_jitter` adds random noise to avoid over-plotting on discrete axes.

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class", y="hwy"))
    + geom_jitter(width=0.2, height=0, alpha=0.6, random_state=42)
    + labs(x="Vehicle Class", y="Highway MPG", title="Highway MPG by Vehicle Class")
)
```

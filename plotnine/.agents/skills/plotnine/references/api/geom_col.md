# geom_col

Bar plot with base on the x-axis

## Signature

`geom_col( mapping=None, data=None, *, stat="identity", position="stack", na_rm=False, inherit_aes=True, show_legend=None, raster=False, just=0.5, width=None, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping. |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `stat` | str \| stat | `"identity"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"stack"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `inherit_aes` | bool | `True` | If False, overrides the default aesthetics. |
| `show_legend` | bool \| dict | `None` | Whether this layer should be included in the legends. None the default, includes any aesthetics that are mapped. If a bool, False never includes and True always includes. A dict can be used to exclude specific aesthetis of the layer from showing in the legend. e.g show_legend={'color': False}, any other aesthetic are included by default. |
| `raster` | bool | `False` | If True, draw onto this layer a raster (bitmap) object even ifthe final image is in vector format. |
| `just` | float | `0.5` | How to align the column with respect to the axis breaks. The default 0.5 aligns the center of the column with the break. 0 aligns the left of the of the column with the break and 1 aligns the right of the column with the break. |
| `width` | float | `None` | Bar width. If None, the width is set to 90% of the resolution of the data. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the stat. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y |  |
| alpha | 1 |
| color | None |
| fill | '#595959' |
| group |  |
| linetype | 'solid' |
| size | 0.5 |

## Examples

### Pre-computed column heights

`geom_col` plots pre-computed y values. Requires both x and y aesthetics.

```python
from plotnine import *
from plotnine.data import mpg

avg_hwy = mpg.groupby("class", as_index=False).agg(mean_hwy=("hwy", "mean"))

(
    ggplot(avg_hwy, aes(x="class", y="mean_hwy"))
    + geom_col()
    + labs(x="Vehicle Class", y="Mean Highway MPG", title="Average Highway MPG by Class")
)
```

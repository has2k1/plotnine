# geom_boxplot

Box and whiskers plot

## Signature

`geom_boxplot( mapping=None, data=None, *, stat="boxplot", position="dodge2", na_rm=False, inherit_aes=True, show_legend=None, raster=False, width=None, outlier_alpha=1, outlier_color=None, outlier_shape="o", outlier_size=1.5, outlier_stroke=0.5, notch=False, varwidth=False, notchwidth=0.5, fatten=2, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping. |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `stat` | str \| stat | `"boxplot"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"dodge2"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `inherit_aes` | bool | `True` | If False, overrides the default aesthetics. |
| `show_legend` | bool \| dict | `None` | Whether this layer should be included in the legends. None the default, includes any aesthetics that are mapped. If a bool, False never includes and True always includes. A dict can be used to exclude specific aesthetis of the layer from showing in the legend. e.g show_legend={'color': False}, any other aesthetic are included by default. |
| `raster` | bool | `False` | If True, draw onto this layer a raster (bitmap) object even ifthe final image is in vector format. |
| `width` | float | `None` | Box width. If None, the width is set to 90% of the resolution of the data. Note that if the stat has a width parameter, that takes precedence over this one. |
| `outlier_alpha` | float | `1` | Transparency of the outlier points. |
| `outlier_color` | str \| tuple | `None` | Color of the outlier points. |
| `outlier_shape` | str | `"o"` | Shape of the outlier points. An empty string hides the outliers. |
| `outlier_size` | float | `1.5` | Size of the outlier points. |
| `outlier_stroke` | float | `0.5` | Stroke-size of the outlier points. |
| `notch` | bool | `False` | Whether the boxes should have a notch. |
| `varwidth` | bool | `False` | If True, boxes are drawn with widths proportional to the square-roots of the number of observations in the groups. |
| `notchwidth` | float | `0.5` | Width of notch relative to the body width. |
| `fatten` | float | `2` | A multiplicative factor used to increase the size of the middle bar across the box. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the stat. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| lower |  |
| middle |  |
| upper |  |
| x |  |
| ymax |  |
| ymin |  |
| alpha | 1 |
| color | '#333333' |
| fill | 'white' |
| group |  |
| linetype | 'solid' |
| shape | 'o' |
| size | 0.5 |
| weight | 1 |

## Examples

### Box plot by category

```python
from plotnine import *
from plotnine.data import mpg

(
    ggplot(mpg, aes(x="class", y="hwy"))
    + geom_boxplot()
    + labs(x="Vehicle Class", y="Highway MPG", title="Highway MPG Distribution by Class")
)
```

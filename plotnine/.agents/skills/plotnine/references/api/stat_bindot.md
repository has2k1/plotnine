# stat_bindot

Binning for a dot plot

## Signature

`stat_bindot( mapping=None, data=None, *, geom="dotplot", position="identity", na_rm=False, bins=None, binwidth=None, origin=None, width=0.9, binaxis="x", method="dotdensity", binpositions="bygroup", drop=False, right=True, breaks=None, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping.  Options for computed aesthetics |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `geom` | str \| geom | `"dotplot"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"identity"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `bins` | int | `None` | Number of bins. Overridden by binwidth. If None, a number is computed using the freedman-diaconis method. |
| `binwidth` | float | `None` | When method="dotdensity", this specifies the maximum binwidth. When method="histodot", this specifies the binwidth. This supersedes the bins. |
| `origin` | float | `None` | When method="histodot", origin of the first bin. |
| `width` | float | `0.9` | When binaxis="y", the spacing of the dotstacks for dodging. |
| `binaxis` | Literal["x", "y"] | `"x"` | Axis to bin along. |
| `method` | Literal["dotdensity", "histodot"] | `"dotdensity"` | Whether to do dot-density binning or fixed widths binning. |
| `binpositions` | Literal["all", "bygroup"] | `"bygroup"` | Position of the bins when method="dotdensity". The value - bygroup - positions of the bins for each group are determined separately. - all - positions of the bins are determined with all data taken together. This aligns the dots stacks across multiple groups. |
| `drop` | bool | `False` | If True, remove all bins with zero counts. |
| `right` | bool | `True` | When method="histodot", True means include right edge of the bins and if False the left edge is included. |
| `breaks` | FloatArray | `None` | Bin boundaries for method="histodot". This supersedes the binwidth and bins. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the geom. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y | after_stat('count') |

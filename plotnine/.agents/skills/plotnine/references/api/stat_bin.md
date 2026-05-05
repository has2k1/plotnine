# stat_bin

Count cases in each interval

## Signature

`stat_bin( mapping=None, data=None, *, geom="histogram", position="stack", na_rm=False, binwidth=None, bins=None, breaks=None, center=None, boundary=None, closed="right", pad=False, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping.  Options for computed aesthetics |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `geom` | str \| geom | `"histogram"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"stack"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `binwidth` | float | `None` | The width of the bins. The default is to use bins bins that cover the range of the data. You should always override this value, exploring multiple widths to find the best to illustrate the stories in your data. |
| `bins` | int | `None` | Number of bins. Overridden by binwidth. If None, a number is computed using the freedman-diaconis method. |
| `breaks` | array_like | `None` | Bin boundaries. This supersedes the binwidth, bins, center and boundary. |
| `center` | float | `None` | The center of one of the bins. Note that if center is above or below the range of the data, things will be shifted by an appropriate number of widths. To center on integers, for example, use width=1 and center=0, even if 0 i s outside the range of the data. At most one of center and boundary may be specified. |
| `boundary` | float | `None` | A boundary between two bins. As with center, things are shifted when boundary is outside the range of the data. For example, to center on integers, use width=1 and boundary=0.5, even if 1 is outside the range of the data. At most one of center and boundary may be specified. |
| `closed` | Literal[left, right] | `"right"` | Which edge of the bins is included. |
| `pad` | bool | `False` | If True, adds empty bins at either side of x. This ensures that frequency polygons touch 0. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the geom. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| weight | None |
| y | after_stat('count') |

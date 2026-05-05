# stat_bin_2d

2 Dimensional bin counts

## Signature

`stat_bin_2d( mapping=None, data=None, *, geom="rect", position="identity", na_rm=False, bins=30, breaks=None, binwidth=None, drop=True, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping.  Options for computed aesthetics |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `geom` | str \| geom | `"rect"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"identity"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `bins` | int | `30` | Number of bins. Overridden by binwidth. |
| `breaks` | array_like \| tuple[array_like, array_like] | `None` | Bin boundaries. This supersedes the binwidth, bins, center and boundary. It can be an array_like or a list of two array_likes to provide distinct breaks for the x and y axes. |
| `binwidth` | float | `None` | The width of the bins. The default is to use bins bins that cover the range of the data. You should always override this value, exploring multiple widths to find the best to illustrate the stories in your data. |
| `drop` | bool | `False` | If True, removes all cells with zero counts. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the geom. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y |  |
| fill | after_stat('count') |
| weight | None |

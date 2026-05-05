# stat_sina

Compute Sina plot values

## Signature

`stat_sina( mapping=None, data=None, *, geom="sina", position="dodge", na_rm=False, binwidth=None, bins=None, method="density", bw="nrd0", maxwidth=None, adjust=1, bin_limit=1, random_state=None, scale="area", style="full", **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping.  Options for computed aesthetics Calculated aesthetics are accessed using the after_stat function. e.g. after_stat('quantile'). |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `geom` | str \| geom | `"sina"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"dodge"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `binwidth` | float | `None` | The width of the bins. The default is to use bins that cover the range of the data. You should always override this value, exploring multiple widths to find the best to illustrate the stories in your data. |
| `bins` | int | `50` | Number of bins. Overridden by binwidth. |
| `method` | Literal[density, counts] | `"density"` | Choose the method to spread the samples within the same bin along the x-axis. Available methods: “density”, “counts” (can be abbreviated, e.g. “d”). See Details. |
| `maxwidth` | float | `None` | Control the maximum width the points can spread into. Values should be in the range (0, 1). |
| `adjust` | float | `1` | Adjusts the bandwidth of the density kernel when method="density". see stat_density. |
| `bw` | str \| float | `"nrd0"` | The bandwidth to use, If a float is given, it is the bandwidth. The str choices are: "nrd0", "normal_reference", "scott", "silverman" nrd0 is a port of stats::bw.nrd0 in R; it is eqiuvalent to silverman when there is more than 1 value in a group. |
| `bin_limit` | int | `1` | If the samples within the same y-axis bin are more than bin_limit, the samples’s X coordinates will be adjusted. This parameter is effective only when method="counts" |
| `random_state` | int \| RandomState | `None` | Seed or Random number generator to use. If None, then numpy global generator numpy.random is used. |
| `scale` | Literal[area, count, width] | `"area"` | How to scale the sina groups. |
| `style` |  |  | Type of sina plot to draw. The options are |
| `**kwargs` | Any |  | Aesthetics or parameters used by the geom. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y |  |

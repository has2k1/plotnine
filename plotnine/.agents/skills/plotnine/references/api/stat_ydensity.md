# stat_ydensity

Density estimate

## Signature

`stat_ydensity( mapping=None, data=None, *, geom="violin", position="dodge", na_rm=False, adjust=1, kernel="gaussian", n=1024, trim=True, bw="nrd0", scale="area", **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping.  Options for computed aesthetics Calculated aesthetics are accessed using the after_stat function. e.g. after_stat('width'). |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `geom` | str \| geom | `"violin"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"dodge"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `kernel` | str | `"gaussian"` | Kernel used for density estimation. One of: |
| `adjust` | float | `1` | An adjustment factor for the bw. Bandwidth becomes bw * adjust. Adjustment of the bandwidth. |
| `trim` | bool | `False` | This parameter only matters if you are displaying multiple densities in one plot. If False, the default, each density is computed on the full range of the data. If True, each density is computed over the range of that group; this typically means the estimated x values will not line-up, and hence you won’t be able to stack density values. |
| `n` | int | `1024` | Number of equally spaced points at which the density is to be estimated. For efficient computation, it should be a power of two. |
| `bw` | str \| float | `"nrd0"` | The bandwidth to use, If a float is given, it is the bandwidth. The str choices are: nrd0 is a port of stats::bw.nrd0 in R; it is eqiuvalent to silverman when there is more than 1 value in a group. |
| `scale` | Literal[area, count, width] | `"area"` | How to scale the violins. The options are: If area all violins have the same area, before trimming the tails. If count the areas are scaled proportionally to the number of observations. If width all violins have the same maximum width. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the geom. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y |  |
| weight | None |

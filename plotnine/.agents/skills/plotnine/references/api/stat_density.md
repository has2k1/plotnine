# stat_density

Compute density estimate

## Signature

`stat_density( mapping=None, data=None, *, geom="density", position="stack", na_rm=False, kernel="gaussian", adjust=1, trim=False, n=1024, gridsize=None, bw="nrd0", cut=3, clip=(-inf, inf), bounds=(-inf, inf), **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping.  Options for computed aesthetics |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `geom` | str \| geom | `"density"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"stack"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `kernel` | str | `"gaussian"` | Kernel used for density estimation. One of: |
| `adjust` | float | `1` | An adjustment factor for the bw. Bandwidth becomes bw * adjust. Adjustment of the bandwidth. |
| `trim` | bool | `False` | This parameter only matters if you are displaying multiple densities in one plot. If False, the default, each density is computed on the full range of the data. If True, each density is computed over the range of that group; this typically means the estimated x values will not line-up, and hence you won’t be able to stack density values. |
| `n` | int | `1024` | Number of equally spaced points at which the density is to be estimated. For efficient computation, it should be a power of two. |
| `gridsize` | int | `None` | If gridsize is None, max(len(x), 50) is used. |
| `bw` | str \| float | `"nrd0"` | The bandwidth to use, If a float is given, it is the bandwidth. The options are: nrd0 is a port of stats::bw.nrd0 in R; it is eqiuvalent to silverman when there is more than 1 value in a group. |
| `cut` | float | `3` | Defines the length of the grid past the lowest and highest values of x so that the kernel goes to zero. The end points are -/+ cut*bw*{min(x) or max(x)}. |
| `clip` | tuple[float, float] | `(-inf, inf)` | Values in x that are outside of the range given by clip are dropped. The number of values in x is then shortened. |
| `bounds` |  |  | The domain boundaries of the data. When the domain is finite the estimated density will be corrected to remove asymptotic boundary effects that are usually biased away from the probability density function being estimated. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the geom. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y | after_stat('density') |

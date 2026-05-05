# stat_qq

Calculation for quantile-quantile plot

## Signature

`stat_qq( mapping=None, data=None, *, geom="qq", position="identity", na_rm=False, distribution="norm", dparams={}, quantiles=None, alpha_beta=(0.375, 0.375), **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping.  Options for computed aesthetics |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `geom` | str \| geom | `"qq"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"identity"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `distribution` | str | `"norm"` | Distribution or distribution function name. The default is norm for a normal probability plot. Objects that look enough like a stats.distributions instance (i.e. they have a ppf method) are also accepted. See scipy stats for available distributions. |
| `dparams` | dict | `None` | Distribution-specific shape parameters (shape parameters plus location and scale). |
| `quantiles` | array_like | `None` | Probability points at which to calculate the theoretical quantile values. If provided, must be the same number as as the sample data points. The default is to use calculated theoretical points, use to alpha_beta control how these points are generated. |
| `alpha_beta` | tuple | `(3/8, 3/8)` | Parameter values to use when calculating the quantiles. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the geom. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| sample |  |
| x | after_stat('theoretical') |
| y | after_stat('sample') |

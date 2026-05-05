# stat_quantile

Compute quantile regression lines

## Signature

`stat_quantile( mapping=None, data=None, *, geom="quantile", position="identity", na_rm=False, quantiles=(0.25, 0.5, 0.75), formula="y ~ x", method_args={}, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping.  Options for computed aesthetics Calculated aesthetics are accessed using the after_stat function. e.g. after_stat('quantile'). |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `geom` | str \| geom | `"quantile"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"identity"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `quantiles` | tuple | `(0.25, 0.5, 0.75)` | Quantiles of y to compute |
| `formula` | str | `"y ~ x"` | Formula relating y variables to x variables |
| `method_args` | dict | `None` | Extra arguments passed on to the model fitting method, fit. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the geom. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y |  |

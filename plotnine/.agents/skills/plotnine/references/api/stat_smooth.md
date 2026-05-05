# stat_smooth

Calculate a smoothed conditional mean

## Signature

`stat_smooth( mapping=None, data=None, *, geom="smooth", position="identity", na_rm=False, method="auto", se=True, n=80, formula=None, fullrange=False, level=0.95, span=0.75, method_args={}, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping.  Options for computed aesthetics Calculated aesthetics are accessed using the after_stat function. e.g. after_stat('se'). |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `geom` | str \| geom | `"smooth"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"identity"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `method` | str \| callable | `"auto"` | The available methods are: If a callable is passed, it must have the signature: For loess smoothing you must install the scikit-misc package. You can install it using with pip install scikit-misc or pip install plotnine[all]. |
| `formula` | formula_like | `None` | An object that can be used to construct a patsy design matrix. This is usually a string. You can only use a formula if method is one of lm, ols, wls, glm, rlm or gls, and in the formula you may refer to the x and y aesthetic variables. |
| `se` | bool | `True` | If True draw confidence interval around the smooth line. |
| `n` | int | `80` | Number of points to evaluate the smoother at. Some smoothers like mavg do not support this. |
| `fullrange` | bool | `False` | If True the fit will span the full range of the plot. |
| `level` | float | `0.95` | Level of confidence to use if se=True. |
| `span` | float | `2/3.` | Controls the amount of smoothing for the loess smoother. Larger number means more smoothing. It should be in the (0, 1) range. |
| `method_args` | dict | `{}` | Additional arguments passed on to the modelling method. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the geom. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y |  |

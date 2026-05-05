# stat_function

Superimpose a function onto a plot

## Signature

`stat_function( mapping=None, data=None, *, geom="path", position="identity", na_rm=False, fun=None, n=101, args=None, xlim=None, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping.  Options for computed aesthetics |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `geom` | str \| geom | `"path"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"identity"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `fun` | callable |  | Function to evaluate. |
| `n` | int | `101` | Number of points at which to evaluate the function. |
| `xlim` | tuple | `None` | x limits for the range. The default depends on the x aesthetic. There is not an x aesthetic then the xlim must be provided. |
| `args` | Optional[tuple[Any] \| dict[str, Any]] | `None` | Arguments to pass to fun. |
| `**kwargs` |  |  | Aesthetics or parameters used by the geom. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| y | after_stat('fx') |

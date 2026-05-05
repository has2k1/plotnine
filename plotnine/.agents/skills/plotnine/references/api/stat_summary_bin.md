# stat_summary_bin

Summarise y values at x intervals

## Signature

`stat_summary_bin( mapping=None, data=None, *, geom="pointrange", position="identity", na_rm=False, bins=30, breaks=None, binwidth=None, boundary=None, fun_data=None, fun_y=None, fun_ymin=None, fun_ymax=None, fun_args=None, random_state=None, **kwargs )`

## Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `mapping` | aes | `None` | Aesthetic mappings created with aes. If specified and inherit_aes=True, it is combined with the default mapping for the plot. You must supply mapping if there is no plot mapping.  Options for computed aesthetics Calculated aesthetics are accessed using the after_stat function. e.g. after_stat('ymin'). |
| `data` | DataFrame | `None` | The data to be displayed in this layer. If None, the data from from the ggplot() call is used. If specified, it overrides the data from the ggplot() call. |
| `geom` | str \| geom | `"pointrange"` | The statistical transformation to use on the data for this layer. If it is a string, it must be the registered and known to Plotnine. |
| `position` | str \| position | `"identity"` | Position adjustment. If it is a string, it must be registered and known to Plotnine. |
| `na_rm` | bool | `False` | If False, removes missing values with a warning. If True silently removes missing values. |
| `binwidth` | float \| tuple | `None` | The width of the bins. The default is to use bins bins that cover the range of the data. You should always override this value, exploring multiple widths to find the best to illustrate the stories in your data. |
| `bins` | int \| tuple | `30` | Number of bins. Overridden by binwidth. |
| `breaks` | array_like \| tuple[array_like, array_like] | `None` | Bin boundaries. This supersedes the binwidth, bins and boundary arguments. |
| `boundary` | float \| tuple | `None` | A boundary between two bins. As with center, things are shifted when boundary is outside the range of the data. For example, to center on integers, use width=1 and boundary=0.5, even if 1 is outside the range of the data. At most one of center and boundary may be specified. |
| `fun_data` | str \| callable | `"mean_se"` | If a string, should be one of mean_cl_boot, mean_cl_normal, mean_sdl, median_hilow, mean_se. If a function, it should that takes an array and return a dataframe with three rows indexed as y, ymin and ymax. |
| `fun_y` | callable | `None` | A function that takes an array_like and returns a single value |
| `fun_ymax` | callable | `None` | A function that takes an array_like and returns a single value |
| `fun_args` | dict | `None` | Arguments to any of the functions. Provided the names of the arguments of the different functions are in not conflict, the arguments will be assigned to the right functions. If there is a conflict, create a wrapper function that resolves the ambiguity in the argument names. |
| `random_state` | int \| RandomState | `None` | Seed or Random number generator to use. If None, then numpy global generator numpy.random is used. |
| `**kwargs` | Any |  | Aesthetics or parameters used by the geom. |

### Aesthetics

| Aesthetic | Default value |
|---|---|
| x |  |
| y |  |

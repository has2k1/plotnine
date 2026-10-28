from warnings import warn

import numpy as np

from .._utils import frame
from ..doctools import document
from ..exceptions import PlotnineWarning
from .stat import stat


# method_args are any of the keyword args (other than q) for
# statsmodels.regression.quantile_regression.QuantReg.fit
@document
class stat_quantile(stat):
    """
    Compute quantile regression lines

    {usage}

    Parameters
    ----------
    {common_parameters}
    quantiles : tuple, default=(0.25, 0.5, 0.75)
        Quantiles of y to compute
    formula : str, default="y ~ x"
        Formula relating y variables to x variables
    method_args : dict, default=None
        Extra arguments passed on to the model fitting method,
        [](`~statsmodels.regression.quantile_regression.QuantReg.fit`).

    See Also
    --------
    plotnine.geom_quantile : The default `geom` for this `stat`.
    statsmodels.regression.quantile_regression.QuantReg
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Options for computed aesthetics**

    ```python
    "quantile"  # quantile
    "group"     # group identifier
    ```

    Calculated aesthetics are accessed using the `after_stat` function.
    e.g. `after_stat('quantile')`{.py}.
    """

    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {
        "geom": "quantile",
        "quantiles": (0.25, 0.5, 0.75),
        "formula": "y ~ x",
        "method_args": {},
    }
    CREATES = {"quantile", "group"}
    DROPPED_AES = ["weight"]

    def setup_params(self, data):
        params = self.params
        if params["formula"] is None:
            params["formula"] = "y ~ x"
            warn("Formula not specified, using '{}'", PlotnineWarning)
        else:
            params["eval_env"] = self.environment.to_patsy_env()

        try:
            iter(params["quantiles"])
        except TypeError:
            params["quantiles"] = (params["quantiles"],)

    def compute_group(self, data, scales):
        res = [
            quant_pred(q, data, self.params) for q in self.params["quantiles"]
        ]
        return frame.concat(res)


def quant_pred(q, data, params):
    """
    Quantile precitions
    """
    import statsmodels.formula.api as smf

    # statsmodels formulas can work with a dict of arrays, so the
    # data does not have to be in a pandas dataframe.
    values = {c: frame.to_numpy(data[c]) for c in data.columns}
    mod = smf.quantreg(
        params["formula"],
        values,
        eval_env=params.get("eval_env"),
    )
    reg_res = mod.fit(q=q, **params["method_args"])
    x = np.array([values["x"].min(), values["x"].max()])
    return frame.frame_like(
        data,
        {
            "x": x,
            "quantile": q,
            "group": f"{data['group'].item(0)}-{q}",
            "y": np.asarray(reg_res.predict({"x": x})),
        },
    )
